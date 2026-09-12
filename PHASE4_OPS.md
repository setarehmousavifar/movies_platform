# Phase 4 — Production-quality backend foundation

## Settings split
- `movies_platform.settings.local` — default for manage.py / runserver
- `movies_platform.settings.production` — HTTPS/HSTS hardened
- Shared config in `movies_platform.settings.base`

## Health
- `GET /healthz` → `{ status, database }`

## Seed
```powershell
python manage.py seed_demo --with-admin
```

## Tests
```powershell
python manage.py test main.tests api.tests -v 2
```

## Docker (Postgres)
```powershell
docker compose up --build
```
App: http://127.0.0.1:8000/  
Health: http://127.0.0.1:8000/healthz  
Admin seed: `admin` / `admin123`

## Logging
Structured console logs via `LOGGING` in base settings (`LOG_LEVEL` env).

## Note on Django LTS
Project targets **Django 5.2 LTS** (see `requirements.txt`).
