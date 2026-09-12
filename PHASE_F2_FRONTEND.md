# Frontend Phase F2 — Partials + unified theme

## What shipped
- Shared partials under `templates/main/partials/`:
  - `_poster_card.html`, `_catalog_filters.html`
  - `_engagement_buttons.html`, `_download_panel.html`, `_reviews_panel.html`
- Catalog surfaces use the same poster card + cinematic CSS:
  - home, movie/series/animation lists, top movies/series
  - movie/series/animation detail shells
- Auth & account pages use `.auth-panel` (no `bg-light` islands):
  - login, register, profile, password reset/confirm, subscription, update subscription
- Titles + SEO hooks in `base.html`:
  - `{% block title %}`, `{% block meta_description %}`, `{% block meta_extra %}`
  - Detail pages set description + Open Graph title

## Theme
Extended `static/css/style.css` (detail-shell, home-hero, poster-card, auth-panel, form controls on dark surface).
