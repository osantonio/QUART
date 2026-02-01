# app/routes/permisos.py

from quart import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from app.config.database import get_session
from app.utils.auth import permission_required
from app.models.roles import Permiso
from sqlmodel import select, delete

permisos_bp = Blueprint("permisos", __name__, url_prefix="/usuarios/permisos")

@permisos_bp.route("/")
@permission_required
async def listar():
    """Vista informativa de la lista de permisos."""
    async for db_session in get_session():
        stmt = select(Permiso).order_by(Permiso.module, Permiso.slug)
        permisos_list = (await db_session.execute(stmt)).scalars().all()
        return await render_template("permisos/listar.html", permisos=permisos_list)

@permisos_bp.route("/crear", methods=["GET", "POST"])
@permission_required
async def crear():
    """Formulario para crear un nuevo permiso."""
    if request.method == "POST":
        form = await request.form
        slug = form.get("slug")
        module = form.get("module")
        description = form.get("description")
        
        from app.utils.auth import get_current_user
        current_user = await get_current_user()
        
        async for db_session in get_session():
            new_perm = Permiso(
                slug=slug, 
                module=module, 
                description=description,
                creado_por=current_user.id if current_user else None
            )

            db_session.add(new_perm)
            await db_session.commit()
            await flash(f"Permiso '{slug}' creado con éxito", "success")
            return redirect(url_for("permisos.listar"))

            
    return await render_template("permisos/crear.html")

@permisos_bp.route("/editar/<int:id>", methods=["GET", "POST"])
@permission_required
async def editar(id):
    """Formulario para editar un permiso existente."""
    async for db_session in get_session():
        stmt = select(Permiso).where(Permiso.id == id)
        permiso = (await db_session.execute(stmt)).scalar_one_or_none()
        
        if not permiso:
            await flash("Permiso no encontrado", "danger")
            return redirect(url_for("permisos.listar"))
            
        if request.method == "POST":
            form = await request.form
            permiso.slug = form.get("slug")
            permiso.module = form.get("module")
            permiso.description = form.get("description")
            
            db_session.add(permiso)
            await db_session.commit()
            await flash(f"Permiso '{permiso.slug}' actualizado", "success")
            return redirect(url_for("permisos.listar"))
            
        return await render_template("permisos/editar.html", permiso=permiso)

@permisos_bp.route("/eliminar/<int:id>", methods=["POST"])
@permission_required
async def eliminar(id):
    """Elimina un permiso."""
    async for db_session in get_session():
        stmt = delete(Permiso).where(Permiso.id == id)
        await db_session.execute(stmt)
        await db_session.commit()
        await flash("Permiso eliminado correctamente", "success")
        return redirect(url_for("permisos.listar"))
