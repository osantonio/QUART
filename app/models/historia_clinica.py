from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime


class HistoriaClinica(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    beneficiario_id: int = Field(foreign_key="beneficiario.id")
    modificado_por: int = Field(foreign_key="usuario.id")
    tabla_modificada: str
    registro_id: Optional[int] = None
    campo_modificado: str
    valor_anterior: Optional[str] = None
    valor_nuevo: Optional[str] = None
    tipo_operacion: str
    motivo: Optional[str] = None
    fecha_modificacion: datetime = Field(default_factory=datetime.now)
    ip_address: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    beneficiario: "Beneficiario" = Relationship(back_populates="historia_clinica")
    modificado_por_usuario: "Usuario" = Relationship(back_populates="historia_clinica")
