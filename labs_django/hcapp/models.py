# -*- coding: utf-8 -*-

from django.db import models


class Party(models.Model):
    name = models.CharField(max_length=128)
    initials = models.CharField(max_length=64, unique=True)

    wikipedia = models.CharField(max_length=128, null=True)
    tendency = models.CharField(max_length=64)

    order = models.IntegerField()

    color_1 = models.CharField(max_length=32)
    color_2 = models.CharField(max_length=32)


class District(models.Model):
    name = models.CharField(max_length=64)
    code = models.IntegerField(unique=True)

    def __str__(self):
        return 'District object: %s' % self.name


class ElectionResult(models.Model):
    district = models.ForeignKey(District)
    party = models.ForeignKey(Party)

    election_type = models.CharField(max_length=24)
    date = models.DateField()
    votes = models.IntegerField()

    # The next columns will be used in testing
    vote_percent = models.FloatField()
    seats = models.IntegerField()

    class Meta:
        unique_together = ('district', 'party', 'election_type', 'date')


class ElectionStats(models.Model):
    district = models.ForeignKey(District)

    date = models.DateField()

    registered_voters = models.IntegerField()
    voters = models.IntegerField()
    blank_voters = models.IntegerField()
    invalid_votes = models.IntegerField()

    class Meta:
        unique_together = ('district', 'date')
