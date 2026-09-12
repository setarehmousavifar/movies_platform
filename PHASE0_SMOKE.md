# Phase 0 — Stabilization smoke checklist

## Before
- `/top-movies/` and `/top-series/` crashed (`order_by('-rating')`)
- `/filter/?genre=...` crashed (bad genre lookup)
- Password reset pointed at missing `accounts/` templates
- Duplicate `login` / `logout` URL names
- Series/animation reviews failed (`Review.movie` required)
- Favorites/watchlist mutations accepted GET
- Secrets hardcoded in `settings.py`
- Signals listened to wrong User model
- Empty catalog (no fixtures)
- Detail pages crashed on empty `background_poster.url`

## After (verified 2026-09-12)
All of the following returned **HTTP 200**:
- `/`
- `/movies/`
- `/movies/1/`
- `/series/1/`
- `/animations/1/`
- `/top-movies/`
- `/top-series/`
- `/filter/?genre=Action`
- `/login/`
- `/password_reset/`
- `/admin/login/`
- `/register/`
- `/search/?q=Sample`

## Local commands
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata demo_catalog
python manage.py runserver 127.0.0.1:8000
```

Admin (if created earlier): `admin` / `admin123`

Copy `.env.example` → `.env` before first run on a new machine.
