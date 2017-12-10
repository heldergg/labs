# -*- coding: utf-8 -*-

# Global imports
import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max
from django.shortcuts import render_to_response
from django.template import RequestContext

# Local imports
from forms import ExchangeForm
from models import ExchangeRate, Currency

##
# Views
##


def get_exchange(date, currency):
    msg = []
    if currency.code == 'EUR':
        return 1.0, msg

    invert = False
    if currency.code in ('XAU', 'XDR'):
        invert = True

    # Try to get the exchange rate for date and currency
    try:
        value = ExchangeRate.objects.get(currency=currency, date=date).value
    except ObjectDoesNotExist:
        msg += [u'Não encontrei o câmbio para %s na data indicada' % currency.name_pt]
        near_rate = ExchangeRate.objects.filter(currency__exact=currency
                                                ).filter(date__lte=date).order_by('-date')[0]
        msg += [u'Vou usar a cotação de dia %s, 1 EUR = %.3f %s' % (
            near_rate.date.isoformat(),
            near_rate.value,
            near_rate.currency.code)]
        value = near_rate.value

    if invert:
        value = 1 / value

    return value, msg


def calc(date, from_currency, to_currency, value):
    msg = []

    fc_eur, m = get_exchange(date, from_currency)
    msg += m
    tc_eur, m = get_exchange(date, to_currency)

    msg += m

    return tc_eur / fc_eur * value, msg


def exchange_calc(request):
    context = {}

    f = ExchangeForm(request.GET)
    is_valid = f.is_valid()

    # Date handling
    date = request.GET.get('date', None)
    try:
        date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        date = None
    if not date:
        date = ExchangeRate.objects.all().aggregate(Max('date'))['date__max']

    # Form currency
    from_currency = request.GET.get('from_currency', None)
    try:
        from_currency = Currency.objects.get(code=from_currency)
    except ObjectDoesNotExist:
        from_currency = Currency.objects.get(code='EUR')

    # To currency
    to_currency = request.GET.get('to_currency', None)
    try:
        to_currency = Currency.objects.get(code=to_currency)
    except ObjectDoesNotExist:
        to_currency = Currency.objects.get(code='USD')

    # submit type
    switch = request.GET.get('submit', '') == 'switch'
    if switch:
        from_currency, to_currency = to_currency, from_currency

    # From value
    from_value = request.GET.get('from_value', 0.0)
    try:
        from_value = float(from_value)
    except ValueError:
        from_value = float(0.0)

    form = ExchangeForm({
        'date': date,
        'from_currency': from_currency.code,
        'to_currency': to_currency.code,
        'from_value': '%0.4f' % from_value,
    })
    context['form'] = form

    context['to_value_1'], msg = calc(date, from_currency, to_currency, 1.0)
    context['to_value'], msg = calc(date, from_currency, to_currency, from_value)

    context['msg'] = msg

    return render_to_response('exchange_calc.html', context,
                              context_instance=RequestContext(request))
