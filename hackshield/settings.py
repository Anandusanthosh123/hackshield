"""
Django settings for hackshield project.
"""

from pathlib import Path

# -------------------------------------------------
# Build paths
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------------------------
# SECURITY
# -------------------------------------------------
SECRET_KEY = 'YOUR KEY '

# Development only – turn off in production
DEBUG = True

# **MUST BE A LIST**
ALLOWED_HOSTS = ['localhost', '127.0.0.1',]

# -------------------------------------------------
# Application definition
# -------------------------------------------------
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Your app
    'core',

    # Optional 2FA
    'django_otp',
    'django_otp.plugins.otp_totp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',      # <-- 2FA middleware
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.DisableClientCacheMiddleware'
]

ROOT_URLCONF = 'hackshield.urls'

# -------------------------------------------------
# Templates
# -------------------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],          # <-- project-wide templates
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

WSGI_APPLICATION = 'hackshield.wsgi.application'


# -------------------------------------------------
# Database (MySQL)
# -------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'hackshield',
        'USER': 'root',
        'PASSWORD': 'Admin@123',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}

# -------------------------------------------------
# Password validation
# -------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -------------------------------------------------
# Internationalisation
# -------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# -------------------------------------------------
# Static & Media files
# -------------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # For collectstatic in production

# Only add STATICFILES_DIRS if folder exists
import os
if os.path.exists(BASE_DIR / 'static'):
    STATICFILES_DIRS = [BASE_DIR / 'static']           # for collectstatic in prod

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# -------------------------------------------------
# Default primary key
# -------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -------------------------------------------------
# Custom User Model (core.CustomUser)
# -------------------------------------------------
AUTH_USER_MODEL = 'core.CustomUser'

# -------------------------------------------------
# Security headers (dev-only – will be overridden in prod)
# -------------------------------------------------
SECURE_SSL_REDIRECT = False          # set True only in production
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
X_FRAME_OPTIONS = 'DENY'

## At the end
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'


# CELERY CONFIG — REDIS ONLY
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_ENABLE_UTC = True

DOCKER_SOCK = "npipe:////./pipe/docker_engine"

# ===============================
# JAZZMIN ADMIN THEME SETTINGS
# ===============================

JAZZMIN_SETTINGS = {
    "site_title": "HackShield Admin",
    "site_header": "HackShield",
    "site_brand": "HackShield",
    "welcome_sign": "Welcome to HackShield Control Panel",

    # Logos (optional)
    # "site_logo": "images/logo.png",
    # "login_logo": "images/logo.png",

    "site_icon": "⚔️",

    # Top Menu
    "topmenu_links": [
        {"name": "Dashboard", "url": "admin:index"},
        {"name": "Main Site", "url": "/", "new_window": True},
    ],

    # Sidebar
    "show_sidebar": True,
    "navigation_expanded": True,

    # Icons for apps/models
    "icons": {
        "auth": "fas fa-users",
        "auth.user": "fas fa-user",

        "core.CustomUser": "fas fa-user-shield",
        "core.Course": "fas fa-graduation-cap",
        "core.Lesson": "fas fa-book",
        "core.UserCourseProgress": "fas fa-chart-line",

        "core.CourseQuizQuestion": "fas fa-question-circle",
        "core.CourseQuizAttempt": "fas fa-clipboard-check",

        "core.Certificate": "fas fa-certificate",
        "core.Challenge": "fas fa-flag",
        "core.HackingLab": "fas fa-terminal",
    },

    # Default icons
    "default_icon_parents": "fas fa-folder",
    "default_icon_children": "fas fa-file",

    # Theme
    "theme": "darkly",   # 🔥 Dark mode by default
}
# ----------------------------------
# EMAIL CONFIG (GMAIL SMTP)
# ----------------------------------

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = 'anandusanthosh1official@gmail.com'
EMAIL_HOST_PASSWORD = 'dwgz dklr qzbe iaze'

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
PASSWORD_RESET_TIMEOUT = 3600
