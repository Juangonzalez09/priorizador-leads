# Priorizador de Leads — Motos y Servicios de Colombia

Convierte leads crudos (WhatsApp, Meta Ads, formulario web) en una lista
priorizada por asesor, enriquecida con la información de las conversaciones.

Pipeline de datos con arquitectura Medallion (bronce → plata → oro) que
persiste en PostgreSQL usando SQLAlchemy.

## Arquitectura general

```
┌─────────────────────────────────────────────────────────────────┐
│  DATA/RAW (Bronce)                                              │
│  • leads.csv (1.503)                                            │
│  • conversaciones.json (677)                                    │
│  • catalogo_motos.csv (24)                                      │
│  • asesores.csv (42)                                            │
│  • historico_cierres.csv (2.200)                                │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  ETL (Extract → Transform → Load)                               │
│  • Normalización (teléfono, fecha, ciudad)                      │
│  • Validación (sin contacto → descarta)                         │
│  • Deduplicación (teléfono + empresa)                           │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  POSTGRESQL (Plata)                                             │
│  • lead (1.502 filas, 51 dedup marcados)                        │
│  • conversacion (677 textos crudos)                             │
│  • catalogo_moto, asesor, historico_cierre                      │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  IA (Google Gemini 3.6 Flash)                                   │
│  • Extracción: conversación → 8 campos estructurados            │
│  • Fuzzy matching: modelo_interes → SKU catálogo                │
│  • Output: extraccion_ia (con enriquecimiento)                  │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  SCORING (Scorecard calibrado)                                  │
│  • Reglas de negocio (pidió cita +30, intención alta +25, ...)  │
│  • Validado con histórico: Lift 1.62x en top 10%                │
│  • Output: scoring (score 0-100, temperatura)                   │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  DASHBOARD WEB (Oro)                                            │
│  • Flask app: lista ordenada por score                          │
│  • Filtro por empresa (respeta separación)                      │
│  • API REST (/api/lead/<id>, /api/stats)                        │
│  • URL: http://localhost:5000                                   │
└─────────────────────────────────────────────────────────────────┘
```

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
    GEMINI_API_KEY=tu_clave_api_aqui

Ejecutar el pipeline ETL:

    python cli.py

Crea la base y las tablas si no existen, lee las fuentes de `data/raw/`, las
limpia, valida y carga en la base. Para producción, ajustar `DATABASE_URL` con
la IP del servidor y volver a ejecutar.

Ejecutar con extracción de IA:

    python cli.py --ia

Procesa las conversaciones de WhatsApp con Gemini para extraer campos estructurados
(modelo, intención, objeciones, etc.) y enriquece con fuzzy matching al catálogo.

Levantar el dashboard web:

    python app.py

Abre `http://localhost:5000` en tu navegador para ver la lista priorizada de leads.

## Estructura

Ordenada según el flujo de ejecución (de arriba hacia abajo):

    priorizador-leads/
    │
    ├── cli.py                    1. Punto de entrada (corre todos los pipelines)
    ├── app.py                    2. Dashboard web (Flask)
    │
    ├── pipelines/                3. Un pipeline por fuente + scoring
    │   ├── pipeline_leads.py        extract → transform → validación → dedup → load
    │   ├── pipeline_asesores.py     extract → transform → load
    │   ├── pipeline_catalogo.py     extract → transform → load (catálogo + disponibilidad)
    │   ├── pipeline_historico.py    extract → transform → load
    │   ├── pipeline_conversaciones.py  extract → transform → load
    │   ├── pipeline_extraccion.py   IA: extrae campos de conversaciones
    │   └── pipeline_scoring.py      Calcula score y temperatura
    │
    ├── etl/
    │   ├── extract.py            4. Lee los CSV/JSON de data/raw
    │   ├── transform.py          5. Limpia, normaliza y explota (usa src/normalizacion)
    │   └── load.py               6. Carga en la base de datos (usa db/)
    │
    ├── ia/
    │   ├── extraccion.py            Extracción con Gemini + fuzzy matching
    │   ├── esquema.py               Schema Pydantic (structured output)
    │   └── fuzzy_matching.py        Mapea modelo_interes → SKU catálogo
    │
    ├── src/
    │   ├── normalizacion.py         Reglas de limpieza (teléfono, fecha, ciudad)
    │   ├── validacion.py            Descarta registros no utilizables
    │   ├── deduplicacion.py         Marca duplicados por teléfono+empresa
    │   └── logger.py                Logging
    │
    ├── db/
    │   ├── modelos.py               Tablas ORM (lead, asesor, catalogo_moto, scoring, ...)
    │   └── conexion.py              Conexión, creación de la base y las tablas
    │
    ├── config/
    │   └── config.py                Lee DATABASE_URL y GEMINI_API_KEY desde .env
    │
    ├── templates/
    │   └── index.html               Vista principal del dashboard
    │
    ├── tests/
    │   └── test_scoring.py          Validación del scoring vs histórico (lift, AUC)
    │
    └── data/
        └── raw/                     Archivos fuente (sintéticos)

## Estado

- [x] Ingesta, limpieza y validación de leads
- [x] Ingesta de asesores
- [x] Ingesta de catálogo (con disponibilidad normalizada)
- [x] Ingesta de histórico de cierres
- [x] Deduplicación (por teléfono + empresa)
- [x] Ingesta de conversaciones
- [x] Extracción con IA (conversaciones → campos estructurados)
- [x] Fuzzy matching (modelo_interes → SKU catálogo)
- [x] Scoring y priorización (scorecard calibrado vs histórico)
- [x] Validación de scoring (Lift 1.62x en top 10%)
- [x] Dashboard web (Flask + API REST)
- [ ] Publicación en URL pública
