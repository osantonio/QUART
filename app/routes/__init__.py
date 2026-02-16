# app/routes/__init__.py

from app.routes.auth import auth_bp
from app.routes.main import bp as main_bp
from app.routes.usuarios import usuarios_bp
from app.routes.me import me_bp
from app.routes.roles import roles_bp
from app.routes.permisos import permisos_bp
from app.routes.beneficiarios import beneficiarios_bp
from app.routes.signos_vitales import signos_vitales_bp
from app.routes.imc import imc_bp
from app.routes.farmacia import farmacia_bp
from app.routes.visitantes import visitantes_bp
from app.routes.parentescos import parentescos_bp
from app.routes.historia_clinica import hclinica_bp


routes = [auth_bp, main_bp, usuarios_bp, me_bp, roles_bp, permisos_bp, beneficiarios_bp, signos_vitales_bp, imc_bp, farmacia_bp, visitantes_bp, parentescos_bp, hclinica_bp]
