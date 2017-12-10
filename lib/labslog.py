# -*- coding: utf-8 -*-

'''Logging facilities'''

import sys
import os

sys.path.append(os.path.abspath('../labs_django'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'labs_django.settings'

from django.conf import settings

import logging


##
# Logging setup
##

# create logger
logger = logging.getLogger("labs_logger")
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.FileHandler(settings.LOGFILE)
ch.setLevel(logging.INFO)

consoleh = logging.StreamHandler(sys.stdout)
consoleh.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s")
formatter.datefmt = '%Y.%m.%d %H:%M:%S'

# add formatter to ch
ch.setFormatter(formatter)
consoleh.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)
logger.addHandler(consoleh)
