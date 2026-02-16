from quart import Blueprint, render_template, request, redirect, url_for, flash, session
from app.config import get_session
from app.utils.auth import permission_required
from app.models.visitantes import Visitante, Visita
from app.services.beneficiarios import ServicioBeneficiarios
from sqlmodel import select
from sqlalchemy.orm import selectinload
from datetime import datetime

visitantes_bp = Blueprint("visitantes", __name__, url_prefix="/visitantes")

@visitantes_bp.route("/")
@permission_required
async def listar():
    async for db in get_session():
        stmt = select(Visitante).options(
            selectinload(Visitante.beneficiario)
        ).order_by(Visitante.apellidos)
        result = await db.execute(stmt)
        visitantes = result.scalars().all()
        return await render_template("visitantes/listar.html", visitantes=visitantes)

@visitantes_bp.route("/crear", methods=["GET", "POST"])
@permission_required
async def crear():
    beneficiario_id = request.args.get("beneficiario_id")
    if request.method == "POST":
        form = await request.form
        datos = dict(form)
        usuario_id = session.get("user_id")

        try:
            datos["beneficiario_id"] = int(datos["beneficiario_id"]) if datos.get("beneficiario_id") else (int(beneficiario_id) if beneficiario_id else None)
            async for db in get_session():
                nuevo_visitante = Visitante(**datos)
                db.add(nuevo_visitante)

                if datos.get("beneficiario_id"):
                    await ServicioBeneficiarios.registrar_auditoria(
                        db,
                        int(datos["beneficiario_id"]),
                        usuario_id,
                        "Visitante",
                        "Creación",
                        None,
                        "nuevo_visitante",
                        None,
                        f"{nuevo_visitante.nombres} {nuevo_visitante.apellidos}",
                    )

                await db.commit()
                await flash("Visitante registrado correctamente", "success")
                if datos.get("beneficiario_id"):
                    return redirect(url_for("beneficiarios.perfil", id=int(datos["beneficiario_id"])))
                return redirect(url_for("visitantes.listar"))
        except Exception as e:
            await flash(str(e), "danger")

    async for db in get_session():
        back_url = url_for("visitantes.listar")
        if beneficiario_id:
            back_url = url_for("beneficiarios.perfil", id=int(beneficiario_id))
        return await render_template(
            "visitantes/crear.html",
            beneficiario_id=int(beneficiario_id) if beneficiario_id else None,
            back_url=back_url,
        )



@visitantes_bp.route("/visitas/registrar/<int:beneficiario_id>", methods=["GET", "POST"])
@permission_required
async def registrar_visita(beneficiario_id: int):
    if request.method == "POST":
        form = await request.form
        datos = dict(form)
        datos["beneficiario_id"] = beneficiario_id
        datos["tramitado_por"] = session.get("user_id")

        if datos.get("hora_entrada"):
            datos["hora_entrada"] = datetime.strptime(datos["hora_entrada"], "%H:%M").time()

        async for db in get_session():
            nueva = Visita(**datos)
            db.add(nueva)
            await db.commit()
            await flash("Visita registrada correctamente", "success")
            return redirect(url_for("beneficiarios.perfil", id=beneficiario_id))

    async for db in get_session():
        visitantes = (
            await db.execute(select(Visitante).where(Visitante.beneficiario_id == beneficiario_id))
        ).scalars().all()
        back_url = url_for("beneficiarios.perfil", id=beneficiario_id)
        return await render_template(
            "visitas/registrar.html",
            beneficiario_id=beneficiario_id,
            visitantes=visitantes,
            hoy=datetime.now().date().isoformat(),
            back_url=back_url,
        )
