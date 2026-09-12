# Frontend Phase F4 — Performance + SEO

## What shipped
- Critical CSS preload; CDN `dns-prefetch`; Font Awesome non-blocking (`media=print` → `all`)
- Bootstrap / `api.js` / `alerts.js` remain deferred
- Default canonical + Open Graph on all pages; detail pages override OG + add:
  - `og:image` / Twitter large image
  - poster image `preload` (LCP)
  - JSON-LD (`Movie` / `TVSeries`)
- Detail posters: `loading=eager` + `fetchpriority=high` + width/height
- Catalog posters: lazy + `decoding=async` + CLS-friendly dimensions; first home row eager
- `robots.txt` + Django `sitemap.xml` (static views + movies/series/animations)
- Filter `absolute_media_uri` for absolute poster URLs in SEO tags
- DEMO notes for Daphne WS + SEO smoke URLs

## Verify
```powershell
python manage.py check
python manage.py test main.tests api.tests -v 1
# optional: open /robots.txt /sitemap.xml and view-source a detail page
```
