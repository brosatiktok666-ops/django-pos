"""
Django settings for posdb project.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-+yhezzyjj!u%_l=oh=257ijxtle(=xynw%8kyz%!bmv=iai0fx'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['mrrin-django-pos.onrender.com', 'localhost', '127.0.0.1']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'sales',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # <-- បងបានថែមជួរនេះនៅទីនេះ
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'posdb.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'posdb.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Phnom_Penh' # ប្តូរមកម៉ោងនៅស្រុកខ្មែរ
USE_I18N = True
USE_TZ = True

# --- ការកំណត់ Static Files (CSS, JavaScript, Images, Fonts) ---
STATIC_URL = 'static/'

# ប្ដូរមកប្រើទម្រង់ STORAGES ថ្មីនេះវិញ ដើម្បីកុំឱ្យ Render ចាប់កំហុសពេល Build
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# ប្រាប់ Django ឱ្យរកមើល File ក្នុង Folder static ធំនៃ Project
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# ទីតាំងសម្រាប់ប្រមូលផ្តុំ Static ពេល Deploy
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# --- ការកំណត់ Media Files (រូបភាពផលិតផល) ---
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# --- ការកំណត់ការ Login/Logout ---
LOGIN_REDIRECT_URL  = '/sales/products/'
LOGOUT_REDIRECT_URL = '/accounts/login/'