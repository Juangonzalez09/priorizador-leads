"""Punto de entrada.

Uso:
    python cli.py            corre la ETL + scoring + asignación
    python cli.py --reset    recrea el esquema antes de la ETL
    python cli.py --ia       corre también la extracción con IA
"""
import sys

from db.conexion import reset_tablas
from pipelines import (
    pipeline_asesores,
    pipeline_asignacion,
    pipeline_catalogo,
    pipeline_conversaciones,
    pipeline_extraccion,
    pipeline_historico,
    pipeline_leads,
    pipeline_scoring,
)

if __name__ == "__main__":
    if "--reset" in sys.argv:
        reset_tablas()

    leads = pipeline_leads.ejecutar()
    asesores = pipeline_asesores.ejecutar()
    catalogo, disponibilidad = pipeline_catalogo.ejecutar()
    historico = pipeline_historico.ejecutar()
    conversaciones = pipeline_conversaciones.ejecutar()
    print(
        f"\nETL lista: {leads} leads, {asesores} asesores, {catalogo} motos, "
        f"{disponibilidad} disponibilidades, {historico} cierres, "
        f"{conversaciones} conversaciones."
    )

    if "--ia" in sys.argv:
        extracciones = pipeline_extraccion.ejecutar()
        print(f"IA: {extracciones} extracciones nuevas.")
    
    # Siempre ejecutar scoring (con o sin IA)
    scoring = pipeline_scoring.ejecutar(recalcular="--reset" in sys.argv)
    print(f"Scoring: {scoring} leads puntuados.")

    asignados = pipeline_asignacion.ejecutar()
    print(f"Asignación: {asignados} leads repartidos entre asesores.")
