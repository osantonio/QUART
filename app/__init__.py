# app/__init__.py

from quart import Quart
from app.routes import routes
from app.config import config, setup_app



def create_app():
    app = Quart(__name__)
    app.secret_key = config.SECRET_KEY
    app.config["DEBUG"] = config.DEBUG
    setup_app(app)

    for route in routes:
        app.register_blueprint(route)

    return app
