# app/services/configuracion_service.py

from sqlmodel import select

from app.models.roles import Rol, Permiso, RolPermiso, RolUsuario
from app.models.usuario import Usuario


_ROLES_BASE = [
    ("administrador", "Acceso total al sistema"),
    ("general", "Acceso restringido de lectura"),
]

_PERMISOS_BASE = [
    ("me.perfil", "perfil", "Ver propio perfil"),
    ("usuarios.listar", "usuarios", "Ver lista de usuarios"),
]


async def sembrar_roles(db) -> dict[str, Rol]:
    result = await db.execute(select(Rol))
    existentes = {r.name: r for r in result.scalars().all()}

    for name, description in _ROLES_BASE:
        if name not in existentes:
            rol = Rol(name=name, description=description)
            db.add(rol)
            existentes[name] = rol

    await db.flush()
    return existentes


async def sembrar_permisos(db, roles: dict[str, Rol]) -> None:
    result = await db.execute(select(Permiso))
    existentes = {p.slug: p for p in result.scalars().all()}

    nuevos: list[Permiso] = []
    for slug, module, description in _PERMISOS_BASE:
        if slug not in existentes:
            p = Permiso(slug=slug, module=module, description=description)
            db.add(p)
            nuevos.append(p)
            existentes[slug] = p

    if nuevos:
        await db.flush()

    rol_general = roles.get("general")
    if rol_general and rol_general.id:
        for slug, _, _ in _PERMISOS_BASE:
            permiso = existentes.get(slug)
            if permiso and permiso.id:
                check = await db.execute(
                    select(RolPermiso).where(
                        RolPermiso.rol_id == rol_general.id,
                        RolPermiso.permiso_id == permiso.id,
                    )
                )
                if not check.first():
                    db.add(RolPermiso(rol_id=rol_general.id, permiso_id=permiso.id))


async def crear_admin(
    db,
    username: str,
    email: str,
    password: str,
    nombres: str,
    apellidos: str,
) -> Usuario:
    """Crea el primer usuario administrador. Llamar solo cuando no hay usuarios."""
    roles = await sembrar_roles(db)
    await sembrar_permisos(db, roles)

    rol_admin = roles.get("administrador")

    usuario = Usuario(
        username=username,
        email=email,
        nombres=nombres,
        apellidos=apellidos,
    )
    usuario.set_password(password)
    db.add(usuario)
    await db.flush()

    if rol_admin and rol_admin.id:
        db.add(RolUsuario(usuario_id=usuario.id, role_id=rol_admin.id))

    return usuario
