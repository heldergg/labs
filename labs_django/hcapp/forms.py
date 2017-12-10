# -*- coding: utf-8 -*-

"""Project forms"""

# Global imports:
from django import forms

# Local imports:
from models import ElectionResult

date_choices = [(date['date'].isoformat(), date['date'].isoformat())
                for date in ElectionResult.objects.all().values('date').distinct().order_by('date')]


class ElectionForm(forms.Form):

    date = forms.ChoiceField(
        label='Eleição de ',
        choices=date_choices,
    )

    uni = forms.ChoiceField(
        label='Distribuição por',
        choices=(
            ('M', 'círculos eleitorais'),
            ('U', 'um circulo eleitoral único')
        ),
    )

    national_circle = forms.IntegerField(
        label='Circulo Nacional',
        min_value=0,
        max_value=1000,
    )

    seats = forms.IntegerField(
        label='Assentos',
        min_value=10,
        max_value=1000,
    )

    def clean(self):
        cleaned_data = super(ElectionForm, self).clean()

        national_circle = cleaned_data.get('national_circle')
        seats = cleaned_data.get('seats')

        if national_circle > (seats - 10):
            raise forms.ValidationError(
                'O número de assentos no circulo nacional tem de ser menor ou igual ao número total de assentos menos 10.')

        return cleaned_data
