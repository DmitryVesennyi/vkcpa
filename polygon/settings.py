# -*- coding: utf-8 -*-
"""
Django settings for polygon project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'z#oygxkfdqq%hh+bf_9t^6xx3$j%78=9ii#s@vnnoe3+r*ah6d'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '37.1.194.157', 'livsa.ru']

ADMINS = ((u'JackSparrow', 'press.83@list.ru'), )

EMAIL_USE_TLS = True

EMAIL_HOST = 'smtp.gmail.com'

EMAIL_PORT = 587

EMAIL_HOST_USER = 'vk.vot.bot@gmail.com'

EMAIL_HOST_PASSWORD = 'VITksfJ47U0kXpmzbIT6'

SERVER_EMAIL = EMAIL_HOST_USER
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'vkcpa',
    'exeption_info',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'polygon.urls'

WSGI_APPLICATION = 'polygon.wsgi.application'

TEMPLATE_DIRS = (os.path.join(BASE_DIR, 'templates'), )


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'django',
        'USER': 'django',
        'PASSWORD': 'Q3q5C3x1',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#    }
#}


# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

#SESSION_EXPIRE_AT_BROWSER_CLOSE = True

SESSION_COOKIE_HTTPONLY = True

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static_files')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATICFILES_FINDERS = ("django.contrib.staticfiles.finders.FileSystemFinder",
"django.contrib.staticfiles.finders.AppDirectoriesFinder")

STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'), )

LOGGING = {
      'version': 1,
      'handlers': {
      'console': {
      'level': 'DEBUG',
      'class': 'logging.StreamHandler',
},
'file': {
'level': 'DEBUG',
'class': 'logging.FileHandler',
'filename': os.path.join(BASE_DIR,
'debug.log'),
},
},
'loggers': {
'students': {#тут пишется имя стартаппа
'handlers': ['console', 'file'],
'level': 'DEBUG',
},},}
