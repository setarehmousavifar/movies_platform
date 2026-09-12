# Phase 3 — REST API v1

## Docs
- Swagger UI: http://127.0.0.1:8000/api/docs/
- ReDoc: http://127.0.0.1:8000/api/redoc/
- OpenAPI schema: http://127.0.0.1:8000/api/schema/

## Auth
- `POST /api/v1/auth/register/`
- `POST /api/v1/auth/token/` → `{ access, refresh }`
- `POST /api/v1/auth/token/refresh/`
- `GET /api/v1/auth/me/` (Bearer token)

Header: `Authorization: Bearer <access>`

## Catalog
- `GET /api/v1/movies/`, `GET /api/v1/movies/{id}/`
- `GET /api/v1/series/`, `GET /api/v1/series/{id}/`
- `GET /api/v1/animations/`, `GET /api/v1/animations/{id}/`
- `GET /api/v1/genres/`
- `GET /api/v1/search/?q=`

Query: `?search=`, `?ordering=-overall_rating`, filters like `?language=English`

## Engagement
- `GET/POST /api/v1/reviews/`
- `GET/POST/DELETE /api/v1/favorites/`
- `GET/POST/DELETE /api/v1/watchlist/`

Favorites/watchlist create body: `{ "movie": 1 }`  
Idempotent: repeated POST returns 200 with existing row.

## Billing
- `GET /api/v1/subscriptions/me/`
- `POST /api/v1/subscriptions/request-upgrade/`

Download URLs on detail payloads are `null` + `locked: true` unless premium/staff.

## Throttling
- anon 120/min, user 240/min
- auth endpoints 20/min
- write endpoints 60/min
