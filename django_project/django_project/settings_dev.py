"""local runserver settings"""

import os

from .settings import BASE_DIR

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "q$yydv1ngc0$@s2(1yk@!yjojfcd3by_jtx+c9m3g*_6ymdxr="

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}


# Static Files
STATIC_ROOT = os.path.join(BASE_DIR, "public/static")
STATIC_URL = "/static/"

STATICFILES_DIRS = [
	os.path.join(BASE_DIR, 'static')
]
