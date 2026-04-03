# Plan de Desarrollo — Pulso Cívico
**Basado en PROPUESTA_IA_PULSO_CIVICO.md · Fecha: 2026-04-03**

---

## Estado actual del proyecto

| Módulo | Tecnología | Estado |
|--------|-----------|--------|
| Backend API | FastAPI + Python | ✅ Activo |
| Base de datos | PostgreSQL (Docker) | ✅ Activo |
| Vector store | ChromaDB | ✅ Indexado |
| RAG | LangChain + Groq/OpenAI | ✅ Funcional |
| Frontend | Next.js 15 + React 19 | ✅ Activo |
| Docker | docker-compose | ✅ Configurado |

---

## FASE 1 — Completada ✅ (3 de abril 2026)

| # | Tarea | Archivo(s) | Estado |
|---|-------|-----------|--------|
| 1 | **System Prompt completo** con etiquetas EVIDENCIA / AUSENCIA / INFERENCIA | `backend/app/ai/prompts.py` | ✅ |
| 2 | **Detección de vacío** — campo `evidence_found` en ChatResponse | `backend/app/schemas/chat.py`, `backend/app/services/ai_service.py` | ✅ |
| 3 | **Endpoint POST /simplify** — "Explícame fácil" backend | `backend/app/routes/ai_assistant.py`, `backend/app/ai/providers.py` | ✅ |
| 4 | **Preguntas sugeridas** — 8 grupos temáticos, 24 preguntas como chips | `frontend/components/AssistantPanel.tsx` | ✅ |
| 5 | **Botón "Explícame fácil"** — llama a /simplify, muestra panel colapsable | `frontend/components/AssistantPanel.tsx`, `frontend/lib/api.ts` | ✅ |
| 6 | **Badge [AUSENCIA DE EVIDENCIA]** en CompareBuilder | `frontend/components/CompareBuilder.tsx` | ✅ |
| 7 | **Tipos TypeScript** actualizados | `frontend/lib/types.ts` | ✅ |
| 8 | **CSS** para todos los componentes nuevos | `frontend/app/globals.css` | ✅ |

### Detalles técnicos de lo implementado

#### Backend: System Prompt (`prompts.py`)
- Sistema de 3 etiquetas: `[EVIDENCIA DOCUMENTAL]`, `[AUSENCIA DE EVIDENCIA]`, `[INFERENCIA]`
- 5 reglas absolutas + 5 reglas de calidad + 5 de tono
- Prompt separado `SIMPLIFY_PROMPT` para el endpoint de simplificación
- Temperatura 0 para respuestas (reproducibilidad), 0.3 para simplificación (fluidez)

#### Backend: `ai_service.py`
- `answer_question()`: retorna `evidence_found=False` cuando chunks vacíos o LLM devuelve string vacío
- `simplify_text()`: nuevo servicio que llama al método `simplify()` del provider
- Mensaje estándar de ausencia: incluye instrucción de verificar en JNE directamente

#### Backend: `providers.py`
- Método abstracto `simplify()` en `LLMProvider`
- Implementación en `GroqLLMProvider`, `OpenAILLMProvider`, `MockLLMProvider`
- Mock retorna los primeros 600 chars + disclaimer

#### Backend: `ai_assistant.py`
- Nuevo endpoint `POST /simplify` → `SimplifyResponse`

#### Backend: `schemas/chat.py`
- `ChatResponse` + campo `evidence_found: bool = True`
- Nuevos schemas: `SimplifyRequest`, `SimplifyResponse`

#### Frontend: `AssistantPanel.tsx`
- 8 grupos de preguntas sugeridas (Seguridad, Salud, Educación, Economía, Corrupción, Trayectoria, Viabilidad, Comparación)
- Dropdown por grupo → chips clickeables que rellenan el textarea
- Disclaimer mejorado al tope del panel
- Badge amarillo `[AUSENCIA DE EVIDENCIA]` cuando `evidence_found === false`
- Botón "💡 Explícame fácil" que llama a `/simplify` y muestra panel colapsable
- Etiqueta "Fuentes consultadas" antes del listado de sources

#### Frontend: `CompareBuilder.tsx`
- Badge `[AUSENCIA DE EVIDENCIA]` en lugar del texto genérico "Sin propuesta cargada para este eje"

---

## FASE 2 — Pendiente (post 13 de abril 2026)

| # | Función | Descripción técnica | Complejidad |
|---|---------|---------------------|-------------|
| 1 | **Radar de fortalezas** | Spider chart con 8 dimensiones. Pipeline de scoring binario (propuesta con indicador / total propuestas). Frontend: recharts o chart.js | Alta |
| 2 | **Comparación por IA** | Endpoint `GET /compare/ai?c1=&c2=&topic=` que usa RAG + prompt estructurado para comparar simétricamente por tema | Media |
| 3 | **Checklist ciudadano** | Flujo guiado de 5-7 preguntas reflexivas. Al final dispara consultas RAG según vacíos declarados | Media |
| 4 | **Resumen por región** | Metadato `region` en chunks del RAG. Selector de departamento en UI → filtra propuestas relevantes | Media |
| 5 | **Detector de propuestas vagas** | Clasificación binaria por propuesta (tiene indicador / no tiene). Pipeline LLM + tabla `proposal_clarity` en DB | Media |
| 6 | **Analytics de uso** | Logging anónimo de preguntas frecuentes para mejorar los suggested groups | Baja |

---

## FASE 3 — Versión futura (post-electoral)

| Función | Descripción |
|---------|-------------|
| Monitor de promesas | Seguimiento de lo prometido vs. lo ejecutado |
| Mapa geográfico de compromisos | Geolocalización de propuestas vs. proyectos reales |
| Integración SIAF/INFOBRAS | Datos abiertos del Estado para contraste |
| API pública | Exportación de datos para periodistas e investigadores |
| Comparación histórica 2021 vs 2026 | ¿Qué prometió antes? ¿Qué cumplió? |

---

## Instrucciones de arranque

```bash
# Levantar todo
docker-compose up -d

# Backend solo
docker-compose up -d api

# Frontend solo
docker-compose up -d web

# Ver logs del asistente
docker-compose logs -f api
```

## Variables de entorno clave (`backend/.env`)

```
LLM_PROVIDER=groq          # groq | openai | mock
GROQ_API_KEY=...
GROQ_MODEL=llama3-70b-8192
RAG_TOP_K=5
```

---

## Archivos modificados en Fase 1

```
backend/
  app/ai/prompts.py           ← System prompt completo + SIMPLIFY_PROMPT
  app/ai/providers.py         ← Método simplify() en todos los providers
  app/services/ai_service.py  ← evidence_found + simplify_text()
  app/routes/ai_assistant.py  ← POST /simplify endpoint
  app/schemas/chat.py         ← evidence_found + SimplifyRequest/Response

frontend/
  components/AssistantPanel.tsx  ← Chips + Explícame fácil + badges
  components/CompareBuilder.tsx  ← Badge AUSENCIA DE EVIDENCIA
  lib/api.ts                     ← simplifyText()
  lib/types.ts                   ← SimplifyResponse + evidence_found
  app/globals.css                ← ~170 líneas CSS nuevas
```
