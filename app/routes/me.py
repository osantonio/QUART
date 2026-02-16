# app/routes/me.py

from quart import Blueprint, render_template, request, redirect, url_for, session, flash
from app.config import get_session, config
from app.utils.auth import permission_required
from app.models import Usuario
from sqlmodel import select
import jwt
import os
import uuid
from datetime import datetime

me_bp = Blueprint("me", __name__, url_prefix="/me")

async def get_current_user_id():
    """Helper para obtener el ID del usuario actual desde el token JWT en la sesión."""
    token = session.get("token")
    if not token:
        return None
    try:
        # Decodificar el token para obtener el 'sub' (usuario_id)
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        return int(payload["sub"])
    except Exception:
        return None

@me_bp.route("/")
@permission_required
async def perfil():
    """Muestra el perfil del usuario autenticado."""
    user_id = await get_current_user_id()
    if not user_id:
        return redirect(url_for("auth.login"))
        
    async for db_session in get_session():
        statement = select(Usuario).where(Usuario.id == user_id)
        result = await db_session.execute(statement)
        usuario = result.scalar_one_or_none()
        
        if not usuario:
            # Si el token es válido pero el usuario no existe, limpiar sesión
            session.clear()
            return redirect(url_for("auth.login"))
            
        # Calcular edad
        edad = None
        if usuario.fecha_nacimiento:
            try:
                fecha_nac = datetime.strptime(usuario.fecha_nacimiento, "%Y-%m-%d")
                hoy = datetime.now()
                edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
            except:
                pass
                
        return await render_template(
            "me/perfil.html", 
            usuario=usuario, 
            edad=edad,
            is_own_profile=True
        )

@me_bp.route("/editar", methods=["GET", "POST"])
@permission_required
async def editar():
    """Formulario para editar el propio perfil."""
    user_id = await get_current_user_id()
    if not user_id:
        return redirect(url_for("auth.login"))
        
    async for db_session in get_session():
        statement = select(Usuario).where(Usuario.id == user_id)
        result = await db_session.execute(statement)
        usuario = result.scalar_one_or_none()
        
        if not usuario:
            session.clear()
            return redirect(url_for("auth.login"))
            
        if request.method == "POST":
            form = await request.form
            files = await request.files
            
            # Actualizar campos permitidos
            usuario.nombres = form.get("nombres")
            usuario.apellidos = form.get("apellidos")
            usuario.telefono = form.get("telefono")
            usuario.fecha_nacimiento = form.get("fecha_nacimiento")
            usuario.genero = form.get("genero")
            
            # Manejar carga de foto de perfil
            foto = files.get("foto_perfil")
            if foto and foto.filename:
                # Validar extensión (opcional pero recomendado)
                ext = os.path.splitext(foto.filename)[1].lower()
                if ext in ['.jpg', '.jpeg', '.png', '.gif']:
                    # Generar nombre único para el archivo
                    nuevo_nombre = f"{uuid.uuid4()}{ext}"
                    upload_path = os.path.join("app", "static", "uploads", "profile_pics", nuevo_nombre)
                    
                    # Asegurar que el directorio existe (doble check)
                    os.makedirs(os.path.dirname(upload_path), exist_ok=True)
                    
                    # Guardar el archivo
                    await foto.save(upload_path)
                    
                    # Eliminar foto anterior si existe y no es la predeterminada
                    if usuario.foto_perfil:
                        old_path = os.path.join("app", "static", "uploads", "profile_pics", usuario.foto_perfil)
                        if os.path.exists(old_path):
                            try:
                                os.remove(old_path)
                            except:
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
    """Formulario para cambiar la contraseña."""
    user_id = await get_current_user_id()
    if not user_id:
        return redirect(url_for("auth.login"))
        
    async for db_session in get_session():
        statement = select(Usuario).where(Usuario.id == user_id)
        result = await db_session.execute(statement)
        usuario = result.scalar_one_or_none()
        
        if not usuario:
            session.clear()
            return redirect(url_for("auth.login"))
            
        if request.method == "POST":
            form = await request.form
            current_password = form.get("current_password")
            new_password = form.get("new_password")
            confirm_password = form.get("confirm_password")
            
            # Validaciones
            if not usuario.verify_password(current_password):
                await flash("La contraseña actual es incorrecta", "danger")
                return await render_template("me/password.html", usuario=usuario)
                
            if new_password != confirm_password:
                await flash("La nueva contraseña y la confirmación no coinciden", "danger")
                return await render_template("me/password.html", usuario=usuario)
                
            if len(new_password) < 6:
                await flash("La nueva contraseña debe tener al menos 6 caracteres", "danger")
                return await render_template("me/password.html", usuario=usuario)
            
            # Actualizar contraseña
            usuario.set_password(new_password)
            db_session.add(usuario)
            await db_session.commit()
            
            await flash("¡Contraseña actualizada con éxito!", "success")
            return redirect(url_for("me.perfil"))
            
        return await render_template("me/password.html", usuario=usuario)
