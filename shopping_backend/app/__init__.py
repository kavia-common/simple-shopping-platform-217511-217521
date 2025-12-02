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
default_frontend = os.getenv("FRONTEND_ORIGIN", "").strip()
extra_origins = os.getenv("FRONTEND_ORIGINS", "").strip()

origins_list = []
if default_frontend:
    origins_list.append(default_frontend)
if extra_origins:
    origins_list.extend([x.strip() for x in extra_origins.split(",") if x.strip()])

# If no explicit origins are provided, default to permissive demo preview settings.
# This avoids CORS failures like "Failed to fetch" in preview environments where the
# frontend runs at https://<host>:3000 and backend at https://<host>:3001.
# Since we do not use cookies (supports_credentials=False), wildcard is acceptable.
cors_origins = origins_list if origins_list else "*"

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": cors_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Type"],
            "supports_credentials": False,
            "max_age": 600,
        },
        r"/": {
            "origins": cors_origins,
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
