from __future__ import unicode_literals
from django.db import models


class MeetingType(models.Model):
    name = models.CharField(max_length=64)


class Legislature(models.Model):
    number = models.CharField(max_length=4)


class Meeting(models.Model):
    date = models.DateField()
    number = models.IntegerField()
    attendance_bid = models.IntegerField()
    schedule_url = models.URLField()
    legistature = models.ForeignKey(Legislature)
    meeting_type = models.ForeignKey(MeetingType)

    class Meta:
        unique_together = ('date', 'number', 'legistature', 'meeting_type')


class Member(models.Model):
    name = models.CharField(max_length=64)
    mp_bid = models.IntegerField()


class Party(models.Model):
    name = models.CharField(max_length=32)


class Attendance(models.Model):
    meeting = models.ForeignKey(Meeting)
    member = models.ForeignKey(Member)
    party = models.ForeignKey(Party)
    status = models.CharField(max_length=64)
    reason = models.CharField(max_length=64)

    class Meta:
        unique_together = ('meeting', 'member')
