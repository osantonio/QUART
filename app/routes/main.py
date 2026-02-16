# app/routes/main.py

from quart import Blueprint, render_template, redirect, url_for, request
from app.utils.auth import permission_required
from app.config import get_session
from app.models.beneficiarios import Beneficiario
from app.models import Usuario
from app.models.visitantes import Visitante
from sqlmodel import select
from datetime import date

bp = Blueprint("main", __name__)


@bp.route("/")
async def index():
    return await render_template("index.html")


@bp.route("/dashboard")
@permission_required
async def dashboard():
    async for db in get_session():
        stmt = select(Beneficiario)
        result = await db.execute(stmt)
        beneficiarios = result.scalars().all()
        today = date.today()

        total_beneficiarios = len(beneficiarios)
        total_hombres = sum(1 for b in beneficiarios if (b.genero or "").strip().upper() == "M")
        total_mujeres = sum(1 for b in beneficiarios if (b.genero or "").strip().upper() == "F")

        usuarios = (await db.execute(select(Usuario))).scalars().all()
        total_usuarios = len(usuarios)
        total_usuarios_hombres = sum(1 for u in usuarios if (u.genero or "").strip().upper() == "M")
        total_usuarios_mujeres = sum(1 for u in usuarios if (u.genero or "").strip().upper() == "F")

        visitantes = (await db.execute(select(Visitante))).scalars().all()
        total_visitantes = len(visitantes)
        total_visitantes_hombres = sum(1 for v in visitantes if (v.genero or "").strip().upper() == "M")
        total_visitantes_mujeres = sum(1 for v in visitantes if (v.genero or "").strip().upper() == "F")

        def next_birthday_info(b):
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
            days = (next_bd - today).days
            return days, next_bd

        ordered = sorted(beneficiarios, key=lambda b: next_birthday_info(b)[0])
        proximos = []
        for b in ordered[:5]:
            days, next_bd = next_birthday_info(b)
            proximos.append({
                "id": b.id,
                "nombre_completo": f"{b.nombres} {b.apellidos}",
                "edad": b.edad,
                "fecha_nacimiento": b.fecha_nacimiento,
                "proximo_cumple": next_bd,
                "dias": days,
            })
        return await render_template(
            "dashboard.html",
            proximos_cumpleanos=proximos,
            total_beneficiarios=total_beneficiarios,
            total_hombres=total_hombres,
            total_mujeres=total_mujeres,
            total_usuarios=total_usuarios,
            total_visitantes=total_visitantes,
            total_usuarios_hombres=total_usuarios_hombres,
            total_usuarios_mujeres=total_usuarios_mujeres,
            total_visitantes_hombres=total_visitantes_hombres,
            total_visitantes_mujeres=total_visitantes_mujeres,
        )
