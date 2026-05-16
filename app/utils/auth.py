# app/utils/auth.py

from functools import wraps
from quart import session, redirect, url_for, flash, request, g
from app.config.database import AsyncSessionLocal
from app.models.usuario import Usuario
from app.models.roles import Rol, Permiso
from sqlmodel import select
from sqlalchemy.orm import selectinload


async def get_current_user() -> Usuario | None:
    """Obtiene el usuario actual desde session["user_id"] (cacheado en g por request)."""
    if hasattr(g, "current_user"):
        return g.current_user

    user_id = session.get("user_id")
    if not user_id:
        g.current_user = None
        return None

    try:
        async with AsyncSessionLocal() as db:
            stmt = (
                select(Usuario)
                .where(Usuario.id == int(user_id))
                .options(selectinload(Usuario.roles))
            )
            result = await db.execute(stmt)
            g.current_user = result.scalar_one_or_none()
    except (ValueError, Exception):
        g.current_user = None

    return g.current_user


def permission_required(f):
    """Decorador: redirige a login si no autenticado; bloquea si sin permiso."""
    @wraps(f)
    async def decorated(*args, **kwargs):
        usuario = await get_current_user()

        if not usuario:
            return redirect(url_for("auth.login"))

        is_admin = any(rol.name.lower() == "administrador" for rol in usuario.roles)
        if is_admin:
            return await f(*args, **kwargs)

        endpoint = request.endpoint
        if await has_permission(endpoint):
            return await f(*args, **kwargs)

        await flash("No tienes permisos suficientes para acceder a esta ruta.", "danger")
        return redirect(url_for("main.index"))

    return decorated


async def has_permission(endpoint: str) -> bool:
    """Verifica si el usuario actual tiene permiso para el endpoint dado (cacheado por request)."""
    if hasattr(g, "user_permissions") and endpoint in g.user_permissions:
        return True

    usuario = await get_current_user()
    if not usuario:
        return False

    if any(rol.name.lower() == "administrador" for rol in usuario.roles):
        return True

    if not hasattr(g, "user_permissions"):
        try:
            async with AsyncSessionLocal() as db:
                role_ids = [rol.id for rol in usuario.roles]
                if not role_ids:
                    g.user_permissions = set()
                else:
                    stmt = (
                        select(Permiso.slug)
                        .join(Permiso.roles)
                        .where(Rol.id.in_(role_ids))
                    )
                    result = await db.execute(stmt)
                    g.user_permissions = set(result.scalars().all())
        except Exception:
            g.user_permissions = set()

    return endpoint in g.user_permissions


async def es_admin() -> bool:
    usuario = await get_current_user()
    if not usuario:
        return False
    return any(rol.name.lower() == "administrador" for rol in usuario.roles)


async def tiene_rol(nombre_rol: str) -> bool:
    usuario = await get_current_user()
    if not usuario:
        return False
    return any(rol.name.lower() == nombre_rol.lower() for rol in usuario.roles)


async def tiene_acceso(*requisitos: str) -> bool:
    """True si el usuario cumple AL MENOS UNO de los requisitos (permiso o rol)."""
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
