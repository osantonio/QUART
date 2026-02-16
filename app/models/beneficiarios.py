from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, Dict, Any
from datetime import datetime, date, time
from decimal import Decimal
from sqlalchemy import JSON

# --- Modelos de Soporte / Catálogos ---
 
class Alergia(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(unique=True, index=True)
    descripcion: Optional[str] = None
    categoria: Optional[str] = None  # Alimentaria, Medicamentosa, Ambiental
    created_at: datetime = Field(default_factory=datetime.now)

    # Relaciones
    beneficiarios: List["BeneficiarioAlergia"] = Relationship(back_populates="alergia")


class Patologia(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(unique=True, index=True)
    descripcion: Optional[str] = None
    categoria: Optional[str] = None  # Crónica, Mental, etc.
    created_at: datetime = Field(default_factory=datetime.now)

    # Relaciones
    beneficiarios: List["BeneficiarioPatologia"] = Relationship(back_populates="patologia")
    historial: List["HistorialPatologia"] = Relationship(back_populates="patologia")


class Medicamento(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(unique=True, index=True)
    nombre_generico: Optional[str] = None
    presentacion: Optional[str] = None  # Tabletas, Jarabe
    concentracion: Optional[str] = None  # 500mg, 10ml
    via_administracion: Optional[str] = None  # Oral, IV
    descripcion: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    # Relaciones
    asignaciones: List["MedicamentoBeneficiario"] = Relationship(back_populates="medicamento")
    lotes: List["CantidadMedicamento"] = Relationship(back_populates="medicamento")
    historial_prescripciones: List["HistorialPrescripcion"] = Relationship(back_populates="medicamento")


# --- Modelo Principal ---

class Beneficiario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    identificacion: str = Field(unique=True, index=True)
    nombres: str
    apellidos: str
    fecha_nacimiento: date
    genero: str  # M, F, Otro
    foto_perfil: Optional[str] = None
    
    # Contacto
    telefono: Optional[str] = None
    email: Optional[str] = None
    ciudad_origen: Optional[str] = None
    departamento_origen: Optional[str] = None
    religion: Optional[str] = None
    
    # Médico Básico
    tipo_sangre: Optional[str] = None
    eps: Optional[str] = None
    estatura: Optional[Decimal] = None  # cm
    
    # Administrativo
    fecha_ingreso: date = Field(default_factory=date.today)
    numero_habitacion: Optional[str] = None
    observaciones: Optional[str] = None
    autorizado_visitas: bool = Field(default=True)
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Propiedades Calculadas
    @property
    def edad(self) -> int:
        today = date.today()
        return today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )

    # Relaciones
    visitantes: List["Visitante"] = Relationship(back_populates="beneficiario")
    visitas: List["Visita"] = Relationship(back_populates="beneficiario")
    alergias: List["BeneficiarioAlergia"] = Relationship(back_populates="beneficiario")
    patologias: List["BeneficiarioPatologia"] = Relationship(back_populates="beneficiario")
    historial_patologias: List["HistorialPatologia"] = Relationship(back_populates="beneficiario")
    medicamentos_asignados: List["MedicamentoBeneficiario"] = Relationship(back_populates="beneficiario")
    historial_prescripciones: List["HistorialPrescripcion"] = Relationship(back_populates="beneficiario")
    lotes_asignados: List["CantidadMedicamento"] = Relationship(back_populates="beneficiario_asignado")
    signos_vitales: List["SignosVitales"] = Relationship(back_populates="beneficiario")
    historia_clinica: List["HistoriaClinica"] = Relationship(back_populates="beneficiario")
    relaciones_parentesco: List["RelacionParentesco"] = Relationship(back_populates="beneficiario")


# --- Relaciones M:N y Detalles ---

class BeneficiarioAlergia(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    beneficiario_id: int = Field(foreign_key="beneficiario.id")
    alergia_id: int = Field(foreign_key="alergia.id")
    severidad: str  # Leve, Moderada, Severa
    notas: Optional[str] = None
    fecha_diagnostico: Optional[date] = None
    
    # Relaciones
    beneficiario: "Beneficiario" = Relationship(back_populates="alergias")
    alergia: "Alergia" = Relationship(back_populates="beneficiarios")


class BeneficiarioPatologia(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    beneficiario_id: int = Field(foreign_key="beneficiario.id")
    patologia_id: int = Field(foreign_key="patologia.id")
    fecha_diagnostico: Optional[date] = None
    genera_discapacidad: bool = Field(default=False)
    tipo_discapacidad: Optional[str] = None
    grado_discapacidad: Optional[str] = None
    nivel_dependencia: str  # Independiente, Parcial, Total
    notas: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.now)

    # Relaciones
    beneficiario: "Beneficiario" = Relationship(back_populates="patologias")
    patologia: "Patologia" = Relationship(back_populates="beneficiarios")


class HistorialPatologia(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    beneficiario_patologia_id_original: int
    beneficiario_id: int = Field(foreign_key="beneficiario.id")
    patologia_id: int = Field(foreign_key="patologia.id")
    nivel_dependencia: str
    genera_discapacidad: bool
    notas: Optional[str] = None
    motivo_cambio: str
    modificado_por: int = Field(foreign_key="usuario.id")
    fecha_modificacion: datetime = Field(default_factory=datetime.now)

    # Relaciones
    beneficiario: "Beneficiario" = Relationship(back_populates="historial_patologias")
    patologia: "Patologia" = Relationship(back_populates="historial")
    modificado_por_usuario: "Usuario" = Relationship(back_populates="historial_patologias")


class MedicamentoBeneficiario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    beneficiario_id: int = Field(foreign_key="beneficiario.id")
    medicamento_id: int = Field(foreign_key="medicamento.id")
    dosis: str
    frecuencia: str
    fecha_inicio: date
    fecha_fin: Optional[date] = None
    prescrito_por: Optional[str] = None
    activo: bool = Field(default=True)
    observaciones: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.now)

    # Relaciones
    beneficiario: "Beneficiario" = Relationship(back_populates="medicamentos_asignados")
    medicamento: "Medicamento" = Relationship(back_populates="asignaciones")


class HistorialPrescripcion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    medicamento_beneficiario_id_original: int
    beneficiario_id: int = Field(foreign_key="beneficiario.id")
    medicamento_id: int = Field(foreign_key="medicamento.id")
    dosis: str
    frecuencia: str
    fecha_inicio: date
    fecha_fin: Optional[date] = None
    activo: bool
    motivo_cambio: str
    modificado_por: int = Field(foreign_key="usuario.id")
    fecha_modificacion: datetime = Field(default_factory=datetime.now)

    # Relaciones
    beneficiario: "Beneficiario" = Relationship(back_populates="historial_prescripciones")
    medicamento: "Medicamento" = Relationship(back_populates="historial_prescripciones")
    modificado_por_usuario: "Usuario" = Relationship(back_populates="historial_prescripciones")

# --- Inventario y Clínica ---

class CantidadMedicamento(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    medicamento_id: int = Field(foreign_key="medicamento.id")
    lote: Optional[str] = None
    fecha_vencimiento: date
    cantidad_disponible: int
    cantidad_inicial: int
    dosis: str  # Dosis del lote
    beneficiario_asignado_id: Optional[int] = Field(default=None, foreign_key="beneficiario.id")
    origen: str  # Compra, Donación, Otro
    proveedor: Optional[str] = None
    fecha_ingreso: date = Field(default_factory=date.today)
    observaciones: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    # Relaciones
    medicamento: "Medicamento" = Relationship(back_populates="lotes")
    beneficiario_asignado: Optional["Beneficiario"] = Relationship(back_populates="lotes_asignados")


 


class ExBeneficiarios(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    beneficiario_id_original: int
    identificacion: str
    nombres: str
    apellidos: str
    fecha_nacimiento: date
    genero: str
    fecha_ingreso: date
    fecha_egreso: date
    motivo_egreso: str
    observaciones_egreso: Optional[str] = None
    datos_completos_json: Dict[str, Any] = Field(default_factory=dict, sa_type=JSON)
    created_at: datetime = Field(default_factory=datetime.now)
