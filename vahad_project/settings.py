"""
Django settings for vahad_project project.
VAHAD – Tourist Management System (VAHAD-TMS)
"""
import os
import sys
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file if it exists
load_dotenv(BASE_DIR / '.env')

# Check if running in a serverless cloud environment (Vercel, AWS Lambda, etc.)
IS_SERVERLESS = bool(
    os.environ.get('VERCEL') or 
    os.environ.get('AWS_LAMBDA_FUNCTION_NAME') or 
    os.environ.get('NOW_REGION')
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False' if not IS_SERVERLESS else 'False').lower() in ('true', '1', 'yes')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    # Deterministic fallback key for serverless / testing if environment variable is omitted
    SECRET_KEY = 'django-insecure-vahad-tms-production-cloud-key-for-serverless-deployments-893149'

# Allowed Hosts Configuration (Auto-allow Vercel, Render, Railway, localhost)
allowed_hosts_env = os.environ.get('ALLOWED_HOSTS', '')
if allowed_hosts_env:
    if allowed_hosts_env.strip() == '*':
        ALLOWED_HOSTS = ['*']
    else:
        ALLOWED_HOSTS = [h.strip() for h in allowed_hosts_env.split(',') if h.strip()]
else:
    ALLOWED_HOSTS = [
        '*',  # Permissive for serverless domains (Vercel, Render, Railway, etc.)
        'localhost',
        '127.0.0.1',
        '[::1]',
        '.vercel.app',
        '.onrender.com',
        '.railway.app',
    ]

# CSRF Trusted Origins for HTTPS cloud deployments (Render, Railway, Vercel, Fly.io, etc.)
csrf_trusted_env = os.environ.get('CSRF_TRUSTED_ORIGINS', '')
if csrf_trusted_env:
    CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in csrf_trusted_env.split(',') if origin.strip()]
else:
    CSRF_TRUSTED_ORIGINS = [
        'http://localhost:8000',
        'http://127.0.0.1:8000',
        'https://*.vercel.app',
        'https://*.onrender.com',
        'https://*.railway.app',
    ]

# Proxy SSL Header (Essential for reverse proxies / load balancers on cloud hosts)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Authentication URLs
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'vahad_app',
    'crispy_forms',
    'crispy_bootstrap5',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'vahad_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'vahad_app' / 'templates',
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'vahad_app.context_processors.locations_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'vahad_project.wsgi.application'

# Database Configuration (Multi-Tier: DATABASE_URL -> MySQL env vars -> SQLite)
try:
    import dj_database_url
except ImportError:
    dj_database_url = None

DATABASE_URL = os.environ.get('DATABASE_URL')
USE_SQLITE = os.environ.get('USE_SQLITE', '').lower() in ('true', '1', 'yes')
DB_ENGINE = os.environ.get('DB_ENGINE', '').lower()

# On Vercel / serverless, copy SQLite database to writable /tmp directory
if IS_SERVERLESS:
    temp_db = Path('/tmp/db.sqlite3')
    orig_db = BASE_DIR / 'db.sqlite3'
    if not temp_db.exists() and orig_db.exists():
        try:
            shutil.copyfile(orig_db, temp_db)
        except Exception:
            pass
    sqlite_path = temp_db
else:
    sqlite_path = BASE_DIR / 'db.sqlite3'

if DATABASE_URL and dj_database_url:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600, ssl_require=not DEBUG)
    }
elif DB_ENGINE in ('mysql', 'mariadb') or (os.environ.get('DB_NAME') and not USE_SQLITE and not IS_SERVERLESS):
    db_name = os.environ.get('DB_NAME', 'Vahadtms')
    db_user = os.environ.get('DB_USER', 'root')
    db_password = os.environ.get('DB_PASSWORD', '')
    db_host = os.environ.get('DB_HOST', '127.0.0.1')
    db_port = os.environ.get('DB_PORT', '3306')
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': db_name,
            'USER': db_user,
            'PASSWORD': db_password,
            'HOST': db_host,
            'PORT': db_port,
            'OPTIONS': {
                'charset': 'utf8mb4',
            }
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': sqlite_path,
        }
    }

# Password validation
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

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static & Media files
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

WHITENOISE_MANIFEST_STRICT = False

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

MEDIA_URL = '/media/'
if IS_SERVERLESS:
    MEDIA_ROOT = Path('/tmp/media')
    orig_media = BASE_DIR / 'media'
    if orig_media.exists() and not MEDIA_ROOT.exists():
        try:
            shutil.copytree(orig_media, MEDIA_ROOT, dirs_exist_ok=True)
        except Exception:
            pass
else:
    MEDIA_ROOT = BASE_DIR / 'media'

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Production Security Hardening
if not DEBUG and not IS_SERVERLESS:
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() in ('true', '1', 'yes')
    CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'False').lower() in ('true', '1', 'yes')
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    
    if os.environ.get('SECURE_SSL_REDIRECT', '').lower() in ('true', '1', 'yes'):
        SECURE_SSL_REDIRECT = True
    
    hsts_seconds = int(os.environ.get('SECURE_HSTS_SECONDS', '0'))
    if hsts_seconds > 0:
        SECURE_HSTS_SECONDS = hsts_seconds
        SECURE_HSTS_INCLUDE_SUBDOMAINS = os.environ.get('SECURE_HSTS_INCLUDE_SUBDOMAINS', 'False').lower() in ('true', '1', 'yes')
        SECURE_HSTS_PRELOAD = os.environ.get('SECURE_HSTS_PRELOAD', 'False').lower() in ('true', '1', 'yes')
