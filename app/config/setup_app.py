
import logging
from datetime import datetime
from quart import Quart
from app.config.database import init_db, engine
from quart import g
from app.utils.auth import get_current_user, has_permission, es_admin, tiene_rol, tiene_acceso
from app.utils.csrf import aplicar_csrf_middleware, csrf_token
from quart import render_template
from app.config.formato_fecha import formato_fecha, formato_fecha_hora, formato_hora

logger = logging.getLogger(__name__)


def setup_app(app: Quart) -> None:

    app.jinja_env.filters["formato_fecha"] = formato_fecha
    app.jinja_env.filters["formato_fecha_hora"] = formato_fecha_hora
    app.jinja_env.filters["formato_hora"] = formato_hora

    aplicar_csrf_middleware(app)

    # Global disponible en macros y templates (context_processor no llega a macros)
    app.jinja_env.globals["csrf_token"] = csrf_token

    @app.before_request
    async def _cargar_usuario():
        g.current_user = await get_current_user()

    @app.context_processor
    def inject_template_globals():
        return {
            "now": datetime.now,
            "current_year": datetime.now().year,
            "current_user": g.get("current_user"),
            "has_permission": has_permission,
            "tiene_permiso": has_permission,
            "es_admin": es_admin,
            "tiene_rol": tiene_rol,
            "tiene_acceso": tiene_acceso,
            "csrf_token": csrf_token,
        }

    @app.errorhandler(Exception)
    async def handle_exception(e):
        logger.exception("Excepción no manejada: %s", e)
        return await render_template("errors/500.html"), 500

    @app.errorhandler(404)
    async def page_not_found(e):
        return await render_template("errors/404.html"), 404

    @app.errorhandler(500)
    async def internal_server_error(e):
        return await render_template("errors/500.html"), 500

    @app.while_serving
    async def startup():
        await init_db()
        yield
        await engine.dispose()
