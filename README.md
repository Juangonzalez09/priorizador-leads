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

## Despliegue

La aplicación está desplegada en un VPS gestionado con **Dokploy**. Corren dos
contenedores separados dentro del mismo proyecto: uno con **PostgreSQL** (la
base de datos) y otro construido a partir del `Dockerfile` de este repo, que
contiene **todo el código Python** (ETL, IA, scoring y el dashboard Flask). Se
comunican por red interna de Docker, no por IP pública. Cada push a `main`
puede reconstruir esa imagen desde Dokploy.

Dentro de ese mismo contenedor de la app corren dos cosas distintas, sin que
una dependa de que la otra esté activa en ese momento:

- **gunicorn** sirve el dashboard Flask de forma continua (`app.py`), atendiendo
  las peticiones de los usuarios.
- El **cron programado en Dokploy** dispara, una vez al día, el comando
  `python cli.py --ia` dentro de ese mismo contenedor: corre la ETL, la
  extracción con IA y el scoring, y deja los resultados en la base de datos.
  El dashboard simplemente lee lo que esa corrida dejó, la próxima vez que
  alguien entra a la página.

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
- [x] Publicación en URL pública (Dokploy)

## Decisiones y supuestos

- **Decidí deduplicar por teléfono + empresa, no solo por teléfono**, porque me di
  cuenta de que el mismo número aparecía en más de una empresa del grupo, y ahí no
  son el mismo cliente para efectos de este ejercicio: cada empresa debe seguir
  viendo solo lo suyo. Cuando sí es un duplicado real dentro de la misma empresa, me
  quedo con el registro que llegó por WhatsApp o el que tiene el estado de gestión
  más avanzado, y marco los demás como duplicados en vez de borrarlos, por si en
  algún momento hay que auditar de dónde salió cada uno.
- **Dejé las conversaciones guardadas como texto plano** en vez de forzarlas a una
  tabla con columnas fijas, porque lo que se habla por WhatsApp no tiene una
  estructura que se pueda anticipar de antemano. Lo que sí tiene forma (intención del
  cliente, presupuesto, si pidió cita, etc.) se lo pido a la IA y ese resultado sí
  queda en una tabla aparte, `extraccion_ia`.
- **Usé la IA únicamente para leer las conversaciones**, y dejé todo lo demás
  (normalizar teléfonos y fechas, detectar duplicados, calcular el score) como código
  normal. Me pareció que meter IA en pasos donde una regla simple ya resuelve el
  problema solo agrega riesgo y complejidad sin necesidad; prefiero usarla donde de
  verdad hace algo que el código no podría, que es entender texto libre.

- **Tomé la decisión de armar el scoring como un scorecard de reglas** (puntos por
  señal) desde el inicio del proyecto, en vez de entrenar un modelo de machine
  learning desde cero. Con ~2.200 registros de histórico no me pareció suficiente
  dato para entrenar algo confiable, y un scorecard me permite explicar exactamente
  por qué un lead quedó con score alto (pidió cita, mostró intención alta, mencionó
  cuota inicial, etc.), en vez de una caja negra que ni yo podría defender en la
  sustentación. Los pesos de cada señal los calibré comparando la tasa de cierre real
  del histórico contra cada regla, y validé el resultado contra ese mismo histórico
  antes de darlo por bueno.
- **Supuesto sobre "empresa" del dashboard**: sin login implementado, el filtro de
  empresa se pasa por parámetro en la URL en vez de autenticación real, para poder
  demostrar el aislamiento en la demo.

## Con más tiempo

Si tuviera más tiempo para seguir puliendo esto, lo primero sería reemplazar el
filtro por parámetro con un login real por empresa y por asesor, porque hoy cualquiera
que sepa el nombre de la empresa en la URL puede verla, y eso no es un aislamiento de
verdad, solo la demostración de que el filtro funciona.

También me gustaría guardar embeddings de las conversaciones y no solo los campos que
extrae la IA hoy, para poder buscar leads con conversaciones parecidas entre sí (por
ejemplo, "clientes que dudaron por precio de forma similar a este"), algo que un campo
de texto suelto o unos campos estructurados no permiten hacer bien.

Cambiaría también la forma en que actualizo el esquema de la base: hoy borro y recreo
las tablas cada vez que cambio algo, lo cual funciona para esta prueba pero sería
inaceptable con datos reales de producción; usaría algo adicional para hacer migraciones de
verdad, que solo alteran lo que cambió.

Y por último, hoy el sistema entrega una lista priorizada pero no reparte esos leads
entre los asesores; el siguiente paso lógico sería asignarlos automáticamente
respetando cuántos puede atender cada uno al día.
