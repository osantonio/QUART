from datetime import date, datetime
import logging
import time
from quart import Blueprint, render_template, request, jsonify
from sqlmodel import select
from sqlalchemy import func
from app.config import get_session
from app.models.beneficiarios import Beneficiario
from app.models.signos_vitales import SignosVitales, Peso

logger = logging.getLogger(__name__)

imc_bp = Blueprint("imc", __name__, url_prefix="/imc")

_imc_cache = {"timestamp": 0.0, "data": None, "count": 0}


def _calcular_edad(fecha_nacimiento: date) -> int:
    today = date.today()
    return today.year - fecha_nacimiento.year - (
        (today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
    )


def _clasificar_imc(valor: float) -> str:
    if valor < 18.5:
        return "Bajo peso"
    if valor < 25:
        return "Normal"
    if valor < 30:
        return "Sobrepeso"
    return "Obesidad"


@imc_bp.route("/")
async def imc_index():
    quiere_json = request.args.get("format") == "json" or "application/json" in request.headers.get("Accept", "")

    try:
        async for db in get_session():
            total_stmt = select(func.count(Beneficiario.id))
            total_beneficiarios = (await db.execute(total_stmt)).scalar_one()

            if total_beneficiarios > 100 and _imc_cache["data"]:
                if time.time() - _imc_cache["timestamp"] < 300:
                    data = _imc_cache["data"]
                    if quiere_json:
                        return jsonify(data)
                    return await render_template("signos_vitales/imc/imc.html", **data)

            sub = (
                select(
                    SignosVitales.beneficiario_id.label("beneficiario_id"),
                    func.max(Peso.id).label("peso_id"),
                )
                .join(Peso, Peso.signos_vitales_id == SignosVitales.id)
                .group_by(SignosVitales.beneficiario_id)
                .subquery()
            )

            stmt = (
                select(
                    Beneficiario.id,
                    Beneficiario.nombres,
                    Beneficiario.apellidos,
                    Beneficiario.fecha_nacimiento,
                    Beneficiario.estatura,
                    Peso.valor,
                )
                .outerjoin(sub, sub.c.beneficiario_id == Beneficiario.id)
                .outerjoin(Peso, Peso.id == sub.c.peso_id)
                .order_by(Beneficiario.apellidos, Beneficiario.nombres)
            )
            res = await db.execute(stmt)
            rows = res.all()

        items = []
        categorias = {
            "Bajo peso": 0,
            "Normal": 0,
            "Sobrepeso": 0,
            "Obesidad": 0,
        }
        total_validos = 0

        for row in rows:
            beneficiario_id = row[0]
            nombres = row[1]
            apellidos = row[2]
            fecha_nacimiento = row[3]
            estatura_cm = row[4]
            peso_kg = row[5]
            edad = _calcular_edad(fecha_nacimiento)

            estatura_m = float(estatura_cm) / 100 if estatura_cm is not None else None
            imc_valor = None
            categoria = "Sin datos"

            if peso_kg is None or estatura_m is None or estatura_m <= 0 or peso_kg <= 0:
                logger.warning(
                    "IMC sin datos para beneficiario %s %s (id=%s) peso=%s estatura_cm=%s",
                    nombres,
                    apellidos,
                    beneficiario_id,
                    peso_kg,
                    estatura_cm,
                )
            else:
                imc_valor = float(peso_kg) / (estatura_m ** 2)
                categoria = _clasificar_imc(imc_valor)
                categorias[categoria] += 1
                total_validos += 1

            items.append(
                {
                    "id": beneficiario_id,
                    "nombre": f"{nombres} {apellidos}",
                    "edad": edad,
                    "peso": float(peso_kg) if peso_kg is not None else None,
                    "estatura": estatura_m,
                    "imc": round(imc_valor, 2) if imc_valor is not None else None,
                    "categoria": categoria,
                }
            )

        distribucion = []
        for categoria, count in categorias.items():
            porcentaje = (count / total_validos * 100) if total_validos > 0 else 0
            distribucion.append(
                {"categoria": categoria, "cantidad": count, "porcentaje": round(porcentaje, 2)}
            )

        data = {
            "items": items,
            "distribucion": distribucion,
            "total": len(items),
            "total_validos": total_validos,
            "actualizado_en": datetime.now().isoformat(),
        }

        if total_beneficiarios > 100:
            _imc_cache["timestamp"] = time.time()
            _imc_cache["data"] = data
            _imc_cache["count"] = total_beneficiarios

        if quiere_json:
            return jsonify(data)
        return await render_template("signos_vitales/imc/imc.html", **data)
    except Exception as exc:
        logger.exception("Error calculando IMC: %s", exc)
        if quiere_json:
            return jsonify({"error": "Error calculando IMC"}), 500
        return await render_template(
            "signos_vitales/imc/imc.html",
            items=[],
            distribucion=[],
            total=0,
            total_validos=0,
            actualizado_en=datetime.now().isoformat(),
        )


@imc_bp.route("/<int:id>")
async def imc_historial(id: int):
    quiere_json = request.args.get("format") == "json" or "application/json" in request.headers.get("Accept", "")

    async for db in get_session():
        beneficiario = (await db.execute(select(Beneficiario).where(Beneficiario.id == id))).scalar_one_or_none()
        if not beneficiario:
            if quiere_json:
                return jsonify({"error": "Beneficiario no encontrado"}), 404
            return await render_template(
                "signos_vitales/imc/imc_historial.html",
                beneficiario=None,
                series=[],
                error="Beneficiario no encontrado",
            ), 404

        stmt = (
            select(SignosVitales.fecha_registro, Peso.valor)
            .join(Peso, Peso.signos_vitales_id == SignosVitales.id)
            .where(SignosVitales.beneficiario_id == id, Peso.valor.is_not(None))
            .order_by(SignosVitales.fecha_registro.asc())
        )
        res = await db.execute(stmt)
        registros = res.all()

    series = [
        {"fecha": fecha.isoformat(), "peso": float(peso)}
        for fecha, peso in registros
        if fecha is not None and peso is not None
    ]

    if quiere_json:
        return jsonify({"beneficiario_id": beneficiario.id, "items": series})

    error = "No hay registros de peso para este beneficiario" if len(series) == 0 else None
    return await render_template(
        "signos_vitales/imc/imc_historial.html",
        beneficiario=beneficiario,
        series=series,
        error=error,
    )
