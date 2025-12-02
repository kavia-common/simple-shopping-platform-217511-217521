"""
WSGI entrypoint for shopping_backend.

This exposes the Flask application as `application` for WSGI servers such as gunicorn or uWSGI.
"""
from app import app as application  # noqa: F401
