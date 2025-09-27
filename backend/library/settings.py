import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "unsafe")
DEBUG = os.getenv("DJANGO_DEBUG", "0") == "1"
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "django_filters",
    "drf_spectacular",
    "corsheaders",

    "users",
    "books",
    "borrowings",
    "payments",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # має бути якнайвище
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "library.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "library.wsgi.application"

# Database: якщо DB_HOST не заданий — SQLite
if os.getenv("DB_HOST"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME", "library"),
            "USER": os.getenv("DB_USER", "library"),
            "PASSWORD": os.getenv("DB_PASSWORD", "library"),
            "HOST": os.getenv("DB_HOST", "db"),
            "PORT": os.getenv("DB_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_USER_MODEL = "users.User"

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=int(os.getenv("ACCESS_MINUTES", "60"))
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=int(os.getenv("REFRESH_DAYS", "1"))
    ),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

SPECTACULAR_SETTINGS = {
    "TITLE": os.getenv("API_TITLE", "Library API"),
    "VERSION": os.getenv("API_VERSION", "1.0.0"),
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Kyiv"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# CORS/CSRF (якщо є фронтенд)
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
]
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
]

# Штрафи
FINE_MULTIPLIER = int(os.getenv("FINE_MULTIPLIER", "2"))
