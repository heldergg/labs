#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Tretas.org maintenance scripts
'''

# Imports

import getopt
import sys
import os.path

sys.path.append(os.path.abspath('../lib/'))
sys.path.append(os.path.abspath('../labs_django/'))

os.environ['DJANGO_SETTINGS_MODULE'] = 'labs_django.settings'

import django
django.setup()


def usage():
    print '''Usage: %(script_name)s [options]\n
    Commands:
        --export_time_sheet <file name>
                            Export MP's time sheet data to CSV
        --read_time_sheet   Read the MP's time sheet
        --update_time_sheet Update the MP's time sheet
        --read_change       Read the exchange rates from BdP

        -h
        --help              This help screen

    Option:
        --verbose           Verbose output
    ''' % {'script_name': sys.argv[0]}


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   'hv',
                                   ['help',
                                    'read_change',
                                    'export_time_sheet=',
                                    'read_time_sheet',
                                    'update_time_sheet',
                                    'verbose',
                                    ])
    except getopt.GetoptError, err:
        print str(err)
        print
        usage()
        sys.exit(1)

    # Defaults
    verbose = False

    # Options
    for o, a in opts:
        if o in ('-v', '--verbose'):
            verbose = True

    # Commands
    for o, a in opts:
        if o == '--read_change':
            from exchange_reader import ExchangeReader

            reader = ExchangeReader()
            reader.run()

            sys.exit()

        elif o == '--read_time_sheet' or o == '--update_time_sheet':
            import parlamento.scraper
            from parlamento.scraper import ParlamentoIndex, attendance_read
            from timeclockapp.models import (
                MeetingType,
                Legislature,
                Meeting,
                Member,
                Party,
                Attendance)
            from django.core.exceptions import ObjectDoesNotExist
            from django.db import IntegrityError

            update = o == '--update_time_sheet'
            parlamento.scraper.verbose = verbose

            for meeting_data in ParlamentoIndex().meetings():
                # Process meeting
                try:
                    legislature = Legislature.objects.get(
                        number=meeting_data['legislature'])
                except ObjectDoesNotExist:
                    legislature = Legislature(number=meeting_data['legislature'])
                    legislature.save()
                try:
                    meeting_type = MeetingType.objects.get(
                        name=meeting_data['type'])
                except ObjectDoesNotExist:
                    meeting_type = MeetingType(name=meeting_data['type'])
                    meeting_type.save()
                try:
                    meeting = Meeting(
                        date=meeting_data['date'],
                        number=meeting_data['number'],
                        attendance_bid=meeting_data['attendance_bid'],
                        schedule_url=meeting_data['schedule_url'])
                    meeting.legistature = legislature
                    meeting.meeting_type = meeting_type
                    meeting.save()
                    if verbose:
                        print('Reading %s meeting' % meeting_data['date'])
                except IntegrityError:
                    meeting = Meeting.objects.get(
                        date=meeting_data['date'],
                        legistature=legislature,
                        number=meeting_data['number'],
                        meeting_type=meeting_type)
                    if verbose:
                        print('Skipping %s meeting' % meeting.date.isoformat())
                    if verbose and update:
                        print('Update done')
                    # If updating, terminate on the first repeated record
                    if update:
                        break
                    continue

                for mp in attendance_read(meeting_data):
                    # Process MP attendace
                    try:
                        member = Member.objects.get(mp_bid=mp['mp_bid'])
                    except ObjectDoesNotExist:
                        member = Member(
                            name=mp['name'], mp_bid=mp['mp_bid'])
                        member.save()
                    try:
                        party = Party.objects.get(name=mp['party'])
                    except ObjectDoesNotExist:
                        party = Party(name=mp['party'])
                        party.save()
                    try:
                        attendance = Attendance()
                        attendance.member = member
                        attendance.meeting = meeting
                        attendance.party = party
                        attendance.status = mp['status']
                        attendance.reason = mp['reason']
                        attendance.save()
                    except IntegrityError:
                        pass
                if verbose:
                    print('Done')
            sys.exit()

        elif o == '--export_time_sheet':
            from timeclockapp.models import Meeting, Attendance
            from mix_utils import UnicodeWriter
            import csv

            with open(a, 'w') as csvfile:
                writer = UnicodeWriter(csvfile, quoting=csv.QUOTE_MINIMAL)
                queryset = Attendance.objects.all().order_by('meeting__date')
                queryset = queryset.select_related('meeting__date')
                queryset = queryset.select_related('meeting__number')
                queryset = queryset.select_related('meeting__attendance_bid')
                queryset = queryset.select_related('meeting__meeting_type__name')
                queryset = queryset.select_related('member__name')
                queryset = queryset.select_related('member__mp_bid')
                queryset = queryset.order_by()
                queryset = queryset.iterator()
                for attendance in queryset:
                    meeting = attendance.meeting
                    writer.writerow([
                        meeting.legistature.number,
                        meeting.date.isoformat(),
                        "%d" % meeting.number,
                        "%d" % meeting.attendance_bid,
                        meeting.meeting_type.name,
                        attendance.member.name,
                        "%d" % attendance.member.mp_bid,
                        attendance.party.name,
                        attendance.status,
                        attendance.reason
                    ])
            sys.exit()

    # Show the help screen if no commands given
    usage()
    sys.exit()
