# parlamento - Open some data present in parlamento.pt
# Copyright (C) 2017 Helder Guerreiro

# This file is part of parlamento.
#
# parlamento is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# parlamento is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with parlamento.  If not, see <http://www.gnu.org/licenses/>.

#
# Helder Guerreiro <helder@tretas.org>
#

'''
This is a scraper to get data from parlamento.pt. This is the site of the
Portuguese parliament where some data is available to the citizens.
Unfortunately the format in which the data is available (sharepoint generated
html) makes it very difficult to make other uses for this data, besides
simply reading it.
This project aims to free this data.

Data:

The data produced is:

    meeting = {'legislature': <str>,        # Legislature number, roman numeral
               'date': <date>,
               'attendance_bid': <int>,     # Internal ID pointing to the
                                            # attendance page
               'number': <int>,             # Meeting number
               'type': <str>,               # Meeting type
               'schedule_url': <link>}      # PDF schedule

For each meeting we can extract the meeting attendance in the form:

    attendance = {
               'name': <str>,               # MP name
               'mp_bid': <int>,             # Internal ID pointing to the MP
                                            # page
               'party': <str>,              # Party name or parliament group
               'attendance': <str>,         # Present/not present
               'reason': <str> }            # If not present, why?

Example usage:

    for meeting in ParlamentoIndex().meetings():
        print(meeting)
        for mp in attendance(meeting):
            print(mp)
'''

##
# Imports
##

from __future__ import print_function
from bs4 import BeautifulSoup
import requests
import urllib3
from zeep import Client
from zeep.transports import Transport
import datetime

# Disable warning: InsecureRequestWarning: Unverified HTTPS request is being
# made. Adding certificate verification is strongly advised.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

##
# Configuration
##

USERAGENT = ('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101'
             ' Firefox/55.0')

INDEXURL = ('https://www.parlamento.pt/DeputadoGP/Paginas'
            '/reunioesplenarias.aspx')

ATTENDANCEURL = (
    'https://www.parlamento.pt/DeputadoGP/Paginas/DetalheReuniaoPlenaria.aspx?BID=')

SITEWSDL = 'https://www.parlamento.pt/DeputadoGP/_vti_bin/sites.asmx?wsdl'

FORMID = 'ctl00$ctl43$g_90441d47_53a9_460e_a62f_b50c50d57276$ctl00$'

verbose = True

##
# Errors
##


class EndOfLegislatureError(Exception):
    pass

##
# Utils
##

def chunks(l, n):
    '''Yield successive n-sized chunks from l.
    https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
    '''
    for i in range(0, len(l), n):
        yield l[i:i + n]


##
# Scraper
##


class ParlamentoConn:
    '''
    Establishes the connection to parlmento.pt and keeps the session
    information.
    '''

    def __init__(self):
        session = requests.Session()
        session.headers.update({'User-Agent': USERAGENT, })
        session.verify = False
        self.session = session


