# app/config/auth.py

import jwt
from datetime import datetime, timedelta, timezone
from app.config.config import config

def generate_token(usuario_id: int):
    """Genera un token JWT usando la zona horaria UTC actual."""
    payload = {
        # Expira en el tiempo configurado 
        "exp": datetime.now(timezone.utc) + timedelta(minutes=config.JWT_EXPIRATION_MINUTES),
        "iat": datetime.now(timezone.utc),
        "sub": str(usuario_id)
    }
    return jwt.encode(payload, config.SECRET_KEY, algorithm=config.JWT_ALGORITHM)