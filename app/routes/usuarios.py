# app/routes/usuarios.py

from quart import Blueprint, render_template, request, redirect, url_for, session, flash
from app.config import get_session
from app.utils.auth import permission_required, es_admin
from app.models import Usuario
from sqlmodel import select
import os
import uuid

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")

@usuarios_bp.route("/")
@permission_required
async def listar():
    """
    Ruta para listar todos los usuarios registrados en el sistema.
    Requiere autenticación mediante token.
    """
    async for db_session in get_session():
        # Consultar todos los usuarios ordenados por ID
        statement = select(Usuario).order_by(Usuario.id)
        result = await db_session.execute(statement)
        usuarios = result.scalars().all()
        
        return await render_template(
            "usuarios/listar.html",
            usuarios=usuarios
        )

@usuarios_bp.route("/<int:usuario_id>")
@permission_required
async def perfil(usuario_id):
    """
    Ruta para ver el perfil individual de un usuario.
    Muestra información detallada tipo red social.
    """
    async for db_session in get_session():
        # Consultar el usuario por ID
        statement = select(Usuario).where(Usuario.id == usuario_id)
        result = await db_session.execute(statement)
        usuario = result.scalar_one_or_none()
        
        if not usuario:
            await flash("Usuario no encontrado", "danger")
            return redirect(url_for("usuarios.listar"))
        
        # Calcular edad si tiene fecha de nacimiento
        edad = None
        if usuario.fecha_nacimiento:
            from datetime import datetime
            try:
                fecha_nac = datetime.strptime(usuario.fecha_nacimiento, "%Y-%m-%d")
                hoy = datetime.now()
                edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
            except:
                pass
        
        return await render_template(
            "usuarios/perfil.html",
            usuario=usuario,
            edad=edad
        )

@usuarios_bp.route("/editar/<int:usuario_id>", methods=["GET", "POST"])
@permission_required
async def editar(usuario_id):
    if not await es_admin():
        await flash("Acceso restringido a administradores.", "danger")
        return redirect(url_for("usuarios.perfil", usuario_id=usuario_id))
    
    async for db_session in get_session():
        statement = select(Usuario).where(Usuario.id == usuario_id)
        result = await db_session.execute(statement)
        usuario = result.scalar_one_or_none()
        
        if not usuario:
            await flash("Usuario no encontrado", "danger")
            return redirect(url_for("usuarios.listar"))
        
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
                if ext in ['.jpg', '.jpeg', '.png', '.gif']:
                    nuevo_nombre = f"{uuid.uuid4()}{ext}"
                    upload_path = os.path.join("app", "static", "uploads", "profile_pics", nuevo_nombre)
                    os.makedirs(os.path.dirname(upload_path), exist_ok=True)
                    await foto.save(upload_path)
                    if usuario.foto_perfil:
                        old_path = os.path.join("app", "static", "uploads", "profile_pics", usuario.foto_perfil)
                        if os.path.exists(old_path):
                            try:
                                os.remove(old_path)
                            except:
                                pass
                    usuario.foto_perfil = nuevo_nombre
            
            db_session.add(usuario)
            await db_session.commit()
            await db_session.refresh(usuario)
            
            await flash("Perfil del usuario actualizado correctamente.", "success")
            return redirect(url_for("usuarios.perfil", usuario_id=usuario_id))
        
        return await render_template("usuarios/editar.html", usuario=usuario)

