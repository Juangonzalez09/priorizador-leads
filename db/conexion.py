"""Conexión a la base de datos y creación del esquema."""
import re

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from config.config import DATABASE_URL
from db.modelos import Base

engine = create_engine(DATABASE_URL, future=True)
Session = sessionmaker(bind=engine, future=True)


def crear_base_si_no_existe():
    """Crea la base de datos si no existe (solo Postgres)."""
    url = make_url(DATABASE_URL)
    nombre = url.database
    if not nombre or url.get_backend_name() != "postgresql":
        return

    if not re.fullmatch(r"[A-Za-z0-9_]+", nombre):
        raise ValueError(f"Nombre de base no válido: {nombre!r}")

    # CREATE DATABASE no admite transacción; requiere AUTOCOMMIT.
    servidor = create_engine(
        url.set(database="postgres"), future=True, isolation_level="AUTOCOMMIT"
    )
    with servidor.connect() as c:
        existe = c.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :n"), {"n": nombre}
        ).scalar()
        if not existe:
            c.execute(text(f'CREATE DATABASE "{nombre}"'))
    servidor.dispose()


def crear_tablas():
    """Crea la base y las tablas que falten."""
    crear_base_si_no_existe()
    Base.metadata.create_all(engine)


def reset_tablas():
    """Borra y recrea todas las tablas."""
    crear_base_si_no_existe()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
