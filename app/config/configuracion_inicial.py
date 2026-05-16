# app/config/configuracion_inicial.py

import logging

from sqlmodel import select

from app.models.roles import Permiso, Rol, RolPermiso

logger = logging.getLogger(__name__)


async def configuracion_inicial(engine):
    """Siembra roles y permisos base si no existen. El usuario admin se crea via /configuracion."""
    from app.config.database import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        roles_result = await session.execute(select(Rol))
        if not roles_result.first():
            logger.info("Creando roles iniciales")
            admin_role = Rol(name="administrador", description="Acceso total al sistema")
            general_role = Rol(name="general", description="Acceso restringido de lectura")
            session.add_all([admin_role, general_role])
            await session.flush()

            perms_result = await session.execute(select(Permiso))
            if not perms_result.first():
                p_perfil = Permiso(slug="me.perfil", module="perfil", description="Ver propio perfil")
                p_listar = Permiso(slug="usuarios.listar", module="usuarios", description="Ver lista de usuarios")
                session.add_all([p_perfil, p_listar])
                await session.flush()

                session.add(RolPermiso(rol_id=general_role.id, permiso_id=p_perfil.id))
                session.add(RolPermiso(rol_id=general_role.id, permiso_id=p_listar.id))

            await session.commit()
            logger.info("Roles y permisos base creados")
