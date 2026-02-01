# app/config/configuracion_inicial.py

from app.models.roles import Rol, Permiso, RolPermiso, RolUsuario
from app.models.usuario import Usuario
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import AsyncSessionLocal

async def configuracion_inicial(engine):
    """Inicializa datos maestros (Roles y Usuario Admin) si la base de datos está vacía."""
    
    async with AsyncSessionLocal() as session:
        # 1. Configuración de Roles
        roles_stmt = select(Rol)
        result = await session.execute(roles_stmt)
        if not result.first():
            print("--- Creando roles iniciales ---")
            admin_role = Rol(name="administrador", description="Acceso total al sistema")
            general_role = Rol(name="general", description="Acceso restringido de lectura")
            
            session.add_all([admin_role, general_role])
            await session.commit()
            print("--- Roles 'administrador' y 'general' creados ---")
        else:
            # Obtener el rol administrador para asignaciones posteriores
            admin_role = (await session.execute(select(Rol).where(Rol.name == "administrador"))).scalar_one_or_none()

        # 2. Configuración de Usuario Administrador (ID 1)
        user_stmt = select(Usuario).where(Usuario.id == 1)
        user_result = await session.execute(user_stmt)
        admin_user = user_result.scalar_one_or_none()

        if not admin_user:
            print("--- Creando usuario administrador inicial (admin:admin) ---")
            admin_user = Usuario(
                id=1,
                username="admin",
                email="admin@system.local",
                nombres="Administrador",
                apellidos="Sistema",
                identificacion=1000
            )
            admin_user.set_password("admin")
            session.add(admin_user)
            await session.commit()
            print("--- Usuario admin creado con ID 1 ---")

        # 3. Asignar rol administrador si no lo tiene
        if admin_role and admin_user:
            check_rel = select(RolUsuario).where(
                RolUsuario.usuario_id == admin_user.id, 
                RolUsuario.role_id == admin_role.id
            )
            rel_exists = (await session.execute(check_rel)).first()
            
            if not rel_exists:
                print(f"--- Asignando rol '{admin_role.name}' al usuario '{admin_user.username}' ---")
                new_rel = RolUsuario(usuario_id=admin_user.id, role_id=admin_role.id)
                session.add(new_rel)
                await session.commit()
                print("--- Rol asignado exitosamente ---")

        # 4. Rutas Iniciales para rol General (Solo GET de ejemplo)
        # Nota: administrador no necesita estas rutas por el bypass
        perms_stmt = select(Permiso)
        perms_result = await session.execute(perms_stmt)
        if not perms_result.first():
            print("--- Creando rutas base ---")
            p_perfil = Permiso(slug="me.perfil", module="perfil", description="Ver propio perfil")
            p_listar = Permiso(slug="usuarios.listar", module="usuarios", description="Ver lista de usuarios")
            
            session.add_all([p_perfil, p_listar])
            await session.commit()
            
            # Asignar al rol general
            general_role = (await session.execute(select(Rol).where(Rol.name == "general"))).scalar_one_or_none()
            if general_role:
                session.add(RolPermiso(rol_id=general_role.id, permiso_id=p_perfil.id))
                session.add(RolPermiso(rol_id=general_role.id, permiso_id=p_listar.id))
                await session.commit()
            print("--- Rutas base asignadas al rol 'general' ---")
