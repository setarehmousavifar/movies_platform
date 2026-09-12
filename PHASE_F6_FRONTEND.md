# Frontend Phase F6 — Optional JWT browse client

## Goal
Show a thin SPA against `/api/v1/` for the resume, without replacing the SSR site.

## What shipped
- Route: [`/app/`](http://127.0.0.1:8000/app/) (`spa_browse`)
- Vanilla JS client (no npm/React):
  - JWT login / refresh / logout (`sessionStorage`)
  - Browse movies · series · animations (paginated)
  - Detail + favorite toggle (auth)
  - Search + recommendations
- Assets: `templates/spa/browse.html`, `static/js/spa-browse.js`, `static/css/spa-browse.css`
- Footer link on the main site → API browse app

## How to demo
```powershell
python manage.py runserver 127.0.0.1:8000
# open http://127.0.0.1:8000/app/
# login with admin / admin123 (after seed_demo)
```

Main catalog UX remains Django templates; this app is an API consumer showcase.
