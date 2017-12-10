# -*- coding: utf-8 -*-

from django import forms


class DevalForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(DevalForm, self).__init__(*args, **kwargs)

    year_0 = forms.IntegerField(min_value=1903, max_value=2015)
    year_1 = forms.IntegerField(min_value=1903, max_value=2015)

    value = forms.FloatField(min_value=0.0)
