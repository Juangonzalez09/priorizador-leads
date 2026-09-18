"""Pipeline de asignación: reparte los leads priorizados entre los asesores.

Por cada punto de venta, toma los asesores activos y les reparte los leads
(ya deduplicados y con score) en orden round-robin, respetando la capacidad
diaria de cada uno. Si un punto de venta no tiene asesores activos, sus leads
se reparten entre los asesores activos de la misma empresa.
"""
from datetime import datetime

from db.conexion import Session, crear_tablas
from db.modelos import Asesor, Asignacion, Lead, Scoring
from src.logger import obtener_logger

log = obtener_logger("pipeline_asignacion")


def ejecutar():
    """Recalcula la asignación del día para todas las empresas."""
    crear_tablas()

    with Session() as s:
        leads = s.query(Lead, Scoring.score).outerjoin(
            Scoring, Lead.lead_id_origen == Scoring.lead_id_origen
        ).filter(
            (Lead.es_duplicado == False) | (Lead.es_duplicado.is_(None))
        ).order_by(Scoring.score.desc().nulls_last()).all()

        asesores = s.query(Asesor).filter(Asesor.activo == True).all()

        s.query(Asignacion).delete()

        asesores_por_pv = {}
        asesores_por_empresa = {}
        for a in asesores:
            asesores_por_pv.setdefault(a.punto_venta_id, []).append(a)
            asesores_por_empresa.setdefault(a.empresa_id, []).append(a)

        # cupo restante por asesor (capacidad_diaria) y próximo turno (round-robin)
        cupo = {a.asesor_id_origen: (a.capacidad_diaria or 0) for a in asesores}
        turno = {}
        orden_asesor = {}

        n = 0
        for lead, _score in leads:
            candidatos = asesores_por_pv.get(lead.punto_venta_id) or asesores_por_empresa.get(lead.empresa_id) or []
            candidatos = [a for a in candidatos if cupo.get(a.asesor_id_origen, 0) > 0]
            if not candidatos:
                continue

            clave_turno = lead.punto_venta_id if asesores_por_pv.get(lead.punto_venta_id) else lead.empresa_id
            i = turno.get(clave_turno, 0) % len(candidatos)
            asesor = candidatos[i]
            turno[clave_turno] = i + 1

            cupo[asesor.asesor_id_origen] -= 1
            orden_asesor[asesor.asesor_id_origen] = orden_asesor.get(asesor.asesor_id_origen, 0) + 1
            n += 1

            s.add(Asignacion(
                lead_id_origen=lead.lead_id_origen,
                asesor_id_origen=asesor.asesor_id_origen,
                empresa_id=lead.empresa_id,
                punto_venta_id=lead.punto_venta_id,
                orden=orden_asesor[asesor.asesor_id_origen],
                fecha_asignacion=datetime.now(),
            ))

        s.commit()

    log.info("Asignación: %d leads repartidos entre asesores activos", n)
    return n
