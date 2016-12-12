# -*- coding: utf-8 -*-

##
## Imports
##

import csv
import datetime
import os.path
import StringIO
import sys

# Append the current project path
sys.path.append(os.path.abspath('../lib/'))
sys.path.append(os.path.abspath('../labs_django/'))

os.environ['DJANGO_SETTINGS_MODULE'] = 'labs_django.settings'

from django.db.models import Max

import django
django.setup()

# Local
from exchangeapp.models import Currency, ExchangeRate
from labslog import logger
from mix_utils import fetch_url

##
## Configuration
##

BDP_SOURCE_URL = 'https://www.bportugal.pt/sites/default/files/taxas-relacionados/cambdia.csv'

##
## Utils
##

def latin_to_utf( st ):
    return st.decode('latin-1').encode('utf-8')

##
## Reader
##

class ExchangeReader( object ):
    def read_bdp_file(self):
        url, payload, cj = fetch_url( BDP_SOURCE_URL )
        return csv.reader( StringIO.StringIO( payload ), delimiter=';')

    def add_exchange(self, date, currency_st, value):
        currency = Currency.objects.get( name_pt = currency_st )

        exrate = ExchangeRate()
        exrate.date = date
        exrate.currency = currency
        exrate.value = value
        exrate.save()

    def run(self):
        csv = self.read_bdp_file()
        last_date = ExchangeRate.objects.all().aggregate(Max('date'))['date__max']
        logger.info('Getting exchange rates, last date: %s' % last_date )

        header = False
        for row in csv:
            if 'Período (Dias Úteis)' in latin_to_utf(row[0]):
                # Ignore begining of the file before data
                header = dict(list(enumerate( row )))
                continue
            if not header or not row[0]:
                # Ignore empty lines
                continue
            date = datetime.datetime.strptime( row[0], '%Y-%m-%d' ).date()
            if last_date and date <= last_date:
                # Ignore dates in the database
                continue

            # Add new exchange rates
            for i, cell in enumerate(row):
                try:
                    currency = unicode(header[i].split('/')[0].decode('latin-1')).strip()
                    self.add_exchange( date, currency, float(cell) )
                    logger.debug('Saving exchange rate: %s %s %s' % (date, currency, cell))
                except (ValueError, KeyError):
                    logger.debug('Error saving exchange rate: %s %s' % (currency, cell))


