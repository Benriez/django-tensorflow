"""local runserver settings"""

import os
import environ

from .main import BASE_DIR


env = environ.Env()
environ.Env.read_env()

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "q$yydv1ngc0$@s2(1yk@!yjojfcd3by_jtx+c9m3g*_6ymdxr="

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "../db.sqlite3"),
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}

# Static Files
STATIC_ROOT = os.path.join(BASE_DIR, "public/static")
STATIC_URL = "/static/"

STATICFILES_DIRS = [
	os.path.join(BASE_DIR, '../static')
]


EMAIL_BACKEND = env("EMAIL_BACKEND_DEV")
EMAIL_HOST = env("EMAIL_HOST_DEV")
EMAIL_HOST_USER = env("EMAIL_HOST_USER_DEV")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD_DEV")
EMAIL_PORT = env("EMAIL_PORT_DEV")
EMAIL_TIMEOUT = 30

AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
AWS_S3_ENDPOINT_URL = env("AWS_S3_ENDPOINT_URL")

SITE_URL='http://127.0.0.1:8000'