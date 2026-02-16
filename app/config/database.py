# app/config/database.py

from dotenv import load_dotenv
from sqlmodel import SQLModel
from app.config import config
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()
DATABASE_URL = config.DATABASE_URL

# Creamos el motor asíncrono con optimizaciones para evitar cierres de conexión
engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,      # Verifica la conexión antes de usarla
    pool_recycle=1800,       # Recicla conexiones cada 30 minutos
    connect_args={
        "command_timeout": 60,  # Tiempo máximo para una consulta
        "timeout": 60           # Tiempo máximo para conectar
    }
)

# Inicializamos el sessionmaker globalmente para evitar overhead en cada petición
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Generador de sesiones para las rutas
async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

# Función para crear las tablas al iniciar
async def init_db():
    # Importamos los modelos aquí para asegurar que estén registrados en SQLModel.metadata
    from app.models import models  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    # Configuración inicial de datos maestros
    from app.config import configuracion_inicial
    await configuracion_inicial(engine)
