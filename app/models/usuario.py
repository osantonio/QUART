from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from app.models.roles import Rol, RolUsuario
import bcrypt

class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    google_id: Optional[str] = Field(default=None, unique=True)
    identificacion: Optional[int] = Field(default=None, unique=True)
    username: str = Field(unique=True, index=True)
    nombres: str
    apellidos: str
    email: str = Field(unique=True, index=True)
    password: Optional[str] = None  # Opcional para soportar OAuth luego
    telefono: Optional[str] = None
    fecha_nacimiento: Optional[str] = None
    foto_perfil: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now)

    # Nuevos campos para IPS
    genero: Optional[str] = None  # M, F, Otro
    tipo_sangre: Optional[str] = None  # A+, A-, B+, B-, AB+, AB-, O+, O-

    # Relación RBAC
    roles: List["Rol"] = Relationship(back_populates="usuarios", link_model=RolUsuario)

    # Relaciones con módulo Beneficiarios (Auditoría y Gestión)
    visitantes: List["Visitante"] = Relationship(back_populates="usuario")
    visitas_tramitadas: List["Visita"] = Relationship(back_populates="tramitado_por_usuario")
    historial_prescripciones: List["HistorialPrescripcion"] = Relationship(back_populates="modificado_por_usuario")
    historial_patologias: List["HistorialPatologia"] = Relationship(back_populates="modificado_por_usuario")
    historia_clinica: List["HistoriaClinica"] = Relationship(back_populates="modificado_por_usuario")
    signos_vitales_registrados: List["SignosVitales"] = Relationship(back_populates="usuario")
    relaciones_parentesco: List["RelacionParentesco"] = Relationship(back_populates="usuario")

    def set_password(self, password: str) -> None:
        """Hash y guarda la contraseña"""
        salt = bcrypt.gensalt()
        self.password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, password: str) -> bool:
        """Verifica si la contraseña coincide con el hash bcrypt"""
        if not self.password:
            return False
        
        # Verificar usando bcrypt
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
