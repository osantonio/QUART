from quart import Blueprint, render_template, request, redirect, url_for, flash
from app.utils.auth import permission_required
from app.services.farmacia import ServicioFarmacia
from app.models.beneficiarios import Medicamento
from app.config import get_session
from sqlmodel import select

farmacia_bp = Blueprint("farmacia", __name__, url_prefix="/farmacia")

@farmacia_bp.route("/")
@farmacia_bp.route("/inventario")
@permission_required
async def inventario():
    inventario = await ServicioFarmacia.obtener_resumen_inventario()
    return await render_template("farmacia/inventario.html", inventario=inventario)

@farmacia_bp.route("/medicamento/<int:id>")
@permission_required
async def detalle_medicamento(id):
    detalle = await ServicioFarmacia.obtener_detalle_medicamento(id)
    return await render_template(
        "farmacia/detalle_medicamento.html", 
        medicamento=detalle["medicamento"], 
        lotes=detalle["lotes"]
    )

@farmacia_bp.route("/lote/nuevo", methods=["GET", "POST"])
@permission_required
async def nuevo_lote():
    if request.method == "POST":
        form = await request.form
        datos = dict(form)
        try:
            await ServicioFarmacia.registrar_lote(datos)
            await flash("Lote registrado correctamente", "success")
            return redirect(url_for("farmacia.inventario"))
        except Exception as e:
            await flash(str(e), "danger")
            
    async for db in get_session():
        stmt = select(Medicamento).order_by(Medicamento.nombre)
        res = await db.execute(stmt)
        medicamentos = res.scalars().all()
        return await render_template("farmacia/form_lote.html", medicamentos=medicamentos)
