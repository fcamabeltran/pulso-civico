# Contributing to Pulso Cívico

Gracias por interesarte en mejorar el proyecto.

## Scope

Pulso Cívico es una plataforma de voto informado orientada a:

- claridad editorial neutral;
- evidencia verificable;
- uso responsable de IA sobre datos públicos;
- experiencia de usuario comprensible para ciudadanía general.

## Before Opening a PR

1. Revisa si el cambio mejora comprensión, trazabilidad o confiabilidad.
2. Evita introducir rankings, scores morales o lenguaje editorial sesgado.
3. Mantén consistencia entre frontend, backend y fuentes documentales.

## Development Setup

### Docker

```bash
docker compose up --build
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Coding Guidelines

- Mantén cambios pequeños, específicos y fáciles de revisar.
- No mezcles refactors amplios con cambios funcionales no relacionados.
- Prioriza claridad sobre cleverness.
- Si tocas respuestas o resúmenes IA, explica el criterio editorial y la trazabilidad.
- Si tocas ingestión de datos, documenta el origen y la estructura resultante.

## Pull Requests

Incluye en tu PR:

- objetivo del cambio;
- contexto funcional;
- archivos principales modificados;
- riesgos o tradeoffs;
- screenshots o GIFs si hay cambios de UI.

## Issues

Son especialmente útiles issues de:

- errores en recuperación RAG;
- inconsistencias entre datos oficiales y vista pública;
- mejoras de UX en comparación, asistente o fichas;
- problemas de documentación o setup local.

## Editorial Guardrails

No deben introducirse:

- recomendaciones de voto;
- puntajes agregados de candidatos;
- etiquetas moralizantes tipo "bueno" o "malo";
- colores o patrones visuales que sugieran ganador/perdedor.

## Questions

Si vas a proponer una mejora grande de producto o arquitectura, abre primero un issue con contexto y alcance.
