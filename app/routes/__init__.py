# app/routes/__init__.py

from app.routes.auth import auth_bp
from app.routes.main import bp as main_bp
from app.routes.usuarios import usuarios_bp
from app.routes.me import me_bp
from app.routes.roles import roles_bp
from app.routes.permisos import permisos_bp


routes = [auth_bp, main_bp, usuarios_bp, me_bp, roles_bp, permisos_bp]

