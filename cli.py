"""Punto de entrada.

Uso:
    python cli.py            corre los pipelines
    python cli.py --reset    recrea el esquema
"""
import sys

from db.conexion import reset_tablas
from pipelines import (
    pipeline_asesores,
    pipeline_catalogo,
    pipeline_conversaciones,
    pipeline_historico,
    pipeline_leads,
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
        f"\nListo: {leads} leads, {asesores} asesores, {catalogo} motos, "
        f"{disponibilidad} disponibilidades, {historico} cierres, "
        f"{conversaciones} conversaciones."
    )
