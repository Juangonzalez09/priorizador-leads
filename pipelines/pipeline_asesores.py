"""Pipeline de asesores: extract -> transform -> load."""
from etl.extract import extraer_asesores
from etl.load import cargar_asesores
from etl.transform import transformar_asesores
from src.logger import obtener_logger

log = obtener_logger("pipeline_asesores")


def ejecutar():
    log.info("Extract: leyendo asesores.csv ...")
    crudo = extraer_asesores()
    log.info("  %d filas leidas", len(crudo))

    log.info("Transform: normalizando ...")
    limpio = transformar_asesores(crudo)

    log.info("Load: guardando en la tabla 'asesor' ...")
    n = cargar_asesores(limpio)
    log.info("  %d asesores ingestados", n)
    return n
