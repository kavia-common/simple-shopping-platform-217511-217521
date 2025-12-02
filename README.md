# simple-shopping-platform-217511-217521

This repository contains a simple shopping platform with a Flask backend.

## Backend (shopping_backend)

- Location: `shopping_backend/`
- Quick start:
  1. `pip install -r shopping_backend/requirements.txt`
  2. `python shopping_backend/app.py` (Starts on 0.0.0.0:3001)

Alternatively, use Flask CLI:
```
export FLASK_APP=app:app
export FLASK_RUN_HOST=0.0.0.0
export FLASK_RUN_PORT=3001
flask --app shopping_backend/app.py run
```

No local venv activation is required; dependencies should be installed by CI or by the runtime using the provided requirements.txt.