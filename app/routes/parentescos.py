from quart import Blueprint, render_template, request, redirect, url_for, flash, session
from app.config import get_session
from app.utils.auth import permission_required
from app.models.parentescos import Parentesco, RelacionParentesco
from app.models.visitantes import Visitante
from app.models.beneficiarios import Beneficiario
from app.models.usuario import Usuario
from app.services.beneficiarios import ServicioBeneficiarios
from app.utils.exceptions import ValidationError
from sqlmodel import select, delete
from sqlalchemy.orm import selectinload

parentescos_bp = Blueprint("parentescos", __name__, url_prefix="/parentescos")

@parentescos_bp.route("/", methods=["GET"])
@permission_required
async def listar():
    async for db in get_session():
        stmt = select(Parentesco).order_by(Parentesco.nombre)
        res = await db.execute(stmt)
        parentescos = res.scalars().all()
        return await render_template("parentescos/listar.html", parentescos=parentescos)

@parentescos_bp.route("/crear", methods=["GET", "POST"])
@permission_required
async def crear():
    if request.method == "POST":
        form = await request.form
        datos = dict(form)
        try:
            if not datos.get("nombre"):
                raise ValidationError("El nombre es obligatorio")
            datos["contacto_emergencia"] = True if datos.get("contacto_emergencia") in ("1", "true", "True", "on") else False
            async for db in get_session():
                existente = (await db.execute(select(Parentesco).where(Parentesco.nombre == datos["nombre"]))).scalar_one_or_none()
                if existente:
                    await flash("Ya existe un parentesco con ese nombre", "warning")
                    return redirect(url_for("parentescos.crear"))
                nuevo = Parentesco(
                    nombre=datos["nombre"],
                    descripcion=datos.get("descripcion"),
                    contacto_emergencia=datos["contacto_emergencia"]
                )
                db.add(nuevo)
                await db.commit()
                await flash("Parentesco creado correctamente", "success")
                return redirect(url_for("parentescos.listar"))
        except Exception as e:
            await flash(str(e), "danger")
    return await render_template("parentescos/crear.html")

@parentescos_bp.route("/editar/<int:id>", methods=["GET", "POST"])
@permission_required
async def editar(id: int):
    if request.method == "POST":
        form = await request.form
        datos = dict(form)
        try:
            if not datos.get("nombre"):
                raise ValidationError("El nombre es obligatorio")
            datos["contacto_emergencia"] = True if datos.get("contacto_emergencia") in ("1", "true", "True", "on") else False
            async for db in get_session():
                existente = (await db.execute(select(Parentesco).where(Parentesco.nombre == datos["nombre"], Parentesco.id != id))).scalar_one_or_none()
                if existente:
                    await flash("Ya existe un parentesco con ese nombre", "warning")
                    return redirect(url_for("parentescos.editar", id=id))
                p = (await db.execute(select(Parentesco).where(Parentesco.id == id))).scalar_one_or_none()
                if not p:
                    await flash("Parentesco no encontrado", "danger")
                    return redirect(url_for("parentescos.listar"))
                p.nombre = datos["nombre"]
                p.descripcion = datos.get("descripcion")
                p.contacto_emergencia = datos["contacto_emergencia"]
                await db.commit()
                await flash("Parentesco actualizado correctamente", "success")
                return redirect(url_for("parentescos.listar"))
        except Exception as e:
            await flash(str(e), "danger")
    async for db in get_session():
        p = (await db.execute(select(Parentesco).where(Parentesco.id == id))).scalar_one_or_none()
        if not p:
            await flash("Parentesco no encontrado", "danger")
            return redirect(url_for("parentescos.listar"))
        return await render_template("parentescos/editar.html", p=p)

@parentescos_bp.route("/eliminar/<int:id>/confirmar", methods=["GET"])
@permission_required
async def confirmar_eliminar(id: int):
    async for db in get_session():
        p = (await db.execute(select(Parentesco).where(Parentesco.id == id))).scalar_one_or_none()
        if not p:
            await flash("Parentesco no encontrado", "danger")
            return redirect(url_for("parentescos.listar"))
        return await render_template("parentescos/confirmar_eliminar.html", p=p)

@parentescos_bp.route("/eliminar/<int:id>", methods=["POST"])
@permission_required
async def eliminar(id: int):
    async for db in get_session():
        try:
            await db.execute(delete(Parentesco).where(Parentesco.id == id))
            await db.commit()
            await flash("Parentesco eliminado", "success")
        except Exception as e:
            await flash("No se pudo eliminar el parentesco. Verifique relaciones existentes.", "danger")
        return redirect(url_for("parentescos.listar"))

