# app/utils/red.py


def extraer_ip(request) -> str | None:
    """Extrae la IP real del cliente respetando proxies (X-Forwarded-For)."""
    ip = request.headers.get("X-Forwarded-For", "") or request.remote_addr or ""
    ip = ip.split(",")[0].strip()
    if not ip or ip in ("127.0.0.1", "::1", ""):
        return None
    return ip
