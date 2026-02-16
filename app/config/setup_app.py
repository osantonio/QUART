
from datetime import datetime, time as dtime
from quart import Quart
from app.config.database import init_db, engine
from app.utils.auth import has_permission, es_admin, tiene_rol, tiene_acceso
from quart import render_template
from app.config.formato_fecha import formato_fecha, formato_fecha_hora, formato_hora

def setup_app(app: Quart) -> None:

    app.jinja_env.filters["formato_fecha"] = formato_fecha
    app.jinja_env.filters["formato_fecha_hora"] = formato_fecha_hora
    app.jinja_env.filters["formato_hora"] = formato_hora

    @app.context_processor
    def inject_template_globals():
        return {
            "now": datetime.now,
            "current_year": datetime.now().year,
            "has_permission": has_permission,
            "tiene_permiso": has_permission,
            "es_admin": es_admin,
            "tiene_rol": tiene_rol,
            "tiene_acceso": tiene_acceso,
        }

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
