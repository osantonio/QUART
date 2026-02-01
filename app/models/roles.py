# app/models/rbac.py

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class RolUsuario(SQLModel, table=True):
    """Tabla intermedia para asignar múltiples roles a usuarios."""
    usuario_id: int = Field(foreign_key="usuario.id", primary_key=True)
    role_id: int = Field(foreign_key="rol.id", primary_key=True)

class RolPermiso(SQLModel, table=True):
    """Tabla intermedia para asignar Permiso a roles (Matriz de Permiso)."""
    rol_id: int = Field(foreign_key="rol.id", primary_key=True)
    permiso_id: int = Field(foreign_key="permiso.id", primary_key=True)

class Rol(SQLModel, table=True):
    """Modelo para los Roles del sistema (Admin, Coordinador, etc.)."""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: Optional[str] = None
    
    # Relaciones
    usuarios: List["Usuario"] = Relationship(back_populates="roles", link_model=RolUsuario)
    permisos: List["Permiso"] = Relationship(back_populates="roles", link_model=RolPermiso)
    
    creado_por: Optional[int] = Field(default=None, foreign_key="usuario.id")


class Permiso(SQLModel, table=True):
    """Modelo para los Permiso ( slugs como 'usuario.crear' )."""
    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(unique=True, index=True)
    description: Optional[str] = None
    module: str = Field(index=True) # Para agrupar: 'usuarios', 'config', etc.
    
    # Relaciones
    roles: List[Rol] = Relationship(back_populates="permisos", link_model=RolPermiso)
    
    creado_por: Optional[int] = Field(default=None, foreign_key="usuario.id")

