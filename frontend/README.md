# Pulso Civico Frontend

Frontend inicial en Next.js App Router, alineado al prototipo HTML del proyecto.

## Vistas

- `/`: portada, destacados y asistente IA
- `/candidates`: exploracion de candidatos
- `/candidates/[id]`: ficha con propuestas, promesas y datos
- `/compare`: comparador lado a lado y acceso a imagen para compartir

## Variables

```bash
cp .env.example .env.local
```

Configura `NEXT_PUBLIC_API_URL`, por ejemplo:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## Arranque local

```bash
npm install
npm run dev
```

## Nota

La UI reutiliza la direccion visual de `pulso-civico-mvp (1).html`, pero ya conectada al backend FastAPI modular.
