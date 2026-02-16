# app/routes/auth.py

from quart import Blueprint, render_template, request, redirect, url_for, session, flash
from app.utils.exceptions import ValidationError
from app.services import AuthService
from app.config import generate_token

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login", methods=["GET", "POST"])
async def login():
    if request.method == "POST":
        form = await request.form
        login_value = form.get("login")
        password = form.get("password")

        try:
            usuario = await AuthService.login(login_value, password)
            token = generate_token(usuario.id)
            session["token"] = token
            session["user_id"] = usuario.id
            session["username"] = usuario.username
            session["foto_perfil"] = usuario.foto_perfil
            await flash("Inicio de sesión exitoso", "success")
            return redirect(url_for("main.index"))
        except ValidationError as e:
            await flash(str(e), "danger")
            return redirect(url_for("auth.login"))
        except Exception:
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
    # Limpiar la sesión
    session.clear()
    await flash("Sesión cerrada exitosamente", "success")
    return redirect(url_for("auth.login"))
