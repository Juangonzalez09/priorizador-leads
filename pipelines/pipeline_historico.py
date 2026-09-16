"""Pipeline de historico: extract -> transform -> load."""
from etl.extract import extraer_historico
from etl.load import cargar_historico
from etl.transform import transformar_historico
from src.logger import obtener_logger

log = obtener_logger("pipeline_historico")


def ejecutar():
    log.info("Extract: leyendo historico_cierres.csv ...")
    crudo = extraer_historico()
    log.info("  %d filas leidas", len(crudo))

    log.info("Transform: normalizando ...")
    limpio = transformar_historico(crudo)

    log.info("Load: guardando en la tabla 'historico_cierre' ...")
    n = cargar_historico(limpio)
    log.info("  %d cierres ingestados", n)
    return n
