# app/routes/main.py

from quart import Blueprint, render_template
from app.utils.auth import permission_required

bp = Blueprint("main", __name__)


@bp.route("/")
async def index():
    return await render_template("index.html")


@bp.route("/dashboard")
@permission_required
async def dashboard():
    return await render_template("dashboard.html")
