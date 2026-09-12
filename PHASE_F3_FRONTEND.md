# Frontend Phase F3 — Mobile / UX / a11y

## What shipped
- Skip link + `#main-content` landmark; primary nav `aria-label`
- Visible `:focus-visible` rings; `prefers-reduced-motion` respect
- Mobile-first nav search (`site-search` full width under collapse)
- Poster-card hover/focus lift; responsive trailer (`aspect-ratio` 16:9)
- Catalog filters stack full-width on small screens; larger touch targets on engagement buttons
- Themed list surfaces + empty states: favorites, watchlist, notifications, search, genres
- Engagement buttons expose `aria-pressed`; unread notifications announced to screen readers
- Toast container uses `aria-live="polite"`

## Verify
Hard-refresh the site and check home / list / detail / favorites / alerts on a narrow viewport.
