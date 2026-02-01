# app/routes/roles.py

from quart import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from app.config.database import get_session
from app.utils.auth import permission_required
from app.models.roles import Rol, Permiso, RolPermiso, RolUsuario
from app.models.usuario import Usuario
from sqlmodel import select, delete
from sqlalchemy.orm import selectinload

roles_bp = Blueprint("roles", __name__, url_prefix="/usuarios/roles")

@roles_bp.route("/")
@permission_required
async def listar():
    """Lista todos los roles."""
    async for db_session in get_session():
        stmt = select(Rol).options(selectinload(Rol.usuarios))
        roles_list = (await db_session.execute(stmt)).scalars().all()
        return await render_template("roles/listar.html", roles=roles_list)

@roles_bp.route("/crear", methods=["GET", "POST"])
@permission_required
async def crear():
    """Crea un nuevo rol."""
    if request.method == "POST":
        form = await request.form
        name = form.get("name").lower()
        description = form.get("description")
        
        from app.utils.auth import get_current_user
        current_user = await get_current_user()
        
        async for db_session in get_session():
            new_rol = Rol(
                name=name, 
                description=description,
                creado_por=current_user.id if current_user else None
            )

            db_session.add(new_rol)
            await db_session.commit()
            await flash(f"Rol '{name}' creado con éxito", "success")
            return redirect(url_for("roles.listar"))

            
    return await render_template("roles/crear.html")

@roles_bp.route("/editar/<int:id>", methods=["GET", "POST"])
@permission_required
async def editar(id):
    """Matriz de selección de permisos para un rol específico."""
    async for db_session in get_session():
        # Obtener el rol
        stmt_rol = select(Rol).where(Rol.id == id)
        rol = (await db_session.execute(stmt_rol)).scalar_one_or_none()
        
        if not rol:
            await flash("Rol no encontrado", "danger")
            return redirect(url_for("roles.listar"))
            
        if request.method == "POST":
            # Guardado manual de permisos
            form = await request.form
            selected_perm_ids = form.getlist("permissions")
            selected_perm_ids = [int(pid) for pid in selected_perm_ids]
            
            # 1. Eliminar relaciones actuales
            stmt_del = delete(RolPermiso).where(RolPermiso.rol_id == id)
            await db_session.execute(stmt_del)
            
            # 2. Agregar nuevas relaciones
            for pid in selected_perm_ids:
                db_session.add(RolPermiso(rol_id=id, permiso_id=pid))
                
            await db_session.commit()
            await flash(f"Permisos del rol '{rol.name}' actualizados correctamente.", "success")
            return redirect(url_for("roles.listar"))
            
        # Obtener todos los permisos agrupados por módulo
        stmt_perms = select(Permiso).order_by(Permiso.module, Permiso.slug)
        permisos_list = (await db_session.execute(stmt_perms)).scalars().all()
        
        # Obtener IDs de permisos que ya tiene el rol
        stmt_mapping = select(Permiso.id).join(Permiso.roles).where(Rol.id == id)
        mapping = (await db_session.execute(stmt_mapping)).scalars().all()
        
        return await render_template(
            "roles/editar.html",
            rol=rol,
            permisos=permisos_list,
            mapping=mapping
        )


@roles_bp.route("/eliminar/<int:id>", methods=["POST"])
@permission_required
async def eliminar(id):
    """Elimina un rol, protegiendo 'administrador' y 'general'."""
    async for db_session in get_session():
        stmt_rol = select(Rol).where(Rol.id == id)
        rol = (await db_session.execute(stmt_rol)).scalar_one_or_none()
        
        if not rol:
            await flash("Rol no encontrado", "danger")
            return redirect(url_for("roles.listar"))
            
        if rol.name in ["administrador", "general"]:
            await flash(f"No se puede eliminar el rol vital '{rol.name}'", "warning")
            return redirect(url_for("roles.listar"))
            
        await db_session.delete(rol)
        await db_session.commit()
        await flash(f"Rol '{rol.name}' eliminado", "success")
        return redirect(url_for("roles.listar"))

@roles_bp.route("/asignar/<int:usuario_id>", methods=["GET", "POST"])
@permission_required
async def asignar_usuario(usuario_id):
    """Vista para gestionar los roles de un usuario."""
    async for db_session in get_session():
        stmt_user = select(Usuario).where(Usuario.id == usuario_id).options(selectinload(Usuario.roles))
        usuario = (await db_session.execute(stmt_user)).scalar_one_or_none()
        
        if not usuario:
            await flash("Usuario no encontrado", "danger")
            return redirect(url_for("usuarios.listar"))
            
        if request.method == "POST":
            # Guardado manual de roles
            form = await request.form
            selected_role_ids = form.getlist("roles")
            selected_role_ids = [int(rid) for rid in selected_role_ids]
            
            # 1. Eliminar relaciones actuales
            stmt_del = delete(RolUsuario).where(RolUsuario.usuario_id == usuario_id)
            await db_session.execute(stmt_del)
            
            # 2. Agregar nuevas relaciones
            for rid in selected_role_ids:
                db_session.add(RolUsuario(usuario_id=usuario_id, role_id=rid))
                
            await db_session.commit()
            await flash(f"Roles del usuario '{usuario.username}' actualizados correctamente.", "success")
            return redirect(url_for("usuarios.listar"))

        stmt_roles = select(Rol)
        roles_list = (await db_session.execute(stmt_roles)).scalars().all()
        
        # Mapeo de roles actuales del usuario
        user_role_ids = [r.id for r in usuario.roles]
        
        return await render_template(
            "roles/asignar_usuario.html",
            usuario=usuario,
            roles=roles_list,
            user_role_ids=user_role_ids
        )

