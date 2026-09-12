# Frontend Phase F5 — Commercial Django Admin

## What shipped
- Custom admin home (`templates/admin/catalog_index.html`):
  - Catalog counts (movies / series / animations)
  - Active premium, unread alerts, titles needing AI enrich
  - Recent `subscription.upgrade_requested` audit rows with links to user/subscriptions
- Inlines:
  - `DownloadLinkInline` on Movie / Series / Animation
  - `SeasonInline` on Series; `EpisodeInline` on Season
- Staff actions via billing service:
  - Subscription / User: **Grant premium (30 days)**
  - Subscription: deactivate + sync premium flag
  - Notification: mark read/unread
  - Catalog: existing **Enrich with AI**
- Polish: download counts on catalog lists, AuditLog read-only + note preview, DownloadLinkAdmin, UserAdmin with premium flags

## Verify
```powershell
python manage.py check
python manage.py test main.tests api.tests -v 1
# open /admin/ as staff — dashboard + edit a movie (download links) / series (seasons)
```
