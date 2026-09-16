"""Extracción de los archivos fuente."""
from pathlib import Path

import pandas as pd

CARPETA_RAW = Path(__file__).resolve().parent.parent / "data" / "raw"


def extraer_leads(carpeta=CARPETA_RAW):
    """Lee leads.csv sin conversiones, preservando los valores originales."""
    ruta = Path(carpeta) / "leads.csv"
    return pd.read_csv(ruta, dtype=str, keep_default_na=False, encoding="utf-8-sig")
