from quart import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.config import get_session
from app.utils.auth import permission_required
from sqlmodel import select
from sqlalchemy.orm import selectinload

signos_vitales_bp = Blueprint("signos_vitales", __name__, url_prefix="/signos-vitales")

@signos_vitales_bp.route("/asignar/<int:beneficiario_id>", methods=["GET", "POST"])
@permission_required
async def asignar(beneficiario_id):
    from decimal import Decimal
    from app.models.signos_vitales import SignosVitales, TensionArterial, Peso, SaturacionOxigeno, Glucosa
    from app.models.historia_clinica import HistoriaClinica
    if request.method == "POST":
        form = await request.form
        datos = dict(form)
        usuario_id = session.get("user_id")
        
        try:
            async for db in get_session():
                registros_creados = 0

                if datos.get("tension_arterial_sistolica") or datos.get("tension_arterial_diastolica"):
                    registro_ta = SignosVitales(
                        beneficiario_id=beneficiario_id,
                        registrado_por=usuario_id
                    )
                    db.add(registro_ta)
                    await db.commit()
                    await db.refresh(registro_ta)
                    # Buscar valor anterior de TA
                    prev_ta_val = None
                    prev_stmt_sv = select(SignosVitales).options(
                        selectinload(SignosVitales.tension_arterial)
                    ).where(SignosVitales.beneficiario_id == beneficiario_id).order_by(SignosVitales.fecha_registro.desc())
                    prev_res_sv = await db.execute(prev_stmt_sv)
                    prev_svs = prev_res_sv.scalars().all()
                    for sv in prev_svs:
                        if sv.id != registro_ta.id and sv.tension_arterial:
                            prev_ta_val = f"{sv.tension_arterial.sistolica or '—'}/{sv.tension_arterial.diastolica or '—'} mmHg"
                            break
                    ta = TensionArterial(
                        signos_vitales_id=registro_ta.id,
                        sistolica=int(datos["tension_arterial_sistolica"]) if datos.get("tension_arterial_sistolica") else None,
                        diastolica=int(datos["tension_arterial_diastolica"]) if datos.get("tension_arterial_diastolica") else None,
                        observaciones=datos.get("observaciones_tension")
                    )
                    db.add(ta)
                    await db.commit()
                    # Log Historia Clínica
                    oper_ta = "Creación" if prev_ta_val is None else "Modificación"
                    hc_ta = HistoriaClinica(
                        beneficiario_id=beneficiario_id,
                        modificado_por=usuario_id,
                        tabla_modificada="tension_arterial",
                        registro_id=ta.id,
                        campo_modificado="registro",
                        valor_anterior=prev_ta_val,
                        valor_nuevo=f"{ta.sistolica or '—'}/{ta.diastolica or '—'} mmHg",
                        tipo_operacion=oper_ta,
                        motivo="Registro de Signo Vital",
                        ip_address=None
                    )
                    db.add(hc_ta)
                    await db.commit()
                    registros_creados += 1
                
                if datos.get("peso"):
                    registro_peso = SignosVitales(
                        beneficiario_id=beneficiario_id,
                        registrado_por=usuario_id
                    )
                    db.add(registro_peso)
                    await db.commit()
                    await db.refresh(registro_peso)
                    # Buscar valor anterior de Peso
                    prev_peso_val = None
                    prev_stmt_sv = select(SignosVitales).options(
                        selectinload(SignosVitales.peso_medicion)
                    ).where(SignosVitales.beneficiario_id == beneficiario_id).order_by(SignosVitales.fecha_registro.desc())
                    prev_res_sv = await db.execute(prev_stmt_sv)
                    prev_svs = prev_res_sv.scalars().all()
                    for sv in prev_svs:
                        if sv.id != registro_peso.id and sv.peso_medicion and sv.peso_medicion.valor is not None:
                            prev_peso_val = f"{sv.peso_medicion.valor} kg"
                            break
                    p = Peso(
                        signos_vitales_id=registro_peso.id,
                        valor=Decimal(datos["peso"]),
                        observaciones=datos.get("observaciones_peso")
                    )
                    db.add(p)
                    await db.commit()
                    # Log Historia Clínica
                    oper_peso = "Creación" if prev_peso_val is None else "Modificación"
                    hc_p = HistoriaClinica(
                        beneficiario_id=beneficiario_id,
                        modificado_por=usuario_id,
                        tabla_modificada="peso",
                        registro_id=p.id,
                        campo_modificado="valor",
                        valor_anterior=prev_peso_val,
                        valor_nuevo=f"{p.valor} kg",
                        tipo_operacion=oper_peso,
                        motivo="Registro de Signo Vital",
                        ip_address=None
                    )
                    db.add(hc_p)
                    await db.commit()
                    registros_creados += 1
                
                if datos.get("saturacion_oxigeno"):
                    registro_o2 = SignosVitales(
                        beneficiario_id=beneficiario_id,
                        registrado_por=usuario_id
                    )
                    db.add(registro_o2)
                    await db.commit()
                    await db.refresh(registro_o2)
                    # Buscar valor anterior de O₂
                    prev_o2_val = None
                    prev_stmt_sv = select(SignosVitales).options(
                        selectinload(SignosVitales.saturacion)
                    ).where(SignosVitales.beneficiario_id == beneficiario_id).order_by(SignosVitales.fecha_registro.desc())
                    prev_res_sv = await db.execute(prev_stmt_sv)
                    prev_svs = prev_res_sv.scalars().all()
                    for sv in prev_svs:
                        if sv.id != registro_o2.id and sv.saturacion and sv.saturacion.porcentaje is not None:
                            prev_o2_val = f"{sv.saturacion.porcentaje}%"
                            break
                    s = SaturacionOxigeno(
                        signos_vitales_id=registro_o2.id,
                        porcentaje=int(datos["saturacion_oxigeno"]),
                        observaciones=datos.get("observaciones_saturacion")
                    )
                    db.add(s)
                    await db.commit()
                    # Log Historia Clínica
                    oper_o2 = "Creación" if prev_o2_val is None else "Modificación"
                    hc_o2 = HistoriaClinica(
                        beneficiario_id=beneficiario_id,
                        modificado_por=usuario_id,
                        tabla_modificada="saturacion_oxigeno",
                        registro_id=s.id,
                        campo_modificado="porcentaje",
                        valor_anterior=prev_o2_val,
                        valor_nuevo=f"{s.porcentaje}%",
                        tipo_operacion=oper_o2,
                        motivo="Registro de Signo Vital",
                        ip_address=None
                    )
                    db.add(hc_o2)
                    await db.commit()
                    registros_creados += 1
                
                if datos.get("glucosa"):
                    registro_glu = SignosVitales(
                        beneficiario_id=beneficiario_id,
                        registrado_por=usuario_id
                    )
                    db.add(registro_glu)
                    await db.commit()
                    await db.refresh(registro_glu)
                    # Buscar valor anterior de Glucosa
                    prev_glu_val = None
                    prev_stmt_sv = select(SignosVitales).options(
                        selectinload(SignosVitales.glucosa_medicion)
                    ).where(SignosVitales.beneficiario_id == beneficiario_id).order_by(SignosVitales.fecha_registro.desc())
                    prev_res_sv = await db.execute(prev_stmt_sv)
                    prev_svs = prev_res_sv.scalars().all()
                    for sv in prev_svs:
                        if sv.id != registro_glu.id and sv.glucosa_medicion and sv.glucosa_medicion.mg_dl is not None:
                            prev_glu_val = f"{sv.glucosa_medicion.mg_dl} mg/dL"
                            break
                    g = Glucosa(
                        signos_vitales_id=registro_glu.id,
                        mg_dl=int(datos["glucosa"]),
                        observaciones=datos.get("observaciones_glucosa")
                    )
                    db.add(g)
                    await db.commit()
                    # Log Historia Clínica
                    oper_glu = "Creación" if prev_glu_val is None else "Modificación"
                    hc_glu = HistoriaClinica(
                        beneficiario_id=beneficiario_id,
                        modificado_por=usuario_id,
                        tabla_modificada="glucosa",
                        registro_id=g.id,
                        campo_modificado="mg_dl",
                        valor_anterior=prev_glu_val,
                        valor_nuevo=f"{g.mg_dl} mg/dL",
                        tipo_operacion=oper_glu,
                        motivo="Registro de Signo Vital",
                        ip_address=None
                    )
                    db.add(hc_glu)
                    await db.commit()
                    registros_creados += 1

                if registros_creados == 0:
                    await flash("Debe registrar al menos un signo vital.", "warning")
                    return redirect(url_for("signos_vitales.asignar", beneficiario_id=beneficiario_id))

                await flash(f"Se registraron {registros_creados} mediciones.", "success")
                return redirect(url_for("signos_vitales.listar", id=beneficiario_id))
        except Exception as e:
            await flash(f"Error: {e}", "danger")

    return await render_template("signos_vitales/asignar.html", beneficiario_id=beneficiario_id)

