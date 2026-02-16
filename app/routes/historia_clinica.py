from quart import Blueprint, render_template
from app.config import get_session
from app.utils.auth import permission_required
from sqlmodel import select
from sqlalchemy.orm import selectinload
from app.models.historia_clinica import HistoriaClinica
from app.models.beneficiarios import Beneficiario

hclinica_bp = Blueprint("hclinica", __name__, url_prefix="/beneficiarios/historia_clinica")

@hclinica_bp.route("/<int:id>")
@permission_required
async def historia_clinica(id: int):
    async for db in get_session():
        stmt = select(HistoriaClinica).options(
            selectinload(HistoriaClinica.modificado_por_usuario)
        ).where(HistoriaClinica.beneficiario_id == id).order_by(HistoriaClinica.fecha_modificacion.desc())
        result = await db.execute(stmt)
        eventos = result.scalars().all()

        beneficiario = (await db.execute(select(Beneficiario).where(Beneficiario.id == id))).scalar_one_or_none()
        return await render_template("beneficiarios/historia_clinica.html", beneficiario=beneficiario, eventos=eventos)
