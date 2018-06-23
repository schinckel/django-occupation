import os

USE_TZ = True

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'occupation',
    # 'boardinghouse.contrib.template',
    # 'boardinghouse.contrib.demo',
    'django.contrib.admin',
    'tests',
]

DATABASES = {
    "default": {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'occupation'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASS'),
        'PORT': os.environ.get('DB_PORT', 5432),
    }
}

ROOT_URLCONF = 'tests.urls'
STATIC_URL = '/static/'

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'occupation.middleware.SelectTenant',
    'occupation.middleware.ActivateTenant',

)

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)
AUTH_USER_MODEL = 'auth.User'
SECRET_KEY = 'django-occupataion-sekret-keye'


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
                'occupation.context_processors.tenants',
            ]
        }
    },
]

# SHARED_MODELS = ['tests.SettingsSharedModel']
# PRIVATE_MODELS = ['tests.SettingsPrivateModel']
