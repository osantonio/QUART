from quart import Blueprint, render_template, request, redirect, url_for, flash, session
from app.config import get_session
from app.utils.auth import permission_required
from app.models.beneficiarios import Beneficiario
from app.models.historia_clinica import HistoriaClinica
from app.models.visitantes import Visitante, Visita
from app.services.beneficiarios import ServicioBeneficiarios
from sqlmodel import select
from sqlalchemy.orm import selectinload
from datetime import datetime, date

beneficiarios_bp = Blueprint("beneficiarios", __name__, url_prefix="/beneficiarios")

@beneficiarios_bp.route("/")
@permission_required
async def listar():
    async for db in get_session():
        stmt = select(Beneficiario).order_by(Beneficiario.apellidos)
        result = await db.execute(stmt)
        beneficiarios = result.scalars().all()
        return await render_template("beneficiarios/listar.html", beneficiarios=beneficiarios)

@beneficiarios_bp.route("/edad")
@permission_required
async def edad():
    async for db in get_session():
        stmt = select(Beneficiario)
        result = await db.execute(stmt)
        beneficiarios = result.scalars().all()

        today = date.today()

        def days_until_next_birthday(b):
            dob = b.fecha_nacimiento
            try:
                next_bd = date(today.year, dob.month, dob.day)
            except ValueError:
                if dob.month == 2 and dob.day == 29:
                    next_bd = date(today.year, 2, 28)
                else:
                    next_bd = date(today.year, dob.month, dob.day)
            if next_bd < today:
                try:
                    next_bd = date(today.year + 1, dob.month, dob.day)
                except ValueError:
                    if dob.month == 2 and dob.day == 29:
                        next_bd = date(today.year + 1, 2, 28)
                    else:
                        next_bd = date(today.year + 1, dob.month, dob.day)
            return (next_bd - today).days

        beneficiarios_ordenados = sorted(beneficiarios, key=days_until_next_birthday)
        total_beneficiarios = len(beneficiarios_ordenados)
        return await render_template("beneficiarios/edad.html", beneficiarios=beneficiarios_ordenados, total_beneficiarios=total_beneficiarios)
@beneficiarios_bp.route("/crear", methods=["GET", "POST"])
@permission_required
async def crear():
    if request.method == "POST":
        form = await request.form
        datos = dict(form)
        usuario_id = session.get("user_id")
        
        try:
            # Procesar fechas y tipos si es necesario
            if datos.get("fecha_nacimiento"):
                datos["fecha_nacimiento"] = datetime.strptime(datos["fecha_nacimiento"], "%Y-%m-%d").date()
            if datos.get("fecha_ingreso"):
                datos["fecha_ingreso"] = datetime.strptime(datos["fecha_ingreso"], "%Y-%m-%d").date()
            if datos.get("estatura"):
                datos["estatura"] = float(datos["estatura"])
                
            await ServicioBeneficiarios.crear_beneficiario(datos, usuario_id)
            await flash("Beneficiario registrado exitosamente", "success")
            return redirect(url_for("beneficiarios.listar"))
        except Exception as e:
            await flash(str(e), "danger")
            
    return await render_template("beneficiarios/crear.html", beneficiario=None)

@beneficiarios_bp.route("/<int:id>")
@permission_required
async def perfil(id):
    async for db in get_session():
        stmt = select(Beneficiario).options(
            selectinload(Beneficiario.visitantes),
            selectinload(Beneficiario.visitas).selectinload(Visita.visitante)
        ).where(Beneficiario.id == id)
        result = await db.execute(stmt)
        beneficiario = result.scalar_one_or_none()
        
        if not beneficiario:
            await flash("Beneficiario no encontrado", "danger")
            return redirect(url_for("beneficiarios.listar"))
            
        return await render_template("beneficiarios/perfil.html", beneficiario=beneficiario)

 

@beneficiarios_bp.route("/<int:id>/editar", methods=["GET", "POST"])
@permission_required
async def editar(id):
    if request.method == "POST":
        form = await request.form
        datos = dict(form)
        usuario_id = session.get("user_id")
        
        try:
            # Procesar campos
            if datos.get("fecha_nacimiento"):
                datos["fecha_nacimiento"] = datetime.strptime(datos["fecha_nacimiento"], "%Y-%m-%d").date()
            if datos.get("fecha_ingreso"):
                datos["fecha_ingreso"] = datetime.strptime(datos["fecha_ingreso"], "%Y-%m-%d").date()
            if datos.get("estatura"):
                datos["estatura"] = float(datos["estatura"])
                
            await ServicioBeneficiarios.actualizar_beneficiario(id, datos, usuario_id)
            await flash("Información actualizada exitosamente", "success")
            return redirect(url_for("beneficiarios.perfil", id=id))
        except Exception as e:
            await flash(str(e), "danger")

    async for db in get_session():
        stmt = select(Beneficiario).where(Beneficiario.id == id)
        result = await db.execute(stmt)
        beneficiario = result.scalar_one_or_none()
        return await render_template("beneficiarios/crear.html", beneficiario=beneficiario)
 

