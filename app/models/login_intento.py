# app/models/login_intento.py

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class LoginIntento(SQLModel, table=True):
    __tablename__ = "login_intentos"

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id", nullable=True, index=True)
    username_o_email: str = Field(max_length=255)
    ip: Optional[str] = Field(default=None, max_length=45)
    creado_en: datetime = Field(default_factory=datetime.now, index=True)