@parentescos_bp.route("/asignar", methods=["GET", "POST"])
@permission_required
async def asignar():
    visitante_id = request.args.get("visitante_id")
    beneficiario_id = request.args.get("beneficiario_id")
    back_url = url_for("visitantes.listar")
    if beneficiario_id:
        back_url = url_for("beneficiarios.perfil", id=int(beneficiario_id))

    if request.method == "POST":
        form = await request.form
        raw = dict(form)
        try:
            visitante_id = int(raw.get("visitante_id")) if raw.get("visitante_id") else None
            parentesco_id = int(raw.get("parentesco_id")) if raw.get("parentesco_id") else None
            beneficiario_id = int(raw.get("beneficiario_id")) if raw.get("beneficiario_id") else None
            usuario_id = int(raw.get("usuario_id")) if raw.get("usuario_id") else None

            if not visitante_id or not parentesco_id:
                raise ValidationError("Visitante y parentesco son obligatorios")
            if not beneficiario_id and not usuario_id:
                raise ValidationError("Debe seleccionar beneficiario o usuario")
            if beneficiario_id and usuario_id:
                raise ValidationError("Seleccione solo beneficiario o usuario")

            payload = {
                "visitante_id": visitante_id,
                "parentesco_id": parentesco_id,
                "beneficiario_id": beneficiario_id,
                "usuario_id": usuario_id,
            }

            async for db in get_session():
                rel = RelacionParentesco(**payload)
                db.add(rel)
                
                if beneficiario_id:
                    p = (await db.execute(select(Parentesco).where(Parentesco.id == parentesco_id))).scalar_one_or_none()
                    v = (await db.execute(select(Visitante).where(Visitante.id == visitante_id))).scalar_one_or_none()
                    nuevo_valor = None
                    try:
                        if p and v:
                            nuevo_valor = f"{p.nombre} con {v.nombres} {v.apellidos}"
                        elif p:
                            nuevo_valor = p.nombre
                        elif v:
                            nuevo_valor = f"{v.nombres} {v.apellidos}"
                    except Exception:
                        nuevo_valor = None
                    
                    usuario_actual_id = session.get("user_id")
                    await ServicioBeneficiarios.registrar_auditoria(
                        db,
                        beneficiario_id,
                        usuario_actual_id if usuario_actual_id else None,
                        "RelacionParentesco",
                        "Creación",
                        rel.id,
                        "parentesco",
                        None,
                        nuevo_valor,
                    )
                
                await db.commit()
                await flash("Parentesco establecido correctamente", "success")
                if beneficiario_id:
                    return redirect(url_for("beneficiarios.perfil", id=int(beneficiario_id)))
                return redirect(url_for("visitantes.listar"))
        except Exception as e:
            await flash(str(e), "danger")

    async for db in get_session():
        parentescos = (await db.execute(select(Parentesco).order_by(Parentesco.nombre))).scalars().all()
        visitantes = (await db.execute(select(Visitante).order_by(Visitante.apellidos))).scalars().all()
        beneficiarios = (await db.execute(select(Beneficiario).order_by(Beneficiario.apellidos))).scalars().all()
        usuarios = (await db.execute(select(Usuario).order_by(Usuario.apellidos))).scalars().all()
        return await render_template(
            "parentescos/asignar.html",
            visitante_id=int(visitante_id) if visitante_id else None,
            beneficiario_id=int(beneficiario_id) if beneficiario_id else None,
            visitantes=visitantes,
            beneficiarios=beneficiarios,
            usuarios=usuarios,
            parentescos=parentescos,
            back_url=back_url,
        )

@parentescos_bp.route("/asignado", methods=["GET"])
@permission_required
async def asignado():
    async for db in get_session():
        stmt = (
            select(RelacionParentesco)
            .options(
                selectinload(RelacionParentesco.visitante),
                selectinload(RelacionParentesco.parentesco),
                selectinload(RelacionParentesco.beneficiario),
                selectinload(RelacionParentesco.usuario),
            )
            .order_by(RelacionParentesco.created_at.desc())
        )
        res = await db.execute(stmt)
        relaciones = res.scalars().all()
        return await render_template("parentescos/asignado.html", relaciones=relaciones)
