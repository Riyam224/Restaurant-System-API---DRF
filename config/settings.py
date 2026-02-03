from pathlib import Path
from datetime import timedelta
import os

import dj_database_url
from dotenv import load_dotenv

# --------------------------------------------------
# BASE DIRECTORY & ENV VARIABLES
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# --------------------------------------------------
# CORE
# --------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-dev-secret-key")

DEBUG = os.getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "web-production-e1bea.up.railway.app",
    ".railway.app",
]

# --------------------------------------------------
# APPS
# --------------------------------------------------
INSTALLED_APPS = [
    # Admin UI
    "jazzmin",
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_api_key",
    "drf_spectacular",
    "corsheaders",
    # Local apps
    "accounts",
    "addresses",
    "menu",
    "cart",
    "orders",
    "reviews",
    "coupons",
    "core",
    "analytics",
]

# --------------------------------------------------
# MIDDLEWARE
# --------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# --------------------------------------------------
# SECURITY
# --------------------------------------------------
SECURE_SSL_REDIRECT = not DEBUG
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# --------------------------------------------------
# CORS / CSRF
# --------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = DEBUG

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:8000",
    "https://web-production-e1bea.up.railway.app",
]

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    "https://web-production-e1bea.up.railway.app",
]

# --------------------------------------------------
# DRF
# --------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "2000/day",
    },
}

# --------------------------------------------------
# JWT
# --------------------------------------------------
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# --------------------------------------------------
# SWAGGER / OPENAPI
# --------------------------------------------------
SPECTACULAR_SETTINGS = {
    "TITLE": "Restaurant API",
    "DESCRIPTION": (
        "Professional Restaurant Delivery API\n\n"
        "• JWT Authentication\n"
        "• API Key access (TMDB-style)\n"
        "• Rate limited & production ready\n"
        "• Flutter-ready backend"
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SERVERS": [
        {"url": "http://localhost:8000", "description": "Local"},
        {
            "url": "https://web-production-e1bea.up.railway.app",
            "description": "Production",
        },
    ],
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            },
            "ApiKeyAuth": {
                "type": "apiKey",
                "name": "X-API-Key",
                "in": "header",
            },
        }
    },
    "SECURITY": [{"BearerAuth": []}],
    "SWAGGER_UI_SETTINGS": {
        "docExpansion": "none",
        "persistAuthorization": True,
    },
}

# --------------------------------------------------
# URLS / TEMPLATES
# --------------------------------------------------
ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --------------------------------------------------
# DATABASE
# --------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

# Parse database config - only use SSL for PostgreSQL
db_config = dj_database_url.config(
    default=DATABASE_URL,
    conn_max_age=600,
)

# Add SSL requirement only for PostgreSQL
if db_config.get("ENGINE") == "django.db.backends.postgresql":
    db_config["OPTIONS"] = {"sslmode": "require"}

DATABASES = {"default": db_config}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --------------------------------------------------
# CACHING
# --------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "restaurant-cache",
        "OPTIONS": {
            "MAX_ENTRIES": 1000,
        },
        "TIMEOUT": 300,  # 5 minutes default
    }
}

# Cache configuration for different environments
# For production with Redis, use:
# CACHES = {
#     "default": {
#         "BACKEND": "django.core.cache.backends.redis.RedisCache",
#         "LOCATION": os.getenv("REDIS_URL", "redis://127.0.0.1:6379/1"),
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#         },
#         "KEY_PREFIX": "restaurant",
#         "TIMEOUT": 300,
#     }
# }

# --------------------------------------------------
# STATIC / MEDIA
# --------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# --------------------------------------------------
# I18N
# --------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --------------------------------------------------
# LOGGING
# --------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "restaurant.log",
            "maxBytes": 1024 * 1024 * 10,  # 10MB
            "backupCount": 5,
            "formatter": "verbose",
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "errors.log",
            "maxBytes": 1024 * 1024 * 10,  # 10MB
            "backupCount": 5,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["error_file"],
            "level": "ERROR",
            "propagate": False,
        },
        "orders": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "cart": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "coupons": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# Create logs directory if it doesn't exist
import os
os.makedirs(BASE_DIR / "logs", exist_ok=True)

# --------------------------------------------------
# JAZZMIN (Admin UI)
# --------------------------------------------------
JAZZMIN_SETTINGS = {
    # Site branding
    "site_title": "Restaurant Admin",
    "site_header": "Restaurant System",
    "site_brand": "Restaurant Dashboard",
    "site_logo": None,  # Add your logo path here
    "site_logo_classes": "img-circle",
    "site_icon": None,  # Add favicon path here
    "welcome_sign": "Welcome to Restaurant Admin",
    "copyright": "Restaurant API",

    # Layout - Enable wide layout for full-width dashboard
    "layout": "wide",

    # UI Customization - Modern theme
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],

    # Top Menu
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "View Site", "url": "/", "new_window": True},
        {"model": "auth.User"},
    ],

    # User Menu
    "usermenu_links": [
        {"model": "auth.user"}
    ],

    # Side Menu
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs"
    },

    # Related Modal
    "related_modal_active": True,

    # Custom icons for models
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "menu.Product": "fas fa-utensils",
        "menu.Category": "fas fa-list",
        "orders.Order": "fas fa-shopping-cart",
        "orders.OrderStatusHistory": "fas fa-history",
        "cart.Cart": "fas fa-shopping-basket",
        "cart.CartItem": "fas fa-cart-plus",
        "coupons.Coupon": "fas fa-tag",
        "coupons.CouponUsage": "fas fa-ticket-alt",
        "addresses.Address": "fas fa-map-marker-alt",
        "reviews.Review": "fas fa-star",
        "reviews.ReviewHelpfulness": "fas fa-thumbs-up",
        "analytics": "fas fa-chart-line",
    },

    # Default icon for models
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",

    # Custom Links
    "custom_links": {},

    # Custom CSS and JS
    "custom_css": "admin/css/custom_admin.css",
    "custom_js": None,

    # UI Tweaks
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,

    # Theme
    "theme": "flatly",  # Modern flat design theme

    # Language
    "language_chooser": False,

    # Custom App Order - Organize sidebar navigation
    "order_with_respect_to": [
        "analytics",
        "orders",
        "menu",
        "cart",
        "coupons",
        "addresses",
        "reviews",
        "auth",
    ],
}
