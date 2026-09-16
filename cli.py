"""Punto de entrada del pipeline."""
from pipelines.pipeline_leads import ejecutar

if __name__ == "__main__":
    total = ejecutar()
    print(f"\nListo: {total} leads ingestados en la tabla 'lead'.")
