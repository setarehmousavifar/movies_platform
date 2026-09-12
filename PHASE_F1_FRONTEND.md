# Frontend Phase F1 — API progressive enhancement

## What shipped
- [`static/js/api.js`](static/js/api.js): session + CSRF `fetch` client for `/api/v1/`
- Intercepts (with HTML form/link fallback if JS off):
  - Favorites add/remove
  - Watchlist add/remove
  - Notification mark-read
  - Download unlock (`GET /api/v1/downloads/<id>/` then redirect to URL)
- Toast feedback + busy button states
- CSRF via `<meta name="csrf-token">` in [`templates/base.html`](templates/base.html)

## Still server-rendered
First paint and no-JS users keep Django POST/redirect routes from F0.
