# Backend Hardening Pass

## Verdict
Phases 0–7 delivered a usable API. This pass closed the High/Critical gaps found in the final sweep. The backend is **commercially defensible for the capstone + SPA**, not a literal claim of zero residual risk.

## Closed in this pass
- JWT access 15m, refresh rotation + blacklist, `POST /api/v1/auth/logout/`
- Production refuses insecure/default `DJANGO_SECRET_KEY`
- WebSocket `/ws/alerts/` requires authenticated user
- CORS via `django-cors-headers` + `CORS_ALLOWED_ORIGINS`
- Download URLs removed from catalog detail; unlock only via `GET /api/v1/downloads/<id>/` after entitlement
- Global DRF `EXCEPTION_HANDLER` maps DomainError → 400/403/404 with `{detail, code}`
- Favorites/watchlist/enrich/upgrade use serializers; review `parent_id` validated strictly
- Recommendations GET is read-only (no N writes)
- Indexes on `country` and `Series.status`
- Throttles for search + catalog retrieve
- Expanded API tests

## Remaining architectural limits (honest)
- External CDN URLs remain guessable if leaked outside the app; full edge auth needs signed CDN keys.
- Default DRF permission remains `AllowAny` for public catalog reads — new write views must set permissions explicitly.
- OpenAPI docs remain public (acceptable for portfolio; lock behind auth for private deploy if needed).