# --- Submódulo: Asignaciones Médicas ---

@beneficiarios_bp.route("/<int:id>/alergias/asignar", methods=["GET", "POST"])
@permission_required
async def asignar_alergia(id):
    from app.models.beneficiarios import Alergia
    if request.method == "POST":
        form = await request.form
        datos = dict(form)
        alergia_id = datos.pop("alergia_id")
        usuario_id = session.get("user_id")
        try:
            await ServicioBeneficiarios.asignar_alergia(id, int(alergia_id), datos, usuario_id)
            await flash("Alergia asignada", "success")
            return redirect(url_for("beneficiarios.perfil", id=id))
        except Exception as e:
            await flash(str(e), "danger")

    async for db in get_session():
        alergias = (await db.execute(select(Alergia))).scalars().all()
        return await render_template("beneficiarios/alergias/asignar.html", beneficiario_id=id, alergias=alergias)

@beneficiarios_bp.route("/<int:id>/patologias/asignar", methods=["GET", "POST"])
@permission_required
async def asignar_patologia(id):
    from app.models.beneficiarios import Patologia
    if request.method == "POST":
        form = await request.form
        datos = dict(form)
        patologia_id = datos.pop("patologia_id")
        usuario_id = session.get("user_id")
        try:
            await ServicioBeneficiarios.asignar_patologia(id, int(patologia_id), datos, usuario_id)
            await flash("Patología asignada", "success")
            return redirect(url_for("beneficiarios.perfil", id=id))
        except Exception as e:
            await flash(str(e), "danger")

    async for db in get_session():
        patologias = (await db.execute(select(Patologia))).scalars().all()
        return await render_template("beneficiarios/patologias/asignar.html", beneficiario_id=id, patologias=patologias)

@beneficiarios_bp.route("/<int:id>/medicamentos/asignar", methods=["GET", "POST"])
@permission_required
async def asignar_medicamento(id):
    from app.models.beneficiarios import Medicamento
    if request.method == "POST":
        form = await request.form
        datos = dict(form)
        medicamento_id = datos.pop("medicamento_id")
        usuario_id = session.get("user_id")
        
        # Procesar fechas
        if datos.get("fecha_inicio"):
            datos["fecha_inicio"] = datetime.strptime(datos["fecha_inicio"], "%Y-%m-%d").date()
        if datos.get("fecha_fin"):
            datos["fecha_fin"] = datetime.strptime(datos["fecha_fin"], "%Y-%m-%d").date()

        try:
            await ServicioBeneficiarios.asignar_medicamento(id, int(medicamento_id), datos, usuario_id)
            await flash("Medicamento asignado", "success")
            return redirect(url_for("beneficiarios.perfil", id=id))
        except Exception as e:
            await flash(str(e), "danger")

    async for db in get_session():
        medicamentos = (await db.execute(select(Medicamento))).scalars().all()
        return await render_template("beneficiarios/medicamentos/asignar.html", beneficiario_id=id, medicamentos=medicamentos)

# --- Submódulo: Egreso y Archivo ---

@beneficiarios_bp.route("/<int:id>/archivar", methods=["GET", "POST"])
@permission_required
async def archivar(id):
    if request.method == "POST":
        form = await request.form
        datos = dict(form)
        usuario_id = session.get("user_id")
        try:
            await ServicioBeneficiarios.archivar_beneficiario(id, datos, usuario_id)
            await flash("Beneficiario archivado correctamente", "warning")
            return redirect(url_for("beneficiarios.listar"))
        except Exception as e:
            await flash(str(e), "danger")

    async for db in get_session():
        stmt = select(Beneficiario).where(Beneficiario.id == id)
        res = await db.execute(stmt)
        b = res.scalar_one_or_none()
        return await render_template("beneficiarios/archivar.html", beneficiario=b)

@beneficiarios_bp.route("/archivo")
@permission_required
async def lista_archivo():
    from app.models.beneficiarios import ExBeneficiarios
    async for db in get_session():
        stmt = select(ExBeneficiarios).order_by(ExBeneficiarios.fecha_egreso.desc())
        res = await db.execute(stmt)
        ex_beneficiarios = res.scalars().all()
        return await render_template("beneficiarios/archivo_listar.html", ex_beneficiarios=ex_beneficiarios)
