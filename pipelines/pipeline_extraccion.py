"""Pipeline de extracción con IA: lee conversaciones y produce extraccion_ia."""
import hashlib
import time

from db.conexion import Session, crear_tablas
from db.modelos import Conversacion, ExtraccionIA
from ia.extraccion import extraer
from src.logger import obtener_logger

log = obtener_logger("pipeline_extraccion")


def _hash(texto):
    return hashlib.sha256((texto or "").encode("utf-8")).hexdigest()


def ejecutar(limite=None, pausa=4.0):
    crear_tablas()
    with Session() as s:
        conversaciones = s.query(Conversacion).all()
        hechos = {h for (h,) in s.query(ExtraccionIA.hash_texto).all()}
        pendientes = [c for c in conversaciones if _hash(c.texto) not in hechos]
        if limite:
            pendientes = pendientes[:limite]
        log.info("Extracción IA: %d conversaciones pendientes", len(pendientes))

        n = 0
        for c in pendientes:
            try:
                datos = extraer(c.texto)
            except Exception as e:
                log.warning("  falló %s: %s", c.conversacion_id, str(e)[:100])
                continue
            s.add(ExtraccionIA(
                conversacion_id=c.conversacion_id,
                lead_id_origen=c.lead_id_origen,
                hash_texto=_hash(c.texto),
                **datos.model_dump(),
            ))
            n += 1
            if n % 20 == 0:
                s.commit()
                log.info("  %d/%d", n, len(pendientes))
            time.sleep(pausa)
        s.commit()
    log.info("  %d extracciones nuevas", n)
    return n
