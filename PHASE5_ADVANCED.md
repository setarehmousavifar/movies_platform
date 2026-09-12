# Phase 5 — Advanced backend (search, recommendations, AI, alerts)

## Search
- `SearchService` uses Postgres full-text (`SearchVector` / `SearchRank`) when `DB_ENGINE=postgres`
- SQLite / other engines fall back to multi-field `icontains` (title, description, tags, genres)
- Endpoint: `GET /api/v1/search/?q=...`

## Recommendations
- `RecommendationService` ranks movies by user genre preferences + favorites overlap
- Anonymous users get top-rated / high-view titles
- Endpoint: `GET /api/v1/recommendations/?limit=10`

## AI enrichment
- Fields on catalog items: `ai_summary`, `ai_tags`, `ai_enriched_at`
- Default: local extractive summary + keyword tags (no external API required)
- Optional OpenAI: set `OPENAI_API_KEY` (and optionally `OPENAI_MODEL`)
- Staff-only endpoints:
  - `POST /api/v1/movies/{id}/enrich/`
  - `POST /api/v1/series/{id}/enrich/`
  - `POST /api/v1/animations/{id}/enrich/`
  - body: `{ "force": true }` to re-run
- Management command:
```powershell
python manage.py enrich_catalog --limit 50
python manage.py enrich_catalog --force
```

## Alerts / realtime
- New catalog rows notify **staff/superusers** via `Notification` (bounded volume)
- Toggle: `CATALOG_ALERTS_ENABLED=true|false`
- REST:
  - `GET /api/v1/notifications/`
  - `POST /api/v1/notifications/{id}/read/`
- WebSocket (Channels + Daphne): `ws://127.0.0.1:8000/ws/alerts/`
- Channel layer: in-memory by default; set `REDIS_URL` for multi-worker

## Run with ASGI (WebSocket)
```powershell
.\.venv\Scripts\Activate.ps1
daphne -b 127.0.0.1 -p 8000 movies_platform.asgi:application
```
`runserver` still works for HTTP; use Daphne for WS.

## Tests
```powershell
python manage.py test main.tests api.tests -v 2
```
