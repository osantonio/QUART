# app/routes/configuracion.py

from quart import Blueprint, flash, redirect, render_template, request, session, url_for
from sqlalchemy import func, select

from app.config.database import AsyncSessionLocal
from app.models.usuario import Usuario
from app.services.configuracion_service import crear_admin

configuracion_bp = Blueprint("configuracion", __name__, url_prefix="/configuracion")


async def _hay_usuarios() -> bool:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(func.count()).select_from(Usuario))
        return (result.scalar() or 0) > 0


@configuracion_bp.route("/", methods=["GET", "POST"])
async def index():
    if await _hay_usuarios():
        await flash("El sistema ya fue configurado.", "info")
        return redirect(url_for("main.index"))

    if request.method == "GET":
        return await render_template("configuracion/index.html")

    form = await request.form
    nombres = form.get("nombres", "").strip().title()
    apellidos = form.get("apellidos", "").strip().title()
    username = form.get("username", "").strip().lower()
    email = form.get("email", "").strip().lower()
    password = form.get("password", "").strip()
    confirm = form.get("confirm_password", "").strip()

    if not nombres:
        await flash("El nombre es obligatorio.", "error")
        return redirect(url_for("configuracion.index"))

    if not username:
        await flash("El nombre de usuario es obligatorio.", "error")
        return redirect(url_for("configuracion.index"))

    if not email or "@" not in email:
        await flash("Ingresa un correo electrónico válido.", "error")
        return redirect(url_for("configuracion.index"))

    if len(password) < 8:
        await flash("La contraseña debe tener al menos 8 caracteres.", "error")
        return redirect(url_for("configuracion.index"))

    if password != confirm:
        await flash("Las contraseñas no coinciden.", "error")
        return redirect(url_for("configuracion.index"))

    async with AsyncSessionLocal() as db:
        usuario = await crear_admin(
            db,
            username=username,
            email=email,
            password=password,
            nombres=nombres,
            apellidos=apellidos,
        )
        await db.commit()
        await db.refresh(usuario)

    session.clear()
    session["user_id"] = usuario.id
    session["username"] = usuario.username

    await flash(f"¡Configuración completada! Bienvenido, {usuario.nombres}.", "success")
    return redirect(url_for("main.dashboard"))