class ParlamentoIndex:
    '''
    Read legilature session index

    A legislature is composed of a number of sessions. Here we'll get the
    session index, starting on the latest session of the current legislature
    and then going backward, reading each page of the legislature index and,
    when no more pages are available, jumping to the previous session and
    repeating the process.
    '''

    def __init__(self, legislature=None):
        # Open the connection
        self.connection = ParlamentoConn()
        # Get the legislature list and a soupified version of the first index
        # page
        html = self.connection.session.get(INDEXURL).text
        self.soup = BeautifulSoup(html, 'lxml')
        self.legislatures = self.get_legislatures()
        self.legislatures.reverse()
        self.current_legislature = self.legislatures.pop()
        while legislature:
            if legislature != self.current_legislature:
                self.current_legislature = self.legislatures.pop()
            else:
                # A specific legislature was chosen
                self.read_next_legislature()
                break
        self.next_page = 2

    def get_legislatures(self):
        return [lg['value']
                for lg in self.soup.findAll('option')
                if lg['value']]

    def page(self):
        table = self.soup.find(
            'div',
            {'id': 'ctl00_ctl52_g_62fda7ea_cd69_4efd_ac'
                   '24_968bfc19cf59_ctl00_pnlResults'}).find(
                       'div',
                       {'class': 'row margin_h0 margin-Top-15'})
        for date, number, mtype, _ in chunks(
                table.find_all('div', recursive=False)[:-1], 4):
            try:
                schedule_url = number.a['href']
            except KeyError:
                schedule_url = ''
            yield {
                'legislature': self.current_legislature,
                'date': datetime.datetime.strptime(
                    date.a.renderContents(), '%Y-%m-%d'),
                'attendance_bid': int(date.a['href'].split('=')[1]),
                'number': int(number.a.renderContents()),
                'type': mtype.find_all('div')[-1].renderContents(),
                'schedule_url': schedule_url
            }

    def get_form_values(self, switch_legislature=False):
        form = self.soup.find('form', {'id': 'aspnetForm'})
        form_input = form.findAll('input')
        form_values = {}
        for el in form_input:
            if el['id'] != 'pesquisa':
                if (el['name'] == (FORMID + 'btnPesquisar') and
                        not switch_legislature):
                    continue
                try:
                    form_values[el['name']] = el['value']
                except KeyError:
                    form_values[el['name']] = ''

        form_values[FORMID + 'ddlLegislatura'] = self.current_legislature
        if switch_legislature:
            form_values['ctl00$ScriptManager'] = FORMID + \
                'pnlUpdate|' + FORMID + 'btnPesquisar'
            form_values['__EVENTARGUMENT'] = ''
            form_values['__EVENTTARGET'] = ''
        else:
            form_values['__EVENTARGUMENT'] = 'Page$%d' % self.next_page
            form_values['__EVENTTARGET'] = FORMID + 'gvResults'
            form_values['ctl00$ScriptManager'] = (
                FORMID + 'pnlUpdate|' + FORMID + 'gvResults')

        # Get the digest necessary to post the query
        # https://msdn.microsoft.com/en-us/library/dd930042(v=office.12).aspx
        transport = Transport(session=self.connection.session)
        client = Client(SITEWSDL, transport=transport)
        digest = client.service.GetUpdatedFormDigest()
        form_values['__REQUESTDIGEST'] = digest

        return form_values

    def read_page(self):
        form_values = self.get_form_values(switch_legislature=False)
        html = self.connection.session.post(INDEXURL, data=form_values).text
        self.soup = BeautifulSoup(html, 'lxml')

        if 'Ocorreu um erro inesperado.' in html:
            raise EndOfLegislatureError('Reached the end of the legislature')

    def read_next_legislature(self):
        # The last page was an error page, we have to reload the index page
        # and then switch to the next legislature
        html = self.connection.session.get(INDEXURL).text
        self.soup = BeautifulSoup(html, 'lxml')

        # Read page 1 of the new legislature
        form_values = self.get_form_values(switch_legislature=True)
        html = self.connection.session.post(INDEXURL, data=form_values).text
        self.soup = BeautifulSoup(html, 'lxml')

    def get_next_page(self):
        try:
            self.read_page()
            if verbose:
                print('* Legislature %s, Reading page %d' % (
                    self.current_legislature, self.next_page))
            # Set the next page to be read
            self.next_page += 1
        except EndOfLegislatureError:
            self.current_legislature = self.legislatures.pop()
            self.read_next_legislature()
            self.next_page = 2
            if verbose:
                print('* Switching legislature.')
                print('  Legislature %s, Read page 1' %
                      self.current_legislature)

    def meetings(self):
        while True:
            # Return the current page meetings:
            for meeting in self.page():
                yield meeting
            # Get the next page
            try:
                self.get_next_page()
            except IndexError:
                break


def attendance_read(meeting):
    url = ATTENDANCEURL + str(meeting['attendance_bid'])
    request = requests.get(url, verify=False)
    html = request.text
    soup = BeautifulSoup(html, 'lxml')
    table = soup.find(
        'div',
        {'id': 'ctl00_ctl52_g_6319d967_bcb6_4ba9'
               '_b9fc_c9bb325b19f1_ctl00_pnlDetalhe'})
    for mp, party, status, reason, _ in chunks(
            table.find_all('div', recursive=False)[2:], 5):
        yield {
            'name': mp.a.renderContents(),
            'mp_bid': int(mp.a['href'].split('=')[1]),
            'party': party.span.renderContents(),
            'status': status.span.renderContents(),
            'reason': reason.span.renderContents(),
        }
