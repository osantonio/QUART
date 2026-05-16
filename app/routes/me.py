# app/routes/me.py

import os
import uuid
from datetime import datetime

from quart import Blueprint, flash, redirect, render_template, request, session, url_for

from app.config import get_session
from app.models import Usuario
from app.utils.auth import permission_required
from sqlmodel import select

me_bp = Blueprint("me", __name__, url_prefix="/me")


@me_bp.route("/")
@permission_required
async def perfil():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    async for db_session in get_session():
        usuario = (await db_session.execute(
            select(Usuario).where(Usuario.id == int(user_id))
        )).scalar_one_or_none()

        if not usuario:
            session.clear()
            return redirect(url_for("auth.login"))

        edad = None
        if usuario.fecha_nacimiento:
            try:
                fecha_nac = datetime.strptime(usuario.fecha_nacimiento, "%Y-%m-%d")
                hoy = datetime.now()
                edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
            except ValueError:
                pass

        return await render_template("me/perfil.html", usuario=usuario, edad=edad, is_own_profile=True)


@me_bp.route("/editar", methods=["GET", "POST"])
@permission_required
async def editar():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    async for db_session in get_session():
        usuario = (await db_session.execute(
            select(Usuario).where(Usuario.id == int(user_id))
        )).scalar_one_or_none()

        if not usuario:
            session.clear()
            return redirect(url_for("auth.login"))

        if request.method == "POST":
            form = await request.form
            files = await request.files

            usuario.nombres = form.get("nombres")
            usuario.apellidos = form.get("apellidos")
            usuario.telefono = form.get("telefono")
            usuario.fecha_nacimiento = form.get("fecha_nacimiento")
            usuario.genero = form.get("genero")

            foto = files.get("foto_perfil")
            if foto and foto.filename:
                ext = os.path.splitext(foto.filename)[1].lower()
                if ext in (".jpg", ".jpeg", ".png", ".gif"):
                    nuevo_nombre = f"{uuid.uuid4()}{ext}"
                    upload_path = os.path.join("app", "static", "uploads", "profile_pics", nuevo_nombre)
                    os.makedirs(os.path.dirname(upload_path), exist_ok=True)
                    await foto.save(upload_path)

                    if usuario.foto_perfil:
                        old_path = os.path.join("app", "static", "uploads", "profile_pics", usuario.foto_perfil)
                        if os.path.exists(old_path):
                            try:
                                os.remove(old_path)
                            except OSError:
                                pass

                    usuario.foto_perfil = nuevo_nombre
                    session["foto_perfil"] = nuevo_nombre

            db_session.add(usuario)
            await db_session.commit()
            await db_session.refresh(usuario)

            await flash("¡Perfil actualizado con éxito!", "success")
            return redirect(url_for("me.perfil"))

        return await render_template("me/editar.html", usuario=usuario)


@me_bp.route("/password", methods=["GET", "POST"])
@permission_required
async def password():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    async for db_session in get_session():
        usuario = (await db_session.execute(
            select(Usuario).where(Usuario.id == int(user_id))
        )).scalar_one_or_none()

        if not usuario:
            session.clear()
            return redirect(url_for("auth.login"))

        if request.method == "POST":
            form = await request.form
            current_password = form.get("current_password")
            new_password = form.get("new_password")
            confirm_password = form.get("confirm_password")

            if not usuario.verify_password(current_password):
                await flash("La contraseña actual es incorrecta", "danger")
                return await render_template("me/password.html", usuario=usuario)

            if new_password != confirm_password:
                await flash("La nueva contraseña y la confirmación no coinciden", "danger")
                return await render_template("me/password.html", usuario=usuario)

            if len(new_password) < 6:
                await flash("La nueva contraseña debe tener al menos 6 caracteres", "danger")
                return await render_template("me/password.html", usuario=usuario)

            usuario.set_password(new_password)
            db_session.add(usuario)
            await db_session.commit()

            await flash("¡Contraseña actualizada con éxito!", "success")
            return redirect(url_for("me.perfil"))

        return await render_template("me/password.html", usuario=usuario)