@signos_vitales_bp.route("/historial")
@permission_required
async def historial():
    from app.models.signos_vitales import SignosVitales
    async for db in get_session():
        stmt = select(SignosVitales).options(
            selectinload(SignosVitales.beneficiario),
            selectinload(SignosVitales.usuario),
            selectinload(SignosVitales.tension_arterial),
            selectinload(SignosVitales.peso_medicion),
            selectinload(SignosVitales.saturacion),
            selectinload(SignosVitales.glucosa_medicion),
        ).order_by(SignosVitales.fecha_registro.desc())
        res = await db.execute(stmt)
        registros = res.scalars().all()
        return await render_template("signos_vitales/historial.html", registros=registros)

@signos_vitales_bp.route("/historial/<int:beneficiario_id>")
@permission_required
async def historial_beneficiario(beneficiario_id: int):
    from app.models.beneficiarios import Beneficiario
    from app.models.signos_vitales import SignosVitales
    async for db in get_session():
        b = (await db.execute(select(Beneficiario).where(Beneficiario.id == beneficiario_id))).scalar_one_or_none()
        stmt = select(SignosVitales).options(
            selectinload(SignosVitales.tension_arterial),
            selectinload(SignosVitales.peso_medicion),
            selectinload(SignosVitales.saturacion),
            selectinload(SignosVitales.glucosa_medicion),
            selectinload(SignosVitales.usuario),
        ).where(SignosVitales.beneficiario_id == beneficiario_id).order_by(SignosVitales.fecha_registro.desc())
        res = await db.execute(stmt)
        registros = res.scalars().all()
        return await render_template("signos_vitales/historial_beneficiario.html", beneficiario=b, registros=registros)

