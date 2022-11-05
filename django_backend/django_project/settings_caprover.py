"""caprover specific django settings"""

import os

from django.core.exceptions import ImproperlyConfigured

from .settings import BASE_DIR

# key and debugging settings should not changed without care
SECRET_KEY = os.environ.get("CR_SECRET_KEY") or ImproperlyConfigured("CR_SECRET_KEY not set")
DEBUG = False
# allowed hosts get parsed from a comma-separated list
hosts = os.environ.get("CR_HOSTS") or ImproperlyConfigured("CR_HOSTS not set")
try:
    ALLOWED_HOSTS = hosts.split(",")
except:
    raise ImproperlyConfigured("CR_HOSTS could not be parsed")

# Database
if os.environ.get("CR_USESQLITE"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }
else:
    name = os.environ.get("CR_DB_NAME") or ImproperlyConfigured("CR_DB_NAME not set")
    user = os.environ.get("CR_DB_USER") or ImproperlyConfigured("CR_DB_USER not set")
    password = os.environ.get("CR_DB_PASSWORD") or ImproperlyConfigured("CR_DB_PASSWORD not set")
    host = os.environ.get("CR_DB_HOST") or ImproperlyConfigured("CR_DB_HOST not set")
    port = os.environ.get("CR_DB_PORT") or ImproperlyConfigured("CR_DB_PORT not set")

    DATABASES = {
        "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": name,
        "USER": user,
        "PASSWORD": password,
        "HOST": host,
        "PORT": port,
        }
    }


# Static Files
STATIC_ROOT = os.path.join(BASE_DIR, "public/static")
STATIC_URL = "/static/"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]



# ----------------------------------------------------------------------------------------------------------------------------
# EMAIL SETTINGS
#
EMAIL_BACKEND = os.environ.get("CR_EMAIL_BACKEND_PROD") or ImproperlyConfigured("CR_EMAIL_BACKEND_PROD not set")
EMAIL_HOST = os.environ.get("CR_EMAIL_HOST_PROD") or ImproperlyConfigured("CR_EMAIL_HOST_PROD not set")
EMAIL_HOST_USER = os.environ.get("CR_EMAIL_HOST_USER_PROD") or ImproperlyConfigured("CR_EMAIL_HOST_USER_PROD not set")
EMAIL_HOST_PASSWORD = os.environ.get("CR_EMAIL_HOST_PASSWORD_PROD") or ImproperlyConfigured("CR_EMAIL_HOST_PASSWORD_PROD not set")
EMAIL_USE_SSL = os.environ.get("CR_EMAIL_USE_SSL_PROD") or ImproperlyConfigured("CR_EMAIL_USE_SSL_PROD not set")
EMAIL_PORT = os.environ.get("CR_EMAIL_PORT_PROD") or ImproperlyConfigured("CR_EMAIL_PORT_PROD not set")
EMAIL_TIMEOUT = 30
