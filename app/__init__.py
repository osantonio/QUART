# app/__init__.py

import logging
from quart import Quart
from app.routes import routes
from app.config import config, setup_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


def create_app():
    app = Quart(__name__)
    app.secret_key = config.SECRET_KEY
    app.config["DEBUG"] = config.DEBUG
    setup_app(app)

    for route in routes:
        app.register_blueprint(route)

    return app