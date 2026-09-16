"""Pipeline de catalogo: extract -> transform -> load (catalogo + disponibilidad)."""
from etl.extract import extraer_catalogo
from etl.load import cargar_catalogo, cargar_disponibilidad
from etl.transform import explotar_disponibilidad, transformar_catalogo
from src.logger import obtener_logger

log = obtener_logger("pipeline_catalogo")


def ejecutar():
    log.info("Extract: leyendo catalogo_motos.csv ...")
    crudo = extraer_catalogo()
    log.info("  %d filas leidas", len(crudo))

    log.info("Transform: normalizando catalogo y explotando disponibilidad ...")
    catalogo = transformar_catalogo(crudo)
    disponibilidad = explotar_disponibilidad(crudo)

    log.info("Load: guardando catalogo y disponibilidad ...")
    n_cat = cargar_catalogo(catalogo)
    n_disp = cargar_disponibilidad(disponibilidad)
    log.info("  %d motos, %d filas de disponibilidad", n_cat, n_disp)
    return n_cat, n_disp
