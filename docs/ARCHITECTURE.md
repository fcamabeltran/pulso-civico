# Architecture

## Product Surface

Pulso Cívico está compuesto por cuatro superficies principales:

- home orientada a descubrimiento rápido del producto;
- fichas y exploración de candidaturas/fórmulas;
- comparador guiado de candidaturas;
- asistente IA con evidencia y páginas.

## Core System

```text
Next.js frontend
  -> FastAPI backend
    -> PostgreSQL
    -> ChromaDB
    -> corpus local de planes y hojas de vida
    -> proveedor LLM (OpenAI / Groq)
```

## Backend Responsibilities

- exponer API para candidatos, fórmulas, comparación y chat;
- normalizar datos públicos del JNE;
- importar y estructurar hojas de vida;
- mantener propuestas y candidatos en PostgreSQL;
- recuperar chunks por tema y candidatura;
- generar respuestas IA con evidencia, vacíos e inferencias.

## Frontend Responsibilities

- presentar una experiencia de lectura guiada;
- hacer visible evidencia documental y páginas;
- permitir comparación sin sobrecarga cognitiva;
- mantener tono sobrio, neutral y orientado a voto informado.

## Data Sources

- planes de gobierno descargados localmente;
- archivos del JNE y derivados de Voto Informado;
- hojas de vida estructuradas por miembro de fórmula;
- corpus RAG indexado en ChromaDB.

## Retrieval Strategy

El asistente IA no depende solo de búsqueda vectorial libre.

El flujo actual combina:

1. resolución de candidato por alias oficiales e importados;
2. recuperación directa desde base de datos cuando aplica;
3. recuperación semántica en Chroma como apoyo;
4. filtrado temático;
5. respuesta estructurada con evidencia, vacíos e inferencias.

## Comparison Strategy

El comparador y el asistente comparativo priorizan:

- diferencias descriptivas por tema;
- ausencia de propuesta como dato visible;
- evidencia por candidato;
- neutralidad editorial;
- no usar ranking ni scoring agregado.

## Repo Documentation

- `README.md`: entrada principal para GitHub
- `docs/SHOWCASE.md`: assets visuales recomendados
- `backend/README.md`: detalles del backend
- `frontend/README.md`: detalles del frontend
