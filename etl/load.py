"""Carga de datos en la base de datos."""
import pandas as pd

from db.conexion import Session, crear_tablas
from db.modelos import Asesor, CatalogoMoto, Disponibilidad, Lead


def _cargar(df_limpio, modelo, reemplazar=True):
    crear_tablas()

    # NaN/NaT de pandas -> None para que la base guarde NULL.
    df = df_limpio.astype(object).where(pd.notnull(df_limpio), None)
    registros = [modelo(**fila) for fila in df.to_dict(orient="records")]

    with Session() as s:
        if reemplazar:
            s.query(modelo).delete()
        s.add_all(registros)
        s.commit()
    return len(registros)


def cargar_leads(df_limpio):
    """Guarda los leads en la tabla lead, reemplazando el contenido previo."""
    return _cargar(df_limpio, Lead)


def cargar_asesores(df_limpio):
    """Guarda los asesores en la tabla asesor, reemplazando el contenido previo."""
    return _cargar(df_limpio, Asesor)


def cargar_catalogo(df_limpio):
    """Guarda el catalogo en la tabla catalogo_moto, reemplazando el previo."""
    return _cargar(df_limpio, CatalogoMoto)


def cargar_disponibilidad(df_limpio):
    """Guarda la disponibilidad en la tabla disponibilidad, reemplazando el previo."""
    return _cargar(df_limpio, Disponibilidad)
