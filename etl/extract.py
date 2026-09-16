"""Extracción de los archivos fuente."""
from pathlib import Path

import pandas as pd

CARPETA_RAW = Path(__file__).resolve().parent.parent / "data" / "raw"


def _leer_csv(nombre):
    """Lee un CSV de data/raw sin conversiones, preservando los valores originales."""
    ruta = CARPETA_RAW / nombre
    return pd.read_csv(ruta, dtype=str, keep_default_na=False, encoding="utf-8-sig")


def extraer_leads():
    return _leer_csv("leads.csv")


def extraer_asesores():
    return _leer_csv("asesores.csv")


def extraer_catalogo():
    return _leer_csv("catalogo_motos.csv")
