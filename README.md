# Movies Platform

Capstone / portfolio project: a **modular Django monolith** for browsing movies, series, and animations — with REST API, JWT auth, premium entitlements, search, recommendations, AI enrichment, and realtime alerts.

**Repository:** [github.com/setarehmousavifar/movies_platform](https://github.com/setarehmousavifar/movies_platform)

## Highlights

| Area | What you get |
|------|----------------|
| Catalog | Movies, series, animations, genres, reviews, favorites, watchlist |
| API | DRF `/api/v1/` + OpenAPI at `/api/docs/` + JWT |
| Billing | Premium entitlement, upgrade request, staff assign / mock checkout |
| Intelligence | Full-text search (Postgres) / multi-field fallback, recommendations, AI summary/tags |
| Ops | Split settings, `/healthz`, Docker Compose (Postgres), structured logging, tests |
| Realtime | Channels WebSocket `ws/alerts/` + in-app notifications |

## Stack

- Python 3.13+, **Django 5.2 LTS**
- Django REST Framework, SimpleJWT, drf-spectacular, django-filter
- Channels + Daphne (optional Redis channel layer)
- SQLite (local default) or PostgreSQL 16 (Docker / `DB_ENGINE=postgres`)

## Quick start (Windows)

```powershell
cd movies_platform
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py seed_demo --with-admin
python manage.py runserver 127.0.0.1:8000
```

- Site: http://127.0.0.1:8000/  
- Admin: http://127.0.0.1:8000/admin/ (`admin` / `admin123` after seed)  
- API docs: http://127.0.0.1:8000/api/docs/  
- Health: http://127.0.0.1:8000/healthz  

For WebSocket alerts:

```powershell
daphne -b 127.0.0.1 -p 8000 movies_platform.asgi:application
```

## Docker

```powershell
docker compose up --build
```

## Tests

```powershell
python manage.py test main.tests api.tests -v 2
```

## Demo script

See [DEMO.md](DEMO.md) for a 5-minute walkthrough (site + API + admin AI enrich).

## Architecture

One-page overview: [ARCHITECTURE.md](ARCHITECTURE.md)

Phase notes: `PHASE0_SMOKE.md` … `PHASE6_FRONTEND.md`

## Project layout

```
main/           # Domain models, services, site views, admin, Channels
api/            # DRF v1 (auth, catalog, engagement, billing, search, AI, alerts)
movies_platform/settings/  # base / local / production
templates/      # Server-rendered UI
static/         # CSS / JS
```

## Environment

Copy `.env.example` → `.env`. Important keys:

- `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DB_ENGINE`
- `OPENAI_API_KEY` (optional AI enrichment)
- `REDIS_URL` (optional multi-worker Channels)
- `CATALOG_ALERTS_ENABLED`

## License / academic use

Undergraduate capstone project by Setareh Mousavifar. Use as a portfolio reference with attribution.
