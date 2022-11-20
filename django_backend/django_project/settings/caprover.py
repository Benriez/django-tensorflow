"""caprover specific django settings"""

import os

from django.core.exceptions import ImproperlyConfigured

from .main import BASE_DIR

# key and debugging settings should not changed without care
SECRET_KEY = os.environ.get("CR_SECRET_KEY") or ImproperlyConfigured("CR_SECRET_KEY not set")
try:
    if os.environ.get("CR_DEBUG", True):
        DEBUG = True
except:
    DEBUG = False

# allowed hosts get parsed from a comma-separated list
trust_orgins = os.environ.get("CR_TRUSTED_ORIGINS") or ImproperlyConfigured("CR_TRUSTED_ORIGINS not set")
CSRF_TRUSTED_ORIGINS = [trust_orgins]
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


redis_host = os.environ.get("CR_REDIS_HOST") or ImproperlyConfigured("CR_REDIS_HOST not set")
redis_pass = os.environ.get("CR_REDIS_PASS") or ImproperlyConfigured("CR_REDIS_PASS not set")
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("redis://:" + redis_pass + "@" + redis_host + ":6379/0")],
        }
    },
}


SITE_URL=os.environ.get("CR_HOSTS") or ImproperlyConfigured("CR_HOSTS not set")
try:
    SKIP_EMAIL=os.environ.get("CR_SKIP_EMAIL")
except:
    pass
# Static Files
STATIC_ROOT = os.path.join(BASE_DIR, "public/static")
STATIC_URL = "/static/"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, '../static')
]

ARMED=os.environ.get("CR_ARMED") or ImproperlyConfigured("CR_ARMED not set")



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


AWS_ACCESS_KEY_ID = os.environ.get("CR_AWS_ACCESS_KEY_ID") or ImproperlyConfigured("CR_AWS_ACCESS_KEY_ID not set")
AWS_SECRET_ACCESS_KEY = os.environ.get("CR_AWS_SECRET_ACCESS_KEY")  or ImproperlyConfigured("CR_AWS_SECRET_ACCESS_KEY not set")
AWS_STORAGE_BUCKET_NAME = os.environ.get("CR_AWS_STORAGE_BUCKET_NAME") or ImproperlyConfigured("CR_AWS_STORAGE_BUCKET_NAME not set")
AWS_S3_ENDPOINT_URL = os.environ.get("CR_AWS_S3_ENDPOINT_URL") or ImproperlyConfigured("CR_AWS_S3_ENDPOINT_URL not set")