# app/routes/auth.py

from quart import Blueprint, render_template, request, redirect, url_for, session, flash
from app.utils.exceptions import ValidationError
from app.utils.rate_limit import login_bloqueado, registrar_intento
from app.utils.red import extraer_ip
from app.services import AuthService
from app.config.database import AsyncSessionLocal

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
async def login():
    if request.method == "POST":
        form = await request.form
        login_value = form.get("login", "").strip()
        password = form.get("password", "").strip()
        ip = extraer_ip(request)

        async with AsyncSessionLocal() as db:
            bloqueado, restante = await login_bloqueado(db, ip, login_value)
            if bloqueado:
                minutos = max(1, restante // 60)
                await flash(
                    f"Demasiados intentos fallidos. Intenta de nuevo en ~{minutos} min.",
                    "danger",
                )
                return redirect(url_for("auth.login"))

            try:
                usuario = await AuthService.login(login_value, password)
                session.clear()
                session["user_id"] = usuario.id
                session["username"] = usuario.username
                session["foto_perfil"] = usuario.foto_perfil
                await flash("Inicio de sesión exitoso", "success")
                return redirect(url_for("main.index"))
            except ValidationError as e:
                await registrar_intento(db, ip, login_value)
                await db.commit()
                await flash(str(e), "danger")
                return redirect(url_for("auth.login"))
            except Exception:
                await registrar_intento(db, ip, login_value)
                await db.commit()
                await flash("Ocurrió un error inesperado durante el inicio de sesión", "danger")
                return redirect(url_for("auth.login"))

    return await render_template("auth/login.html")


@auth_bp.route("/registro", methods=["GET", "POST"])
async def registro():
    if request.method == "POST":
        form = await request.form
        try:
            await AuthService.registrar_usuario(form)
            await flash("Cuenta creada exitosamente. Por favor inicia sesión.", "success")
            return redirect(url_for("auth.login"))
        except ValidationError as e:
            await flash(str(e), "danger")
            return redirect(url_for("auth.registro"))
        except Exception:
            await flash("Ocurrió un error inesperado durante el registro", "danger")
            return redirect(url_for("auth.registro"))

    return await render_template("auth/registro.html")


@auth_bp.route("/logout")
async def logout():
    session.clear()
    await flash("Sesión cerrada exitosamente", "success")
    return redirect(url_for("auth.login"))
