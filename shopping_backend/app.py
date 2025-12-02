import os
from typing import Dict, Any
from flask import Flask, jsonify, request

# PUBLIC_INTERFACE
def create_app(config: Dict[str, Any] | None = None) -> Flask:
    """
    This is the Flask application factory.

    Creates and configures the Flask application instance.
    Accepts an optional configuration dictionary to override defaults.

    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(
        __name__,
        instance_relative_config=False,
    )

    # Default configuration
    app.config.update(
        JSON_SORT_KEYS=False,
        # Default port is documented in __main__ block; binding handled when running.
        APP_NAME="shopping_backend",
        ENV=os.getenv("FLASK_ENV", "production"),
    )

    # Apply any provided config overrides
    if config:
        app.config.update(config)

    # Healthcheck route
    @app.get("/health")
    def health():
        """Simple healthcheck endpoint."""
        return jsonify({"status": "ok", "service": app.config.get("APP_NAME", "shopping_backend")})

    # Basic API metadata route for quick discovery
    @app.get("/")
    def index():
        """
        Welcome/info route providing minimal API metadata and helpful links.
        """
        return jsonify({
            "service": "shopping_backend",
            "version": "0.1.0",
            "docs": "/openapi.json",
            "health": "/health",
            "endpoints": [
                {"method": "GET", "path": "/health", "desc": "Service health"},
                {"method": "GET", "path": "/products", "desc": "List products (placeholder)"},
            ]
        })

    # Placeholder example endpoint
    @app.get("/products")
    def list_products():
        """
        List products (placeholder).
        In future, this should query the shopping_database service.
        """
        sample_products = [
            {"id": 1, "name": "Sample Product A", "price": 19.99, "currency": "USD"},
            {"id": 2, "name": "Sample Product B", "price": 29.99, "currency": "USD"},
        ]
        # simple filter
        q = request.args.get("q", "").lower().strip()
        if q:
            filtered = [p for p in sample_products if q in p["name"].lower()]
            return jsonify({"items": filtered, "count": len(filtered)})
        return jsonify({"items": sample_products, "count": len(sample_products)})

    return app


# Expose app for WSGI servers (e.g., gunicorn, waitress)
app = create_app()

if __name__ == "__main__":
    """
    Allow running the app via `python app.py` without needing FLASK_APP env.
    Binds to 0.0.0.0:3001 for the preview environment.
    You can override host/port using environment variables:
      HOST=0.0.0.0 PORT=3001 python app.py
    """
    host = os.getenv("HOST", "0.0.0.0")
    # Default to port 3001 as requested
    port_str = os.getenv("PORT", "3001")
    try:
        port = int(port_str)
    except ValueError:
        port = 3001
    debug = os.getenv("FLASK_DEBUG", "0") in ("1", "true", "True", "yes")
    app.run(host=host, port=port, debug=debug)
