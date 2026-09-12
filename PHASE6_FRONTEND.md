# Phase 6 — Frontend & Admin on stable backend/API

## Goal
Site templates and Django Admin consume the same service layer / API contracts from Phases 2–5 (no parallel business logic).

> **Follow-up:** UI polish after this milestone lives in `PHASE_F0_FRONTEND.md` … `PHASE_F6_FRONTEND.md` (templates theme, API progressive enhancement, SEO, commercial admin, optional JWT `/app/` client).

## Admin
- Movie / Series / Animation: `ai_summary`, `ai_tags`, `ai_enriched_at` fieldset
- Bulk action: **Enrich selected with AI summary/tags**
- Polished `NotificationAdmin` and `RecommendationAdmin`

## Site (server-rendered + shared services)
| Surface | Service / API |
|---------|----------------|
| Home “Recommended for you” | `RecommendationService` |
| Navbar search | `SearchService` (multi-type results) |
| Favorites list | `FavoriteService.list_for` |
| Notifications page + badge | `AlertService` + `nav_notifications` |
| Movie detail AI block | model fields from enrichment |

Routes:
- `/notifications/`
- `/notifications/<id>/read/` (POST)

## Client JS
- `static/js/alerts.js` — WebSocket toast for `/ws/alerts/` (needs Daphne)
- `static/js/api.js` — session CSRF progressive enhancement (F1)
- `/app/` — optional JWT browse SPA (F6)

## API still available for SPA / mobile
All Phase 3–5 endpoints under `/api/v1/` + OpenAPI at `/api/docs/`.

## Verify
```powershell
.\.venv\Scripts\Activate.ps1
python manage.py test main.tests api.tests -v 2
python manage.py runserver 127.0.0.1:8000
```
Admin enrich: select movies → action → Enrich…  
Or: `python manage.py enrich_catalog --limit 20`
