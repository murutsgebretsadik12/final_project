"""
Django settings for patrick_garage project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from dotenv import load_dotenv
load_dotenv()

import os, certifi
import dj_database_url
from pathlib import Path



# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
DEBUG = os.environ.get("DEBUG", "False").lower() == 'true'


ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(" ")
ALLOWED_HOSTS = ['final-project-patrick-garage.onrender.com']
ALLOWED_HOSTS = ['final-project-patrick-garage.onrender.com', 'localhost 127.0.0.1 [::1]']


ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'final-project-patrick-garage.onrender.com',
]


# Application definition

INSTALLED_APPS = [
    'vehicle.apps.VehicleConfig',#added
    "crispy_forms", #Updated here
    "crispy_bootstrap5", #Updated here
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
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

ROOT_URLCONF = 'patrick_garage.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'patrick_garage.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

database_url = os.environ.get("DATABASE_URL")
DATABASES["default"]= dj_database_url.parse(database_url)

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = 'bootstrap5'


# MEDIA_ROOT = BASE_DIR / 'media' # Newer modern and Pythonic way, to store uploaded files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
#ˇpython manage.py collectstatic ---run the commanad to look the change on static files--

# Additional locations of static files
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'vehicle/static'),
]


LOGIN_REDIRECT_URL = 'customerclick'# to redirect to home page while login


LOGIN_REDIRECT_URL = 'adminclick'  # Redirect to this URL after login
LOGOUT_REDIRECT_URL = 'vehiclehome'  # Redirect to this URL after logout

LOGIN_URL = 'adminlogin'

LOGIN_URL='customer-dashboard'





