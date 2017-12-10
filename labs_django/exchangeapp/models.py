# -*- coding: utf-8 -*-

from django.db import models


class Currency(models.Model):
    code = models.CharField(max_length=3, primary_key=True)  # ISO 4217 code
    name_pt = models.CharField(max_length=32)
    name_en = models.CharField(max_length=32)


class ExchangeRate(models.Model):
    date = models.DateField()
    currency = models.ForeignKey(Currency)
    value = models.FloatField()

    class Meta:
        unique_together = ('currency', 'date')
