# app/models/__init__.py

from app.models.usuario import Usuario
from app.models.roles import Rol, Permiso, RolUsuario, RolPermiso

models = [
    Usuario,
    Rol,
    Permiso,
    RolUsuario,
    RolPermiso
    ]