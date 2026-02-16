from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, date, time

class Visitante(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    beneficiario_id: Optional[int] = Field(default=None, foreign_key="beneficiario.id")
    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id")
    identificacion: Optional[int] = Field(default=None, unique=True)
    nombres: str
    apellidos: str
    telefono: str
    genero: Optional[str] = None
    fecha_nacimiento: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    beneficiario: Optional["Beneficiario"] = Relationship(back_populates="visitantes")
    usuario: Optional["Usuario"] = Relationship(back_populates="visitantes")
    visitas: List["Visita"] = Relationship(back_populates="visitante")
    relaciones_parentesco: List["RelacionParentesco"] = Relationship(back_populates="visitante")


class Visita(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    beneficiario_id: int = Field(foreign_key="beneficiario.id")
    visitante_id: int = Field(foreign_key="visitante.id")
    tramitado_por: int = Field(foreign_key="usuario.id")
    fecha_visita: date = Field(default_factory=date.today)
    hora_entrada: time
    hora_salida: Optional[time] = None
    observaciones: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    beneficiario: "Beneficiario" = Relationship(back_populates="visitas")
    visitante: "Visitante" = Relationship(back_populates="visitas")
    tramitado_por_usuario: "Usuario" = Relationship(back_populates="visitas_tramitadas")
