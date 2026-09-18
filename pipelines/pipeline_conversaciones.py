"""Pipeline de conversaciones: extract -> transform -> load."""
from etl.extract import extraer_conversaciones
from etl.load import cargar_conversaciones
from etl.transform import transformar_conversaciones
from src.logger import obtener_logger

log = obtener_logger("pipeline_conversaciones")


def ejecutar():
    log.info("Extract: leyendo conversaciones.json ...")
    crudo = extraer_conversaciones()
    log.info("  %d conversaciones leidas", len(crudo))

    log.info("Transform: aplanando a texto ...")
    limpio = transformar_conversaciones(crudo)

    log.info("Load: guardando en la tabla 'conversacion' ...")
    n = cargar_conversaciones(limpio)
    log.info("  %d conversaciones ingestadas", n)
    return n
