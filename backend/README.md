# Pulso Civico Backend

Backend inicial para Pulso Civico con FastAPI, PostgreSQL, Chroma y flujo RAG.

## Modulos

- `candidates`: exploracion de candidatos y detalle completo
- `compare`: comparacion de propuestas entre dos candidatos
- `search`: busqueda textual simple en propuestas
- `ai_assistant`: endpoint de chat con RAG y proveedor LLM configurable
- `share`: generacion de imagen PNG para compartir comparaciones
- `scripts/ingest_data.py`: seed relacional + carga en Chroma

## Arranque con Docker

1. Copiar variables de entorno:

```bash
cp .env.example .env
```

2. Levantar servicios:

```bash
docker compose up --build -d
```

3. Cargar datos de ejemplo e indexar embeddings:

```bash
docker compose exec api python -m app.scripts.ingest_data
```

4. Abrir docs:

```bash
http://localhost:8000/docs
```

## Scraping recomendado

Para extraer fuentes del JNE o PDFs cargados manualmente, usa un flujo hibrido:

1. Edita [`data/source_manifest.json`](/Users/camex/telefonica-documents/tuku-projects/app-pulso-civico/backend/data/source_manifest.json)
2. Ejecuta:

```bash
docker compose exec api python -m app.scripts.scrape_sources
```

3. Revisa la salida en:

```bash
/app/data/raw_sources.json
```

El script intenta:

- leer listados estructurados del JNE
- extraer perfiles de hoja de vida
- descargar PDFs si activas `download_plan_documents`
- procesar PDFs locales que hayas subido a `data/uploads/`

Esto te deja un dataset `raw` con texto y metadatos de fuente, para luego normalizar propuestas y cargar PostgreSQL/Chroma con criterio editorial.

## Descarga desde LP Derecho

Si quieres aprovechar la recopilacion publicada por LP Derecho, puedes descargar los planes enlazados en su articulo y guardarlos por partido:

```bash
docker compose exec api python -m app.scripts.download_lp_plans
```

Salida:

```bash
/app/data/downloads/lp_plans/
```

Cada carpeta de partido incluye:

- el PDF del plan
- `metadata.json`

Ademas se genera un indice consolidado en:

```bash
/app/data/downloads/lp_plans/index.json
```

Cada entrada del indice incluye:

- `party_slug`
- `filename`
- `relative_pdf_path`

## Importar planes LP a PostgreSQL y Chroma

Si quieres que el asistente consulte directamente el corpus local de los 33 planes, importa los PDFs a la base y reindexa Chroma con este script:

```bash
docker compose exec api python -m app.scripts.import_lp_plans_to_rag
```

El proceso:

- valida que cada PDF exista
- extrae texto completo del plan
- crea un candidato y una propuesta por plan
- resetea y reconstruye la coleccion RAG en Chroma
- genera una auditoria de cobertura en `/app/data/downloads/lp_plans/corpus_status.json`

## Endpoints base

- `GET /health`
- `GET /api/candidates`
- `GET /api/candidate/{id}`
- `GET /api/compare?c1=1&c2=2`
- `GET /api/search?q=agua`
- `POST /api/chat`
- `GET /api/share-image?c1=1&c2=2`

## Proveedor de IA

- `LLM_PROVIDER=mock`: desarrollo sin credenciales
- `LLM_PROVIDER=groq`: usar `GROQ_API_KEY`
- `LLM_PROVIDER=openai`: usar `OPENAI_API_KEY`

## Nota de arquitectura

El asistente responde solo sobre contexto recuperado desde Chroma. La neutralidad se fuerza por prompt, por recuperacion basada en datos y por inclusion obligatoria de fuentes en la respuesta.

En este contenedor, si `sentence-transformers` no esta instalado, el sistema usa embeddings ligeros deterministas para mantener el MVP operativo sin dependencias pesadas de `torch`.
