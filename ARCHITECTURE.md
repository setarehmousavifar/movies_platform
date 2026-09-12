# Architecture (one page)

## Style

**Modular monolith** on Django: one deployable unit, clear internal boundaries (domain models → services → HTTP adapters).

```text
┌─────────────────────────────────────────────────────────────┐
│  Adapters                                                    │
│  templates/views (site) │ api/ (DRF+JWT) │ admin │ Channels │
└─────────────┬───────────────────┬───────────────┬───────────┘
              │                   │               │
              ▼                   ▼               ▼
┌─────────────────────────────────────────────────────────────┐
│  Services (main/services/)                                   │
│  catalog · engagement · billing · search · recommendation    │
│  enrichment · alerts                                         │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Domain (main/models.py)                                     │
│  CatalogItem → Movie / Series / Animation                    │
│  User · Subscription · FavoriteItem · Watchlist · Review     │
│  Notification · AuditLog · AI fields on catalog              │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
                     SQLite │ PostgreSQL
```

## Auth & access

| Channel | Mechanism |
|---------|-----------|
| Site | Session cookie |
| API | JWT (SimpleJWT) |
| Downloads | `EntitlementService` — premium / staff only |
| Premium | Staff assign or mock checkout — no free self-upgrade |

## Key HTTP surfaces

| Path | Role |
|------|------|
| `/` … | HTML site |
| `/admin/` | Django Admin (+ AI enrich action) |
| `/api/v1/` | REST |
| `/api/docs/` | OpenAPI UI |
| `/healthz` | Liveness + DB ping |
| `/ws/alerts/` | Breaking catalog alerts (ASGI) |

## Settings

- `movies_platform.settings.local` — default (DEBUG, SQLite)
- `movies_platform.settings.production` — hardened HTTPS/HSTS
- Shared: `movies_platform.settings.base`

## Why this shape (defense talking points)

1. **Single source of truth** — site and API call the same services (no duplicated business rules).
2. **RBAC + entitlement** — premium downloads and upgrades are explicit and auditable (`AuditLog`).
3. **Contract-first API** — OpenAPI schema for future SPA/mobile clients.
4. **Ops-ready** — env-based config, health check, Docker/Postgres path, tests.
5. **Extensible intelligence** — local NLP defaults; optional OpenAI without blocking demos.
