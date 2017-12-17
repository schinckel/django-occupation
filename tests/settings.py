import os
import django

USE_TZ = True

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'boardinghouse',
    'boardinghouse.contrib.template',
    'boardinghouse.contrib.demo',
    'django.contrib.admin',
    # 'boardinghouse.contrib.invite',
    'tests',
]

DATABASES = {
    "default": {
        'ENGINE': 'boardinghouse.backends.postgres',
        'NAME': 'boardinghouse-{DB_NAME}'.format(**os.environ),
        'USER': os.environ.get('DB_USER'),
        'PORT': os.environ.get('DB_PORT', 5432),
    }
}

ROOT_URLCONF = 'tests.urls'
STATIC_URL = '/static/'

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'boardinghouse.middleware.SchemaMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)
if django.VERSION < (1, 10):
    MIDDLEWARE_CLASSES = MIDDLEWARE
    del MIDDLEWARE

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)
AUTH_USER_MODEL = 'auth.User'
SECRET_KEY = 'django-boardinghouse-sekret-keye'
TEST_RUNNER = 'rainbowtests.test.runner.RainbowDiscoverRunner'

# These locations are different for 1.7 and 1.8+ (-> TEMPLATES)
if django.VERSION < (1, 9):
    TEMPLATE_CONTEXT_PROCESSORS = [
        'django.contrib.auth.context_processors.auth',
        'django.core.context_processors.debug',
        'django.core.context_processors.i18n',
        'django.core.context_processors.media',
        'django.core.context_processors.static',
        'django.core.context_processors.tz',
        'django.contrib.messages.context_processors.messages',
        'boardinghouse.context_processors.schemata',
    ]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'boardinghouse.context_processors.schemata',
            ]
        }
    },
]

SHARED_MODELS = ['tests.SettingsSharedModel']
PRIVATE_MODELS = ['tests.SettingsPrivateModel']
