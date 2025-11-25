# JustFit - Django project (Phase 1)

## Setup (local)

1. python3 -m venv .venv
2. source .venv/bin/activate
3. pip install -r requirements.txt
4. python manage.py migrate
5. python manage.py createsuperuser
6. python manage.py runserver

Open http://127.0.0.1:8000/ for frontend and /admin for admin.

## Notes
- SQLite used for Phase 1.
- Media files are stored under `media/`.
- For production you should set DEBUG=False and store SECRET_KEY in environment variables.

to active env 

.venv\Scripts\activate  