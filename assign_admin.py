# assign_admin.py
import asyncio
from app.config.database import engine
from app.models.roles import Rol, RolUsuario, RolPermiso
from app.models.usuario import Usuario
from sqlmodel import select

async def assign():
    async with engine.begin() as conn:
        print("Intentando asignar rol 'administrator' al usuario ID 1...")
    
    # Usamos una sesión para buscar por nombre
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import sessionmaker
    
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # 1. Buscar el rol administrator
            role_stmt = select(Rol).where(Rol.name == "administrator")
            role_result = await session.execute(role_stmt)
            admin_role = role_result.scalar_one_or_none()
            
            if not admin_role:
                print("Error: El rol 'administrator' no existe. Ejecuta primero la inicialización de la DB.")
                return

            # 2. Verificar que el usuario 1 exista
            user_stmt = select(Usuario).where(Usuario.id == 1)
            user_result = await session.execute(user_stmt)
            user = user_result.scalar_one_or_none()
            
            if not user:
                print("Error: El usuario con ID 1 no existe.")
                return

            # 3. Asignar el rol si no lo tiene
            check_stmt = select(RolUsuario).where(RolUsuario.usuario_id == 1, RolUsuario.role_id == admin_role.id)
            check_result = await session.execute(check_stmt)
            if check_result.first():
                print(f"El usuario '{user.username}' ya tiene el rol '{admin_role.name}'.")
                return

            new_rel = RolUsuario(usuario_id=1, role_id=admin_role.id)
            session.add(new_rel)
            await session.commit()
            print(f"¡Éxito! El usuario '{user.username}' ahora es '{admin_role.name}'.")
            
        except Exception as e:
            print(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    asyncio.run(assign())
