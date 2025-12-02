from flask import Flask
from flask_cors import CORS
from .routes.health import blp
from .routes.api import blp_api
from flask_smorest import Api
import os


app = Flask(__name__)
app.url_map.strict_slashes = False

# Configure CORS with explicit headers/methods for frontend origin(s)
# Environment variables:
# - FRONTEND_ORIGIN: single origin (e.g., https://example.com or http://localhost:3000)
# - FRONTEND_ORIGINS: optional comma-separated list of additional origins
default_frontend = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
extra_origins = os.getenv("FRONTEND_ORIGINS", "")
origins = [o.strip() for o in ([default_frontend] + ([x for x in extra_origins.split(",")] if extra_origins else [])) if o.strip()]

# Fallback wildcard for preview environments if not explicitly provided
# Note: When Authorization header is used, browsers require a specific origin, but many preview
# setups terminate TLS and forward requests; we keep wildcard as last resort for GETs without creds.
if not origins:
    origins = [default_frontend]

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Type"],
            "supports_credentials": False,
            "max_age": 600,
        },
        r"/": {
            "origins": origins,
            "methods": ["GET", "OPTIONS"],
            "allow_headers": ["Content-Type"],
            "supports_credentials": False,
        },
    },
)

# OpenAPI / Swagger configuration
app.config["API_TITLE"] = "Shopping API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config['OPENAPI_URL_PREFIX'] = '/docs'
app.config["OPENAPI_SWAGGER_UI_PATH"] = ""
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

api = Api(app)
# Register blueprints
api.register_blueprint(blp)
api.register_blueprint(blp_api)
