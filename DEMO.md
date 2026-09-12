# Demo script (≈5 minutes)

Prerequisites: venv active, migrations applied, seed run.

```powershell
.\.venv\Scripts\Activate.ps1
python manage.py seed_demo --with-admin
python manage.py enrich_catalog --limit 10
python manage.py runserver 127.0.0.1:8000
```

## 1. Site (2 min)

1. Open http://127.0.0.1:8000/ — show **Recommended**, New, Popular.
2. Search from navbar (multi-type results + AI summary when enriched).
3. Open a movie — favorites / watchlist / AI summary block.
4. Log in as `admin` / `admin123` — Alerts badge + `/notifications/`.

## 2. Admin (1 min)

1. http://127.0.0.1:8000/admin/ — operations snapshot (counts, upgrade requests).
2. Movies → select rows → action **Enrich selected with AI summary/tags**.
3. Open a movie → download links inline + **AI enrichment** fieldset.
4. Users/Subscriptions → action **Grant premium (30 days)** (billing service).

## 3. API (2 min)

1. Docs: http://127.0.0.1:8000/api/docs/
2. Token (PowerShell):

```powershell
$body = @{ username = 'admin'; password = 'admin123' } | ConvertTo-Json
$tok = Invoke-RestMethod -Method POST -Uri http://127.0.0.1:8000/api/v1/auth/token/ -ContentType 'application/json' -Body $body
$h = @{ Authorization = "Bearer $($tok.access)" }
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/recommendations/' -Headers $h
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/search/?q=a' -Headers $h
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/healthz'
```

## 4. Optional realtime (WebSocket alerts)

Use Daphne instead of `runserver` so `/ws/alerts/` works:

```powershell
daphne -b 127.0.0.1 -p 8000 movies_platform.asgi:application
```

Create a new movie in Admin while the site is open — toast via `/ws/alerts/` (staff notifications also appear under Alerts).

## SEO check

- http://127.0.0.1:8000/robots.txt
- http://127.0.0.1:8000/sitemap.xml
- View-source on a movie detail page: Open Graph + JSON-LD

## Talking points

- Same services power HTML and API.
- Premium gate for downloads (show locked `download_url` for free user in API detail).
- Optional JWT browse client at `/app/` (Phase F6) for SPA/API storytelling.
- Phase docs `PHASE0`–`PHASE7` + `PHASE_F0`–`PHASE_F6` map to academic milestones.
