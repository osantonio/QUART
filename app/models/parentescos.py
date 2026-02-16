from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class Parentesco(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(unique=True, index=True)
    descripcion: Optional[str] = None
    contacto_emergencia: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    relaciones: List["RelacionParentesco"] = Relationship(back_populates="parentesco")

class RelacionParentesco(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    visitante_id: int = Field(foreign_key="visitante.id")
    parentesco_id: int = Field(foreign_key="parentesco.id")
    beneficiario_id: Optional[int] = Field(default=None, foreign_key="beneficiario.id")
    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id")
    created_at: datetime = Field(default_factory=datetime.now)

    visitante: "Visitante" = Relationship(back_populates="relaciones_parentesco")
    parentesco: "Parentesco" = Relationship(back_populates="relaciones")
    beneficiario: Optional["Beneficiario"] = Relationship(back_populates="relaciones_parentesco")
    usuario: Optional["Usuario"] = Relationship(back_populates="relaciones_parentesco")
