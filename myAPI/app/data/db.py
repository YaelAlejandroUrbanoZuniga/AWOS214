from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, decñarative_base
import os


#1. DEFINIR LA URL DE LA BD
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://admin:123456@postgres:5434/DB_miapi"
)

#2. CREAMOS EL MOTOR DE LA CONEXIÓN
engine = create_engine(DATABASE_URL)

#3. CREAMOS GESTIONADOR DE SESIONES
SessionLocal = sessionmaker(
    autocommit = False,
    autoflush = False,
    bind = engine
)
