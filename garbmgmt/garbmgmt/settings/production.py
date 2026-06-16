import os
from .base import *

# Production-specific settings
DEBUG = False

# SECRET_KEY must be set in environment for production
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise RuntimeError('DJANGO_SECRET_KEY environment variable must be set in production')

# ALLOWED_HOSTS must be provided as comma-separated list
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',') if os.environ.get('DJANGO_ALLOWED_HOSTS') else []
if not ALLOWED_HOSTS:
    raise RuntimeError('DJANGO_ALLOWED_HOSTS must be set in production (comma-separated)')

# Database: allow explicit production overrides
DATABASES['default'] = {
    'ENGINE': os.environ.get('DJANGO_DB_ENGINE', DATABASES['default']['ENGINE']),
    'NAME': os.environ.get('DJANGO_DB_NAME', DATABASES['default']['NAME']),
    'USER': os.environ.get('DJANGO_DB_USER', DATABASES['default']['USER']),
    'PASSWORD': os.environ.get('DJANGO_DB_PASSWORD', DATABASES['default']['PASSWORD']),
    'HOST': os.environ.get('DJANGO_DB_HOST', DATABASES['default']['HOST']),
    'PORT': os.environ.get('DJANGO_DB_PORT', DATABASES['default']['PORT']),
    'OPTIONS': DATABASES['default'].get('OPTIONS', {}),
}

# Security hardening
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_SSL_REDIRECT = os.environ.get('DJANGO_SECURE_SSL_REDIRECT', 'True') == 'True'
SECURE_HSTS_SECONDS = int(os.environ.get('DJANGO_HSTS_SECONDS', '31536000'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.environ.get('DJANGO_HSTS_INCLUDE_SUBDOMAINS', 'True') == 'True'
SECURE_HSTS_PRELOAD = os.environ.get('DJANGO_HSTS_PRELOAD', 'True') == 'True'

# Logging: minimal production logging to console; container platforms can capture this
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
    },
}
