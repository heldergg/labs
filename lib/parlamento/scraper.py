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

ATTENDANCEURL = ('https://www.parlamento.pt/DeputadoGP/Paginas/DetalheReuniaoPlenaria.aspx?BID=')

SITEWSDL = 'https://www.parlamento.pt/DeputadoGP/_vti_bin/sites.asmx?wsdl'

FORMID = 'ctl00$ctl43$g_90441d47_53a9_460e_a62f_b50c50d57276$ctl00$'

##
# Errors
##

class EndOfLegislatureError(Exception):
    pass

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
    def __init__(self):
        # Open the connection
        self.connection = ParlamentoConn()
        # Get the legislature list and a soupified version of the first index
        # page
        html = self.connection.session.get(INDEXURL).text
        self.soup = BeautifulSoup(html, 'lxml')
        self.legislatures = self.get_legislatures()
        self.legislatures.reverse()
        self.current_legislature = self.legislatures.pop()
        self.page_number = 2

    def get_legislatures(self):
        return [lg['value']
                    for lg in self.soup.findAll('option')
                        if lg['value']]

    def page(self):
        table = self.soup.find('table', {'class': 'ARTabResultados'})
        for line in table.find_all(
                'tr', {'class': ['ARTabResultadosLinhaPar',
                                 'ARTabResultadosLinhaImpar']}):
            cells = line.find_all('td')
            yield {
                   'legislature': self.current_legislature,
                   'date': datetime.datetime.strptime(
                       cells[0].a.renderContents(), '%Y-%m-%d'),
                   'attendance_bid': int(cells[0].a['href'].split('=')[1]),
                   'number': int(cells[1].a.renderContents()),
                   'type': cells[2].renderContents(),
                   'schedule_url': cells[1].a['href']
                   }

    def read_next_page(self):
        form = self.soup.find('form', {'id': 'aspnetForm'})
        form_input = form.findAll('input')
        form_values = {}
        for el in form_input:
            if el['id'] != 'pesquisa':
                if el['name'] == (FORMID + 'btnPesquisar'):
                    continue
                try:
                    form_values[el['name']] = el['value']
                except KeyError:
                    form_values[el['name']] = ''

        form_values[FORMID + 'ddlLegislatura'] = self.current_legislature
        form_values['__EVENTARGUMENT'] = 'Page$%d' % self.page_number
        form_values['__EVENTTARGET'] = FORMID + 'gvResults'
        form_values['ctl00$ScriptManager'] = FORMID + 'pnlUpdate|' + FORMID + 'gvResults'

        # Get the digest necessary to post the query
        # https://msdn.microsoft.com/en-us/library/dd930042(v=office.12).aspx
        transport = Transport(session=self.connection.session)
        client = Client(SITEWSDL, transport=transport)
        digest = client.service.GetUpdatedFormDigest()
        form_values['__REQUESTDIGEST'] = digest
        html = self.connection.session.post(INDEXURL, data=form_values).text
        self.soup = BeautifulSoup(html, 'lxml')
        self.page_number += 1

        if 'Ocorreu um erro inesperado.' in html:
            raise EndOfLegislatureError('Reached the end of the legislature')

    def read_next_legislature(self):
        # The last page was an error page, we have to reload the index page
        # and then change to the next legislature
        html = self.connection.session.get(INDEXURL).text
        self.soup = BeautifulSoup(html, 'lxml')

        form = self.soup.find('form', {'id': 'aspnetForm'})
        form_input = form.findAll('input')
        form_values = {}
        for el in form_input:
            if el['id'] != 'pesquisa':
                if el['name'] == FORMID + 'btnPesquisar':
                    continue
                try:
                    form_values[el['name']] = el['value']
                except KeyError:
                    form_values[el['name']] = ''

        form_values['ctl00$ScriptManager'] = FORMID + 'pnlUpdate|' + FORMID + 'btnPesquisar'
        form_values[FORMID + 'ddlLegislatura'] = self.current_legislature
        form_values['__EVENTARGUMENT'] = ''
        form_values['__EVENTTARGET'] = ''
        form_values[FORMID + 'btnPesquisar'] = 'Pesquisar'

        # Get the digest necessary to post the query
        # https://msdn.microsoft.com/en-us/library/dd930042(v=office.12).aspx
        transport = Transport(session=self.connection.session)
        client = Client(SITEWSDL, transport=transport)
        digest = client.service.GetUpdatedFormDigest()
        form_values['__REQUESTDIGEST'] = digest

        html = self.connection.session.post(INDEXURL, data=form_values).text
        self.soup = BeautifulSoup(html, 'lxml')


    def get_next_page(self):
        try:
            self.read_next_page()
        except EndOfLegislatureError:
            self.current_legislature = self.legislatures.pop()
            self.read_next_legislature()
            self.page_number = 2

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
    table = soup.find('table', {'class': 'ARTabResultados'})
    for line in table.find_all(
            'tr', {'class': ['ARTabResultadosLinhaPar',
                             'ARTabResultadosLinhaImpar']}):
        cells = line.find_all('td')
        yield {
               'name': cells[0].a.renderContents(),
               'mp_bid': int(cells[0].a['href'].split('=')[1]),
               'party': cells[1].span.renderContents(),
               'status': cells[2].span.renderContents(),
               'reason': cells[3].span.renderContents(),
               }