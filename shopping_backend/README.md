# shopping_backend

Backend API for the simple shopping platform.

## Run options

- Using Python directly (no venv required in this environment):
  - Install deps: `pip install -r requirements.txt`
  - Start: `python app.py` (binds to 0.0.0.0:3001)

- Using Flask CLI:
  - `export FLASK_APP=app:app`
  - `export FLASK_RUN_HOST=0.0.0.0`
  - `export FLASK_RUN_PORT=3001`
  - `flask run`

- Using Gunicorn (production-style WSGI):
  - `gunicorn -b 0.0.0.0:3001 wsgi:application`

## Endpoints

- `GET /health` Health check
- `GET /` Service info
- `GET /products` Sample products with optional `?q=` filter

## Environment variables

- `HOST` (default: `0.0.0.0`) – host binding when running `python app.py`
- `PORT` (default: `3001`) – port when running `python app.py`
- `FLASK_DEBUG` (`0`/`1`) – enable debug mode in `python app.py`
- `FLASK_APP` (for `flask run`) – set to `app:app`
- `FLASK_RUN_HOST` (for `flask run`) – typically `0.0.0.0`
- `FLASK_RUN_PORT` (for `flask run`) – typically `3001`

No local virtualenv activation is required. If you want isolation locally, create one but do not hardcode activation paths into scripts.
