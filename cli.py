"""Punto de entrada del pipeline."""
from pipelines import pipeline_asesores, pipeline_catalogo, pipeline_leads

if __name__ == "__main__":
    leads = pipeline_leads.ejecutar()
    asesores = pipeline_asesores.ejecutar()
    catalogo, disponibilidad = pipeline_catalogo.ejecutar()
    print(
        f"\nListo: {leads} leads, {asesores} asesores, "
        f"{catalogo} motos, {disponibilidad} disponibilidades."
    )
