"""Configuración de logging del pipeline."""
import logging


def obtener_logger(nombre):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)s  %(message)s",
    )
    return logging.getLogger(nombre)
