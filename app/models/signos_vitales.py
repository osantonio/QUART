from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from decimal import Decimal
from datetime import datetime


class SignosVitales(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    beneficiario_id: int = Field(foreign_key="beneficiario.id")
    registrado_por: int = Field(foreign_key="usuario.id")
    fecha_registro: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)

    beneficiario: "Beneficiario" = Relationship(back_populates="signos_vitales")
    usuario: "Usuario" = Relationship(back_populates="signos_vitales_registrados")
    tension_arterial: Optional["TensionArterial"] = Relationship(back_populates="registro", sa_relationship_kwargs={"uselist": False})
    peso_medicion: Optional["Peso"] = Relationship(back_populates="registro", sa_relationship_kwargs={"uselist": False})
    saturacion: Optional["SaturacionOxigeno"] = Relationship(back_populates="registro", sa_relationship_kwargs={"uselist": False})
    glucosa_medicion: Optional["Glucosa"] = Relationship(back_populates="registro", sa_relationship_kwargs={"uselist": False})


class TensionArterial(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    signos_vitales_id: int = Field(foreign_key="signosvitales.id")
    sistolica: Optional[int] = None
    diastolica: Optional[int] = None
    observaciones: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    registro: "SignosVitales" = Relationship(back_populates="tension_arterial")


class Peso(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    signos_vitales_id: int = Field(foreign_key="signosvitales.id")
    valor: Optional[Decimal] = None
    observaciones: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    registro: "SignosVitales" = Relationship(back_populates="peso_medicion")


class SaturacionOxigeno(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    signos_vitales_id: int = Field(foreign_key="signosvitales.id")
    porcentaje: Optional[int] = None
    observaciones: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    registro: "SignosVitales" = Relationship(back_populates="saturacion")


class Glucosa(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    signos_vitales_id: int = Field(foreign_key="signosvitales.id")
    mg_dl: Optional[int] = None
    observaciones: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    registro: "SignosVitales" = Relationship(back_populates="glucosa_medicion")
