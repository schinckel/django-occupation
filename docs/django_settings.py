"""
Django settings for demo_project project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from typing import List

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

import django  # NOQA

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "c^3@9lyia%1ckn*mbdtu$l%+w#-+=(1zdpmdq=@d@1fc88(ka3"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS: List[str] = []


# Application definition

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "occupation",
    "django.contrib.admin",
)

MIDDLEWARE_CLASSES = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
)

ROOT_URLCONF = "occupation.test.urls"

WSGI_APPLICATION = "occupation.test.wsgi.application"


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {"default": {"ENGINE": "django.db.backends.postgresql", "NAME": "occupation-docs"}}


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = "/static/"


TEMPLATE_DIRS = (os.path.join(BASE_DIR, "templates"),)

PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)

COVERAGE_REPORT_HTML_OUTPUT_DIR = os.path.join(BASE_DIR, ".coverage")
COVERAGE_USE_STDOUT = True
COVERAGE_PATH_EXCLUDES = [".hg", "templates", "tests", "sql", "__pycache__"]
