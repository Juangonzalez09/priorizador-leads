# Priorizador de Leads — Motos y Servicios de Colombia

Convierte leads crudos (WhatsApp, Meta Ads, formulario web) en una lista
priorizada por asesor, enriquecida con la información de las conversaciones.

Pipeline de datos con arquitectura Medallion (bronce → plata → oro) que
persiste en PostgreSQL usando SQLAlchemy.

## Requisitos

- Python 3.11 o superior
- PostgreSQL

## Puesta en marcha

Crear y activar el entorno virtual:

    python -m venv .venv
    .venv\Scripts\Activate.ps1        # PowerShell
    # source .venv/Scripts/activate   # Git Bash

Instalar dependencias:

    pip install -r requirements.txt

Configurar la conexión: copiar `.env.example` a `.env` y ajustar la URL.

    DATABASE_URL=postgresql+psycopg://USUARIO:CONTRASENA@localhost:5432/priorizador_dev

Ejecutar el pipeline:

    python cli.py

Crea la base y las tablas si no existen, lee las fuentes de `data/raw/`, las
limpia, valida y carga en la base. Para producción, ajustar `DATABASE_URL` con
la IP del servidor y volver a ejecutar.

## Estructura

Ordenada según el flujo de ejecución (de arriba hacia abajo):

    priorizador-leads/
    │
    ├── cli.py                    1. Punto de entrada (corre todos los pipelines)
    │
    ├── pipelines/                2. Un pipeline por fuente
    │   ├── pipeline_leads.py        extract → transform → validación → load
    │   └── pipeline_asesores.py     extract → transform → load
    │
    ├── etl/
    │   ├── extract.py            3. Lee los CSV de data/raw
    │   ├── transform.py          4. Limpia y normaliza (usa src/normalizacion)
    │   └── load.py               5. Carga en la base de datos (usa db/)
    │
    ├── src/
    │   ├── normalizacion.py         Reglas de limpieza (teléfono, fecha, ciudad)
    │   ├── validacion.py            Descarta registros no utilizables
    │   └── logger.py                Logging
    │
    ├── db/
    │   ├── modelos.py               Tablas declaradas con el ORM
    │   └── conexion.py              Conexión, creación de la base y las tablas
    │
    ├── config/
    │   └── config.py                Lee DATABASE_URL desde .env
    │
    └── data/
        └── raw/                     Archivos fuente (sintéticos)

## Estado

- [x] Ingesta, limpieza y validación de leads
- [x] Ingesta de asesores
- [ ] Otras fuentes (catálogo, histórico)
- [ ] Deduplicación
- [ ] Extracción con IA (conversaciones)
- [ ] Scoring y priorización
- [ ] Dashboard web
