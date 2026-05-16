# app/utils/csrf.py
"""Protección CSRF basada en token de sesión.

En plantillas:
    {% from "macros/csrf.html" import csrf_field %}
    <form method="post">{{ csrf_field() }} ...</form>

Para AJAX/HTMX: enviar header `X-CSRF-Token: {{ csrf_token() }}`.
"""
import hmac
import secrets
from functools import wraps

from quart import abort, request, session

_SESSION_KEY = "_csrf_token"
_FORM_FIELD = "_csrf_token"
_HEADER_NAME = "X-CSRF-Token"


def csrf_token() -> str:
    token = session.get(_SESSION_KEY)
    if not token:
        token = secrets.token_urlsafe(32)
        session[_SESSION_KEY] = token
    return token


async def _extraer_token() -> str | None:
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return None
    header = request.headers.get(_HEADER_NAME)
    if header:
        return header
    try:
        form = await request.form
        return form.get(_FORM_FIELD)
    except Exception:
        return None


async def validar_csrf() -> bool:
    enviado = await _extraer_token()
    esperado = session.get(_SESSION_KEY)
    if not enviado or not esperado:
        return False
    return hmac.compare_digest(enviado, esperado)


def requiere_csrf(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            if not await validar_csrf():
                abort(400, description="Token CSRF inválido o ausente.")
        return await func(*args, **kwargs)
    return wrapper


_PATHS_ENFORCED = (
    "/auth/",
    "/configuracion/",
    "/me/",
    "/usuarios/",
    "/roles/",
    "/permisos/",
    "/beneficiarios/",
    "/visitantes/",
    "/visitas/",
    "/farmacia/",
    "/parentescos/",
    "/signos-vitales/",
    "/admin/",
)

_PATHS_EXEMPT: tuple[str, ...] = ()


def _aplica_csrf(path: str) -> bool:
    if any(path.startswith(p) for p in _PATHS_EXEMPT):
        return False
    return any(path.startswith(p) for p in _PATHS_ENFORCED)


def aplicar_csrf_middleware(app) -> None:
    @app.before_request
    async def _csrf_check():
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return
        if not _aplica_csrf(request.path):
            return
        if not await validar_csrf():
            abort(400, description="Token CSRF inválido o ausente.")
