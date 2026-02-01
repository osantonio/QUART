# app/utils/auth.py

from functools import wraps
from quart import session, redirect, url_for, flash, request, g
import jwt
from app.config.config import config
from app.config.database import get_session
from app.models.usuario import Usuario
from app.models.roles import Rol, Permiso
from sqlmodel import select
from sqlalchemy.orm import selectinload

async def get_current_user():
    """Obtiene el objeto Usuario actual desde la sesión con sus roles (cacheado por solicitud)."""
    # 1. Verificar caché de la petición
    if hasattr(g, "current_user"):
        return g.current_user

    token = session.get("token")
    if not token:
        g.current_user = None
        return None
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        user_id = int(payload["sub"])
        
        async for db_session in get_session():
            statement = select(Usuario).where(Usuario.id == user_id).options(selectinload(Usuario.roles))
            result = await db_session.execute(statement)
            user = result.scalar_one_or_none()
            g.current_user = user
            return user
    except Exception:
        g.current_user = None
        return None

def permission_required(f):
    """
    Decorador para proteger rutas basado en la ruta (endpoint) actual.
    El administrador tiene acceso total.
    """
    @wraps(f)
    async def decorated(*args, **kwargs):
        usuario = await get_current_user()
        
        if not usuario:
            return redirect(url_for("auth.login"))
        
        # 1. El perfil administrador tiene acceso a todos las rutas.
        is_admin = any(rol.name.lower() == "administrador" for rol in usuario.roles)
        if is_admin:
            return await f(*args, **kwargs)
        
        # 2. Verificar si el endpoint actual está asignado a alguno de los roles del usuario
        endpoint = request.endpoint
        
        if await has_permission(endpoint):
            return await f(*args, **kwargs)
        
        await flash("No tienes permisos suficientes para acceder a esta ruta.", "danger")
        return redirect(url_for("main.index"))
    return decorated

async def has_permission(endpoint: str) -> bool:
    """ Verifica si el usuario actual tiene permiso para el endpoint dado (cacheado por solicitud). """
    # 1. Verificar caché de permisos en la petición
    if hasattr(g, "user_permissions") and endpoint in g.user_permissions:
        return True

    usuario = await get_current_user()
    if not usuario:
        return False
    
    # 2. Administrador tiene acceso total
    if any(rol.name.lower() == "administrador" for rol in usuario.roles):
        return True
        
    # 3. Cargar todos los permisos del usuario si no están en caché
    if not hasattr(g, "user_permissions"):
        async for db_session in get_session():
            role_ids = [rol.id for rol in usuario.roles]
            if not role_ids:
                g.user_permissions = set()
                break
                
            statement = (
                select(Permiso.slug)
                .join(Permiso.roles)
                .where(Rol.id.in_(role_ids))
            )
            result = await db_session.execute(statement)
            g.user_permissions = set(result.scalars().all())
            break
            
    return endpoint in g.user_permissions

async def es_admin() -> bool:
    """Verifica si el usuario actual tiene el rol de administrador."""
    usuario = await get_current_user()
    if not usuario:
        return False
    return any(rol.name.lower() == "administrador" for rol in usuario.roles)

async def tiene_rol(nombre_rol: str) -> bool:
    """Verifica si el usuario actual tiene un rol específico."""
    usuario = await get_current_user()
    if not usuario:
        return False
    return any(rol.name.lower() == nombre_rol.lower() for rol in usuario.roles)

async def tiene_acceso(*requisitos: str) -> bool:
    """
    Generaliza el acceso:
    - Si un requisito tiene un '.', se comprueba como permiso de endpoint/ruta.
    - Si no, se comprueba como nombre de rol.
    - El administrador tiene acceso total.
    - Retorna True si cumple CON AL MENOS UNO de los requisitos.
    """
    if await es_admin():
        return True
    
    for req in requisitos:
        if "." in req:
            if await has_permission(req):
                return True
        else:
            if await tiene_rol(req):
                return True
                
    return False
