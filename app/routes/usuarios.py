# app/routes/usuarios.py

from quart import Blueprint, render_template, request, redirect, url_for, session, flash
from app.config import get_session
from app.utils.auth import permission_required
from app.models import Usuario
from sqlmodel import select

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

