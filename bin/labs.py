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

    ''' % { 'script_name': sys.argv[0] }


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

        elif o == '--read_time_sheet':
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

            for meeting_data in ParlamentoIndex().meetings():
                if verbose:
                    print('Reading %s meeting' % meeting_data['date'])
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
                except IntegrityError:
                    meeting = Meeting.objects.get(
                            legistature=legislature,
                            number=meeting_data['number'])

                for mp in attendance_read(meeting_data):
                    # Process MP attendace
                    if verbose:
                        print('   Reading MP %s attendance' % mp['name'])
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

            sys.exit()

    # Show the help screen if no commands given
    usage()
    sys.exit()
