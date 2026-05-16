# app/utils/rate_limit.py
"""Rate limiting basado en LoginIntento (registro persistente de intentos fallidos)."""

from datetime import datetime, timedelta

from sqlalchemy import func, or_, select

from app.models.login_intento import LoginIntento

VENTANA_MINUTOS = 15
MAX_INTENTOS = 5


async def intentos_recientes(db, ip: str | None, username_o_email: str) -> int:
    desde = datetime.now() - timedelta(minutes=VENTANA_MINUTOS)
    condiciones = [LoginIntento.username_o_email == username_o_email]
    if ip:
        condiciones.append(LoginIntento.ip == ip)

    stmt = (
        select(func.count())
        .select_from(LoginIntento)
        .where(LoginIntento.creado_en >= desde, or_(*condiciones))
    )
    return (await db.execute(stmt)).scalar_one()


async def login_bloqueado(db, ip: str | None, username_o_email: str) -> tuple[bool, int]:
    """Devuelve (bloqueado, segundos_restantes_aproximados)."""
    n = await intentos_recientes(db, ip, username_o_email)
    if n < MAX_INTENTOS:
        return False, 0

    desde = datetime.now() - timedelta(minutes=VENTANA_MINUTOS)
    stmt = (
        select(func.max(LoginIntento.creado_en))
        .where(
            LoginIntento.creado_en >= desde,
            or_(
                LoginIntento.username_o_email == username_o_email,
                LoginIntento.ip == ip,
            ),
        )
    )
    ultimo = (await db.execute(stmt)).scalar_one_or_none()
    if not ultimo:
        return False, 0

    libera_en = ultimo + timedelta(minutes=VENTANA_MINUTOS)
    restante = int((libera_en - datetime.now()).total_seconds())
    return True, max(restante, 0)


async def registrar_intento(db, ip: str | None, username_o_email: str, usuario_id: int | None = None) -> None:
    db.add(LoginIntento(
        usuario_id=usuario_id,
        username_o_email=username_o_email,
        ip=ip,
    ))
