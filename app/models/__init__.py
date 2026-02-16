# app/models/__init__.py

from app.models.usuario import Usuario
from app.models.roles import Rol, Permiso, RolUsuario, RolPermiso
from app.models.beneficiarios import (
    Beneficiario, Alergia, BeneficiarioAlergia, Patologia, BeneficiarioPatologia,
    HistorialPatologia, Medicamento, MedicamentoBeneficiario, HistorialPrescripcion,
    CantidadMedicamento, ExBeneficiarios
)
from app.models.signos_vitales import SignosVitales, TensionArterial, Peso, SaturacionOxigeno, Glucosa
from app.models.historia_clinica import HistoriaClinica
from app.models.visitantes import Visitante, Visita
from app.models.parentescos import Parentesco, RelacionParentesco

models = [
    Usuario,
    Rol,
    Permiso,
    RolUsuario,
    RolPermiso,
    Beneficiario,
    Visitante,
    Parentesco,
    Visita,
    RelacionParentesco,
    Alergia,
    BeneficiarioAlergia,
    Patologia,
    BeneficiarioPatologia,
    HistorialPatologia,
    Medicamento,
    MedicamentoBeneficiario,
    HistorialPrescripcion,
    CantidadMedicamento,
    SignosVitales,
    TensionArterial,
    Peso,
    SaturacionOxigeno,
    Glucosa,
    HistoriaClinica,
    ExBeneficiarios
]
