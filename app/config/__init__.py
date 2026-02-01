# app/config/__init__.py

from app.config.auth import generate_token
from app.config.config import config
from app.config.configuracion_inicial import configuracion_inicial
from app.config.database import init_db, engine, get_session
from app.config.setup_app import setup_app

config_registry = {
    "generate_token": generate_token,
    "config": config,
    "configuracion_inicial": configuracion_inicial,
    "init_db": init_db,
    "engine": engine,
    "get_session": get_session,
    "setup_app": setup_app,
}
