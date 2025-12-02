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

    # Healthcheck routes
    @app.get("/health")
    def health():
        """Simple healthcheck endpoint."""
        return jsonify({"status": "ok", "service": app.config.get("APP_NAME", "shopping_backend")})

    # Provide API-prefixed health for clients expecting /api/health
    @app.get("/api/health")
    def api_health():
        """Healthcheck with /api prefix for compatibility."""
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
                {"method": "GET", "path": "/", "desc": "Service info"},
                {"method": "GET", "path": "/health", "desc": "Service health"},
                {"method": "GET", "path": "/products", "desc": "List products (placeholder)"},
                {"method": "GET", "path": "/api", "desc": "API index"},
                {"method": "GET", "path": "/api/health", "desc": "Service health (API prefix)"},
                {"method": "GET", "path": "/api/products", "desc": "List products (API prefix)"},
                {"method": "GET", "path": "/api/cart", "desc": "View cart (placeholder)"},
                {"method": "POST", "path": "/api/cart", "desc": "Add to cart (placeholder)"},
                {"method": "POST", "path": "/api/auth/login", "desc": "User login (placeholder)"},
                {"method": "POST", "path": "/api/auth/register", "desc": "User registration (placeholder)"},
                {"method": "POST", "path": "/api/order/checkout", "desc": "Checkout (placeholder)"},
            ]
        })

    # API index mirroring root info under /api
    @app.get("/api")
    def api_index():
        """API index route to assist clients expecting an /api base path."""
        return jsonify({
            "service": "shopping_backend",
            "version": "0.1.0",
            "basePath": "/api",
            "health": "/api/health",
            "resources": {
                "products": "/api/products",
                "cart": "/api/cart",
                "auth": { "login": "/api/auth/login", "register": "/api/auth/register" },
                "order": { "checkout": "/api/order/checkout" },
            }
        })

    # Placeholder example endpoint (no prefix)
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

    # API-prefixed alias for products
    @app.get("/api/products")
    def api_list_products():
        """Alias of list_products under /api prefix for client compatibility."""
        return list_products()

    # Temporary placeholder routes to avoid 404s for expected domains

    # Cart
    @app.get("/api/cart")
    def get_cart():
        """Return a placeholder cart."""
        return jsonify({"items": [], "subtotal": 0.0, "currency": "USD"})

    @app.post("/api/cart")
    def add_to_cart():
        """Accepts an item to add to the cart (placeholder, no persistence)."""
        data = request.get_json(silent=True) or {}
        return jsonify({"message": "Item accepted (placeholder)", "item": data}), 201

    # Auth
    @app.post("/api/auth/login")
    def auth_login():
        """Placeholder login route."""
        payload = request.get_json(silent=True) or {}
        return jsonify({"message": "Logged in (placeholder)", "user": {"email": payload.get("email")}})

    @app.post("/api/auth/register")
    def auth_register():
        """Placeholder registration route."""
        payload = request.get_json(silent=True) or {}
        return jsonify({"message": "Registered (placeholder)", "user": {"email": payload.get("email")}}), 201

    # Order
    @app.post("/api/order/checkout")
    def order_checkout():
        """Placeholder checkout route."""
        order = request.get_json(silent=True) or {}
        return jsonify({"message": "Order received (placeholder)", "order": order, "status": "processing"}), 202

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
