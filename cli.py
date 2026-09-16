"""Punto de entrada del pipeline."""
from pipelines import (
    pipeline_asesores,
    pipeline_catalogo,
    pipeline_historico,
    pipeline_leads,
)

if __name__ == "__main__":
    leads = pipeline_leads.ejecutar()
    asesores = pipeline_asesores.ejecutar()
    catalogo, disponibilidad = pipeline_catalogo.ejecutar()
    historico = pipeline_historico.ejecutar()
    print(
        f"\nListo: {leads} leads, {asesores} asesores, {catalogo} motos, "
        f"{disponibilidad} disponibilidades, {historico} cierres históricos."
    )
