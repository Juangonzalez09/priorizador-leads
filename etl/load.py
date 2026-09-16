"""Carga de leads en la base de datos."""
import pandas as pd

from db.conexion import Session, crear_tablas
from db.modelos import Lead


def cargar_leads(df_limpio, reemplazar=True):
    """Guarda los leads en la tabla `lead`, reemplazando el contenido previo."""
    crear_tablas()

    # NaN/NaT de pandas -> None para que la base guarde NULL.
    df = df_limpio.astype(object).where(pd.notnull(df_limpio), None)
    registros = [Lead(**fila) for fila in df.to_dict(orient="records")]

    with Session() as s:
        if reemplazar:
            s.query(Lead).delete()
        s.add_all(registros)
        s.commit()
    return len(registros)
