# flake8: noqa
import os
from pathlib import Path

from django.contrib.auth import get_user_model
from dotenv import load_dotenv


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'default-secret-key')

DEBUG = os.getenv('DEBUG_MODE', False)

ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost 127.0.0.1').split()

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'debug_toolbar',
    'rest_framework',
    'djoser',
    'rest_framework.authtoken',
    'corsheaders',
    'django_filters',
    'recipes.apps.RecipesConfig',
    'api.apps.ApiConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

CSRF_TRUSTED_ORIGINS=os.getenv('CSRF_TRUSTED', 'http://localhost').split()

INTERNAL_IPS = [
    '127.0.0.1',
]

CORS_URLS_REGEX = r'^/api/.*$'
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
]


ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'


DB_TYPE_POSTGRES = {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': os.getenv('POSTGRES_DB', 'django'),
    'USER': os.getenv('POSTGRES_USER', 'django'),
    'PASSWORD': os.getenv('POSTGRES_PASSWORD', ''),
    'HOST': os.getenv('DB_HOST', ''),
    'PORT': os.getenv('DB_PORT', 5432)
}
DB_TYPE_SQLITE = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': BASE_DIR / 'db.sqlite3',
}

DATABASES = {
    'default': DB_TYPE_POSTGRES if os.getenv('DB_PROD_TYPE', False) else DB_TYPE_SQLITE
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'ru-Ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'collected_static'


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


AUTH_USER_MODEL = 'recipes.FoodgramUser'


DJOSER = {
    'SERIALIZERS': {'user': 'api.serializers.FoodgramUserSerializer',
                    'current_user': 'api.serializers.FoodgramUserSerializer',},
    'PERMISSIONS': {
        'user': ['rest_framework.permissions.AllowAny'],
        'user_list': ['rest_framework.permissions.AllowAny'],
    },
    'HIDE_USERS': False,
}


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'api.pagination.QueryPageNumberPagination',
    'PAGE_SIZE': 6,
    'DEFAULT_THROTTLE_RATES': {
        'user': '10000/day',
        'anon': '1000/day',
    }
}
