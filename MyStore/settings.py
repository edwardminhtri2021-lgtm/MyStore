from pathlib import Path
import os
from decouple import config
import dj_database_url
import django_heroku

# ================= BASE DIR =================
BASE_DIR = Path(__file__).resolve().parent.parent

# ================= SECURITY =================
from decouple import config

SECRET_KEY = config('SECRET_KEY', default='fallback-key')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost').split(',')


# ================= DATABASE =================
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",  # Windows-safe
        conn_max_age=600
    )
}

# ================= MEDIA =================
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

# ================= STATIC =================
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ================= ORDERS / CSV FILES =================
# Path to CSVs inside your repo
BASE_DIR = Path(__file__).resolve().parent.parent

MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

# Instead of D:\MyStore\media\analysis\csv...
ORDERS_FILE = BASE_DIR / 'analysis' / 'csv' / 'orders_items.csv'
VIEWS_FILE = BASE_DIR / 'analysis' / 'csv' / 'data_views.csv'
LIKES_FILE = BASE_DIR / 'analysis' / 'csv' / 'data_likes.csv'
RULES_FILE = BASE_DIR / 'analysis' / 'csv' / 'rules.csv'


# ================= APPLICATIONS =================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Your apps
    'store.apps.StoreConfig',
    'cart.apps.CartConfig',
    'orders.apps.OrdersConfig',
    'dashboard.apps.DashboardConfig',
    'storereport.apps.StorereportConfig',
    'analysis.apps.AnalysisConfig',

    # Third-party apps
    'ckeditor',
    'ckeditor_uploader',
    'django.contrib.humanize',
    'rest_framework',
    'storages',
]

# ================= MIDDLEWARE =================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serve static files efficiently
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'MyStore.urls'

# ================= TEMPLATES =================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'MyStore.wsgi.application'

# ================= PASSWORD VALIDATION =================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ================= INTERNATIONALIZATION =================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ================= CKEDITOR =================
CKEDITOR_BASEPATH = '/static/ckeditor/ckeditor/'
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_IMAGE_BACKEND = 'pillow'

# ================= AUTH =================
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/logout-success/'

# ================= AWS S3 (optional) =================
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
# AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
# AWS_QUERYSTRING_AUTH = False
# MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/'

# ================= DJANGO HEROKU =================
django_heroku.settings(locals())
