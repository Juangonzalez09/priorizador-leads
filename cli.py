"""Punto de entrada del pipeline."""
from pipelines import pipeline_asesores, pipeline_leads

if __name__ == "__main__":
    leads = pipeline_leads.ejecutar()
    asesores = pipeline_asesores.ejecutar()
    print(f"\nListo: {leads} leads y {asesores} asesores ingestados.")
