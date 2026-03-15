# app/config/config.py

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    if not SECRET_KEY:
        raise ValueError("La variable de entorno SECRET_KEY debe estar configurada")
    DATABASE_URL = os.getenv("DATABASE_URL")
    DEBUG = os.getenv("DEBUG") == "True"
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
    JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "30"))
    
config = Config()
