"""environment agnostic django settings"""

import os
import environ

from django.core.exceptions import ImproperlyConfigured

env = environ.Env()
environ.Env.read_env()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Application definition
INSTALLED_APPS = [
    "channels",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'rest_framework',
    'storages',
    # 'private_storage',
    # Add your apps here
    "app",
    "authentication",
    "system",
    "djmoney",
]

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}

STREAM_SOCKET_GROUP_NAME = "system_detail"
ASGI_APPLICATION = "django_project.asgi.application"


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "django_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "app/templates"),
            os.path.join(BASE_DIR, "authentication/templates"),
            os.path.join(BASE_DIR, "django_project/templates"),
            os.path.join(BASE_DIR, "system/templates")
        ],
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




#WSGI_APPLICATION = "django_project.wsgi.application"


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "de-DE"

TIME_ZONE = "CET"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

TEMPLATE_DIRS = (os.path.join(BASE_DIR,  "templates"),)

# WhiteNoise Configuration
# http://whitenoise.evans.io/en/stable/#quickstart-for-django-apps
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
DEFAULT_AUTO_FIELD='django.db.models.AutoField'


STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# Media file handling
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'


DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
try:
    AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_ENDPOINT_URL = env("AWS_S3_ENDPOINT_URL")
except:
    AWS_ACCESS_KEY_ID = os.environ.get("CR_AWS_ACCESS_KEY_ID") or ImproperlyConfigured("CR_AWS_ACCESS_KEY_ID not set")
    AWS_SECRET_ACCESS_KEY = os.environ.get("CR_AWS_SECRET_ACCESS_KEY")  or ImproperlyConfigured("CR_AWS_SECRET_ACCESS_KEY not set")
    AWS_STORAGE_BUCKET_NAME = os.environ.get("CR_AWS_STORAGE_BUCKET_NAME") or ImproperlyConfigured("CR_AWS_STORAGE_BUCKET_NAME not set")
    AWS_S3_ENDPOINT_URL = os.environ.get("CR_AWS_S3_ENDPOINT_URL") or ImproperlyConfigured("CR_AWS_S3_ENDPOINT_URL not set")



print("""\
                         ,&&&                                              
                    %@&@@@@@@@* %@@.  *.          
         /     &&  , (* &&&%%%&@@@@@#*@. @@%      
           .&&*   *(               *@&@@#@.@@@    
          %&&@ %     .* /#(,          *#@@@@%@@/  
   .&(  .&*&.,     *%*/,#/(/*/&/(       &&@@@@@@% 
   @@ ((&@% .     &&%..##(,/(/#&#.       @@@@@@@@,
  @@,%@@@# ,    .@/#/.#((/*///(&@%(/      @@@@@@@@
 *@@@@@&@#(     ,#%@&( .,/(/(((@@@@@     //%@@@@@@*
 #@&@@(#&@@. ,#/@%@@/(##%##%%%/@/& ,%(./*#%.@@@@@@#
 #@&@@.*&@#*...,*&&@(,&@&/(&%.(@&** . @ &@ #@@@@@@#
 /@@@@@&@@@%%@&@,(&@@@&#@@(*. &/% .#@%&@@ (@@@@@@@/
 ,(@@@@@@@@@   (&&@@(&%%&&%%%%#/.,&/@#  /%@@@@@@@@
  *@@@@@@@  @      @@#(&&%%%#%%@*&@.    @@@@@@@@@.
    @@@@@@@&        /@@@@%&%@@@%.    .@@@@@@@@@@  
     .%&@@@@@@@@@&.                 @%@&@@@@%@@   
        &@@@@@@@@@@@@@@         .@*&%@@@@@/@@     
           @@@@@@@@@@@@@       ,.* @@&%,#@@       
              @@@@@@@@&        ,/ .  *&@.
                                                """)

if os.environ.get("CAPROVER") is None:
    from .settings_dev import *
else:
    from .settings_caprover import *