@signos_vitales_bp.route("/")
@permission_required
async def listar():
    from app.models.beneficiarios import Beneficiario
    from app.models.signos_vitales import SignosVitales
    async for db in get_session():
        stmt = select(Beneficiario).options(
            selectinload(Beneficiario.signos_vitales).selectinload(SignosVitales.tension_arterial),
            selectinload(Beneficiario.signos_vitales).selectinload(SignosVitales.peso_medicion),
            selectinload(Beneficiario.signos_vitales).selectinload(SignosVitales.saturacion),
            selectinload(Beneficiario.signos_vitales).selectinload(SignosVitales.glucosa_medicion),
            selectinload(Beneficiario.signos_vitales).selectinload(SignosVitales.usuario),
        ).order_by(Beneficiario.id)
        res = await db.execute(stmt)
        beneficiarios = res.scalars().all()
        items = []
        for b in beneficiarios:
            ta_candidates = [sv.tension_arterial for sv in (b.signos_vitales or []) if sv.tension_arterial]
            ta = max(ta_candidates, key=lambda x: getattr(x, "created_at", None) or getattr(x, "id", 0), default=None)
            peso_candidates = [sv.peso_medicion for sv in (b.signos_vitales or []) if sv.peso_medicion and sv.peso_medicion.valor is not None]
            peso = max(peso_candidates, key=lambda x: getattr(x, "created_at", None) or getattr(x, "id", 0), default=None)
            o2_candidates = [sv.saturacion for sv in (b.signos_vitales or []) if sv.saturacion and sv.saturacion.porcentaje is not None]
            o2 = max(o2_candidates, key=lambda x: getattr(x, "created_at", None) or getattr(x, "id", 0), default=None)
            glucosa_candidates = [sv.glucosa_medicion for sv in (b.signos_vitales or []) if sv.glucosa_medicion and sv.glucosa_medicion.mg_dl is not None]
            glucosa = max(glucosa_candidates, key=lambda x: getattr(x, "created_at", None) or getattr(x, "id", 0), default=None)
            items.append({"beneficiario": b, "ta": ta, "peso": peso, "o2": o2, "glucosa": glucosa})
        return await render_template("signos_vitales/listar.html", items=items)
