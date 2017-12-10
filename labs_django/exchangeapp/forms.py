# -*- coding: utf-8 -*-

from django import forms

# Local imports
from models import Currency


class DateInput(forms.widgets.TextInput):
    '''This widget uses the <input type="date" ... > from html5
    '''
    input_type = 'date'


class ExchangeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ExchangeForm, self).__init__(*args, **kwargs)

        currency_list = Currency.objects.all().order_by('code')
        currency_choices = [(x.code, '%s - %s' % (x.code, x.name_pt))
                            for x in currency_list]
        self.fields['from_currency'].choices = currency_choices
        self.fields['to_currency'].choices = currency_choices

    date = forms.DateTimeField(
        required=False,
        widget=DateInput())

    from_currency = forms.ChoiceField()
    to_currency = forms.ChoiceField()

    from_value = forms.FloatField()
