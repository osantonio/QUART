from app.models.usuario import Usuario
from app.config.database import AsyncSessionLocal
from app.utils.exceptions import ValidationError
from sqlmodel import select
from sqlalchemy import or_
from typing import Dict, Any

class AuthService:
    @staticmethod
    async def registrar_usuario(datos: Dict[Any, Any]) -> Usuario:
        """
        Lógica de negocio para registrar un nuevo usuario.
        Valida datos, verifica duplicados y persiste en la base de datos.
        """
        identificacion = datos.get("identificacion")
        nombres = datos.get("nombres")
        apellidos = datos.get("apellidos")
        username = datos.get("username")
        email = datos.get("email")
        password = datos.get("password")
        confirm_password = datos.get("confirm_password")
        telefono = datos.get("telefono")
        fecha_nacimiento = datos.get("fecha_nacimiento")
        genero = datos.get("genero")
        tipo_sangre = datos.get("tipo_sangre")

        # 1. Validaciones básicas
        if not all([identificacion, nombres, apellidos, username, email, password, confirm_password]):
            raise ValidationError("Todos los campos marcados con * son obligatorios")

        if password != confirm_password:
            raise ValidationError("Las contraseñas no coinciden")

        if len(password) < 6:
            raise ValidationError("La contraseña debe tener al menos 6 caracteres")

        async with AsyncSessionLocal() as db_session:
            # 2. Verificar duplicados (Email)
            email_stmt = select(Usuario).where(Usuario.email == email)
            email_result = await db_session.execute(email_stmt)
            if email_result.scalar_one_or_none():
                raise ValidationError("Este email ya está registrado")

            # 3. Verificar duplicados (Username)
            username_stmt = select(Usuario).where(Usuario.username == username)
            username_result = await db_session.execute(username_stmt)
            if username_result.scalar_one_or_none():
                raise ValidationError("Este nombre de usuario ya existe")

            # 4. Crear y guardar usuario
            nuevo_usuario = Usuario(
                identificacion=int(identificacion),
                nombres=nombres,
                apellidos=apellidos,
                username=username,
                email=email,
                telefono=telefono,
                fecha_nacimiento=fecha_nacimiento,
                genero=genero,
                tipo_sangre=tipo_sangre
            )
            nuevo_usuario.set_password(password)

            db_session.add(nuevo_usuario)
            await db_session.commit()
            await db_session.refresh(nuevo_usuario)
            
            return nuevo_usuario

    @staticmethod
    async def login(login_value: str, password: str) -> Usuario:
        """
        Lógica de negocio para autenticar a un usuario.
        Busca por email, username o identificación y verifica password.
        """
        if not login_value or not password:
            raise ValidationError("Debe proporcionar sus credenciales")

        async with AsyncSessionLocal() as db_session:
            identificacion_int = None
            if login_value.isdigit():
                try:
                    identificacion_int = int(login_value)
                except ValueError:
                    identificacion_int = None

            conditions = [
                Usuario.email == login_value,
                Usuario.username == login_value,
            ]
            if identificacion_int is not None:
                conditions.append(Usuario.identificacion == identificacion_int)

            statement = select(Usuario).where(or_(*conditions))
            result = await db_session.execute(statement)
            usuario = result.scalar_one_or_none()

            if usuario and usuario.verify_password(password):
                return usuario
            
            raise ValidationError("Datos de acceso o contraseña incorrectos")
