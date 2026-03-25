from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

#1. DEFINIR LA URL DE LA BD
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://admin:123456@postgres:5432/DB_miapi"
)

#2. CREAMOS EL MOTOR DE LA CONEXIÓN
engine = create_engine(DATABASE_URL)

#3. CREAMOS GESTIONADOR DE SESIONES
SessionLocal = sessionmaker(
    autocommit = False,
    autoflush = False,
    bind = engine
)

#4. BASE DECLARATIVA PARA MODELOS
Base = declarative_base()

#5. FUNCIÓN PARA LA SESIÓN EN CADA PETICIÓN
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
