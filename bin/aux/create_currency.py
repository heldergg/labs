#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# Config

currency_list = (
    ('EUR', 'Euro', 'Euro'),
    ('AUD', 'Dólar australiano', 'Australian dollar'),
    ('BGN', 'Lev da Bulgária', 'Bulgarian Lev'),
    ('CAD', 'Dólar canadiano', 'Canadian dollar'),
    ('CHF', 'Franco suíço', 'Swiss franc'),
    ('CYP', 'Libra de Chipre', 'Cyprus pound'),
    ('CZK', 'Coroa checa', 'Czech koruna'),
    ('DKK', 'Coroa dinamarquesa', 'Danish krone'),
    ('EEK', 'Coroa da Estónia', 'Estonian kroon'),
    ('GBP', 'Libra esterlina', 'Sterling pound'),
    ('GRD', 'Dracma grega', 'Greek drachma'),
    ('HKD', 'Dólar de Hong-Kong', 'Hong-Kong Dollar'),
    ('HUF', 'Forint da Hungria', 'Hungarian forint'),
    ('ISK', 'Coroa islandesa', 'Iceland Krona'),
    ('JPY', 'Iene japonês', 'Japanese yen'),
    ('KRW', 'Won da Coreia do Sul', 'South Korea won'),
    ('LTL', 'Litas da Lituânia', 'Lithuanian litas'),
    ('LVL', 'Lats da Letónia', 'Latvian lats'),
    ('MTL', 'Lira de Malta', 'Maltese lira'),
    ('NOK', 'Coroa norueguesa', 'Norwegian krone'),
    ('NZD', 'Dólar da Nova Zelândia', 'New Zealand dollar'),
    ('PLN', 'Zloty da Polónia', 'Polish zloty'),
    ('RON', 'Novo Leu da Roménia', 'New Romanian leu'),
    ('SEK', 'Coroa sueca', 'Swedish krona'),
    ('SGD', 'Dólar de Singapura', 'Singapore dollar'),
    ('SIT', 'Tolar da Eslovénia', 'Slovenian tolar'),
    ('SKK', 'Coroa da Eslováquia', 'Slovak koruna'),
    ('TRY', 'Lira turca', 'Turkish lira'),
    ('USD', 'Dólar dos E.U.A.', 'US dollar'),
    ('ZAR', 'Rand da África do Sul', 'South African rand'),
    ('BRL', 'Real do Brasil', 'Brazilian real'),
    ('CVE', 'Escudo de Cabo Verde', 'Cape Verde escudo'),
    ('MOP', 'Pataca de Macau', 'Macau pataca'),
    ('XAU', 'Ouro em barra (onça troy)', 'Gold bullion (troy ounce)'),
    ('XDR', 'Direito de Saque Especial', 'Special Drawing Right'),
    ('CNY', 'Yuan Renmimbi da China', '(China) Yuan Renmimbi'),
    ('HRK', 'Kuna da Croácia', '(Croatia) Kuna'),
    ('IDR', 'Rupia Indonésia', 'Indonesian Rupiah'),
    ('MYR', 'Ringgit da Malásia', 'Malaysian Ringgit'),
    ('PHP', 'Peso Filipino', 'Philippines peso'),
    ('RUB', 'Rublo Russo', 'Russian Rouble'),
    ('THB', 'Baht da Tailândia', '(Thailand) Baht'),
    ('MXN', 'Peso mexicano', 'Mexican peso'),
    ('INR', 'Rupia indiana', 'Indian Rupee'),
    ('ILS', 'Shequel de Israel', 'Israeli Shekel'),
)

##
# Imports

import csv
import sys
import os.path
import datetime

sys.path.append(os.path.abspath('../../lib/'))
sys.path.append(os.path.abspath('../../labs_django/'))

os.environ['DJANGO_SETTINGS_MODULE'] = 'labs_django.settings'

import django
django.setup()

from exchangeapp.models import Currency


for curreny in currency_list:
    c = Currency()
    c.code = curreny[0]
    c.name_pt = curreny[1]
    c.name_en = curreny[2]
    c.save()
