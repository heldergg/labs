# -*- coding: utf-8 -*-

##
## DEBUG
##

DEBUG = False
TEMPLATE_DEBUG = DEBUG


##
## BASE PATHS
##

import os.path
project_dir = os.path.abspath ( os.path.join( os.path.dirname( __file__ ), '../..' ))
django_dir = os.path.abspath ( os.path.join( os.path.dirname( __file__ ), '..' ))

##
## Site admins
##

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

##
## Databases
##

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'mysql',
                                         # 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using
                                         # sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain
                                         # sockets or '127.0.0.1' for localhost
                                         # through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

##
## HTTP
##

ALLOWED_HOSTS = []
SITE_ID = 1
SECRET_KEY = 'qvzx6=g4h7*&cyvaf!=l_n@#hzk&8kre*(yns*10$@n7@@@$ok'

##
## Lang and timezone:
##

TIME_ZONE = 'Europe/Lisbon'
LANGUAGE_CODE = 'pt-PT'
USE_I18N = True
USE_L10N = True
USE_TZ = True

##
## Media and files
##

MEDIA_ROOT = ''             # User uploaded files (abs path)
MEDIA_URL = ''              # URL that serves MEDIA_ROOT files (end with '/')
STATIC_ROOT = os.path.join( project_dir, 'collected_static' )
STATIC_URL = '/static/'     # Prefix for static files
STATICFILES_DIRS = (        # Additional locations of static files
    os.path.join(django_dir, 'static'),
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)


##
## Templates
##

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

ROOT_URLCONF = 'labs_django.urls'

TEMPLATE_DIRS = (
    os.path.join( django_dir, 'templates'),
)

##
## Application
##

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
#    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
#    'django.core.context_processors.request',
)

WSGI_APPLICATION = 'labs_django.wsgi.application'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Index app
    'indexapp',

    # HC app
    'hcapp',

    # Money converter app
    'exchangeapp',

    # Money devaluation app
    'devaluationapp',

    # Potuguese MP time sheet
    'timeclockapp',

)

##
## Logging
##

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

LOGDIR  = os.path.join(project_dir, 'log')
LOGFILE = os.path.join(LOGDIR, 'dre.log' )

##
## LOCAL
##

try:
    from local_settings import *
except ImportError:
    pass
