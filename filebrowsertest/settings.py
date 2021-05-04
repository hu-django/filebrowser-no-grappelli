"""
Django settings for my project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(__file__)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-----------'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'filebrowser',
    'filebrowsertest.app'
)

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    },
]

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

ROOT_URLCONF = 'filebrowsertest.urls'

WSGI_APPLICATION = 'filebrowsertest.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

MEDIA_URL = '/media/'

MEDIA_ROOT = "media"

STATIC_URL = '/static/'

STATIC_ROOT = "static"

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

FILEBROWSER_MEDIA_ROOT = MEDIA_ROOT
FILEBROWSER_DIRECTORY = ''

FILEBROWSER_VERSIONS = {
    'fb_thumb': {'verbose_name': 'Admin Thumbnail', 'width': 60, 'height': 60, 'opts': 'crop'},
    'small_index': {'verbose_name': 'Smaill index', 'width': 80, 'height': 60, 'opts': 'upscale'},
    'small_ix_crop': {'verbose_name': 'Smaill index crop', 'width': 80, 'height': 60, 'opts': 'upscale crop'},
    'index': {'verbose_name': 'Index', 'width': 300, 'height': 225, 'opts': 'upscale'},
    '_gal_ix': {'verbose_name': 'Gallery index', 'width': 150, 'height': 113, 'opts': ''},
    'cr_gal_ix': {'verbose_name': 'Gallery index cropped', 'width': 113, 'height': 113, 'opts': 'crop'},
    'fh_gal_ix': {'verbose_name': 'Gallery index full height', 'width': 113, 'height': 113, 'opts': ''},
    'gallery': {'verbose_name': 'Gallery item', 'width': 800, 'height': 800, 'opts': ''},
}

FILEBROWSER_ADMIN_VERSIONS = ['small_index', 'small_ix_crop', 'index', 'cr_gal_ix', 'fh_gal_ix', '_gal_ix', 'gallery']