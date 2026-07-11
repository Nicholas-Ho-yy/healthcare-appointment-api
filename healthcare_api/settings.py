"""
Django settings for the healthcare_api project.

"""

import os
from pathlib import Path


# This points to the main project folder and is used when
# building paths to other files such as the database.
BASE_DIR = Path(__file__).resolve().parent.parent


# -------------------------------------------------------------------
# Security and environment configuration
# -------------------------------------------------------------------

# Use the secret key stored in Render when the project is deployed.
# If I'm running the project locally, use the development key instead.
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-local-development-key",
)

# Keep debug mode turned on while developing the project.
# Render changes this to False when the project is deployed.
DEBUG = os.environ.get("DEBUG", "True").lower() == "true"

# These addresses are used when running the project
# on my own computer.
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
]

# Render creates a website address automatically.
# Add that address so people can access the deployed application.
render_hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME")

if render_hostname:
    ALLOWED_HOSTS.append(render_hostname)


# -------------------------------------------------------------------
# Installed applications
# -------------------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Django REST Framework is used to build the REST API.
    "rest_framework",

    # Main application containing the healthcare data models,
    # This app contains all the models, views, serializers.
    "appointments",
]


# -------------------------------------------------------------------
# Middleware
# -------------------------------------------------------------------

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # WhiteNoise allows CSS and JavaScript files to work
    # after the project has been deployed.
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# Root URL configuration for the project.
ROOT_URLCONF = "healthcare_api.urls"


# -------------------------------------------------------------------
# Templates
# -------------------------------------------------------------------

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        # Templates are stored inside the appointments application,
        # so no additional project-level template directory is needed.
        "DIRS": [],

        # Tell Django to automatically look for templates
        # inside each installed app.
        "APP_DIRS": True,

        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# Gunicorn starts the project using this file
# when the application is deployed on Render.
WSGI_APPLICATION = "healthcare_api.wsgi.application"


# -------------------------------------------------------------------
# Database
# -------------------------------------------------------------------

# SQLite is used, the same database is used both locally and on Render.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# -------------------------------------------------------------------
# Password validation
# -------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# -------------------------------------------------------------------
# Internationalisation and time zones
# -------------------------------------------------------------------

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"

USE_I18N = True
USE_TZ = True


# -------------------------------------------------------------------
# Static files
# -------------------------------------------------------------------

STATIC_URL = "/static/"

# collectstatic copies all CSS, JavaScript and image files here.
# WhiteNoise then serves these files after deployment.
STATIC_ROOT = BASE_DIR / "staticfiles"