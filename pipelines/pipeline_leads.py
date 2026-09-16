"""Pipeline de leads: extract -> transform -> validación -> load."""
from etl.extract import extraer_leads
from etl.load import cargar_leads
from etl.transform import transformar_leads
from src.logger import obtener_logger
from src.validacion import validar_leads

log = obtener_logger("pipeline_leads")


def ejecutar():
    log.info("Extract: leyendo leads.csv ...")
    crudo = extraer_leads()
    log.info("  %d filas leidas", len(crudo))

    log.info("Transform: limpiando y normalizando ...")
    limpio = transformar_leads(crudo)

    log.info("Validación: descartando leads sin contacto ...")
    valido = validar_leads(limpio)
    log.info("  %d descartados, %d válidos", len(limpio) - len(valido), len(valido))

    log.info("Load: guardando en la tabla 'lead' ...")
    n = cargar_leads(valido)
    log.info("  %d leads ingestados", n)
    return n
