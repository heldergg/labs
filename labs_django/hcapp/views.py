# -*- coding: utf-8 -*-

# Global imports
import datetime

from math import pi

from django.core.urlresolvers import reverse
from django.db.models import Sum, Count, Max, Min
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

# Local imports
from hcapp.models import Party, District, ElectionResult, ElectionStats
from hc.pm import hondt_method
from hc.chairs import Hemicycle
from hc.draw import HemicycleSGV
from hcapp.forms import ElectionForm

##
# Config

LAST_ELECTION = ElectionResult.objects.all().aggregate( Max('date') )['date__max'].isoformat()
MAX_GRAPHWIDTH = 150

##
# Utils


##
# Vote processing

def get_uni_votes(results):
    result_uni = {}
    for result in results:
        initials = result.party.initials
        if not result_uni.has_key(initials):
            result_uni[initials] = {
                    'party': result.party,
                    'initials': initials,
                    'votes':    0
                    }
        result_uni[initials]['votes'] += result.votes

    return { 1:[ result_uni[r] for r in result_uni ] }

def get_district_votes(results):
    results_district = {}
    for result in results:
        code = result.district.code
        if not results_district.has_key( code ):
            results_district[code] = []

        results_district[code].append({
            'party':    result.party,
            'initials': result.party.initials,
            'votes':    result.votes
            })
    return results_district


def get_election_results( date, uni_district ):
    # Get the election results
    results = ElectionResult.objects.filter(date__exact = date).select_related('party','district')

    # Parties running for the election:
    parties = [ Xi['party__initials']
                for Xi in results.values('party__initials').distinct() ]

    # Seats:
    total_seats = results.aggregate(Sum('seats'))['seats__sum']

    # Prepare the results
    if uni_district:
        results_dict = get_uni_votes(results)
    else:
        results_dict = get_district_votes(results)

    return results_dict, total_seats, parties


def get_district_seats( date, seats, total_seats, national_circle ):
    '''
    If the number of 'seats' for which we want to define the hemicycle
    is different from the number of seats the actual elections where made
    for, then we have to recalculate the seat attribution by electoral
    district.
    Since we only have demographic data from DGAI for the 2011 elections,
    it's that data that will be used on all elections.
    Data source: DGAI
    http://www.eleicoes.mj.pt/legislativas2011/index.html
    '''
    if national_circle == seats:
        return { 1:{ 'code': 1, 'result': seats } }

    if seats != total_seats:
        # Need to redistribute the PMs by each district:
        stats = ElectionStats.objects.filter( date__exact = date )
        # Get the registred voters for each district
        demographics = []
        for stat in stats:
            demographics.append( {
                'code': stat.district.code,
                'votes': stat.registered_voters } )

        # Recalculate seat attribution by electoral district
        districts_seats = hondt_method( seats, demographics )

    else:
        # Just retrieve the number of seats from the database
        districts_seats = []
        for district in District.objects.all():
            code = district.code
            seats = district.electionresult_set.filter(
                    date__exact=date).aggregate(seats=Sum('seats'))['seats']
            if seats:
                districts_seats.append({ 'code': code, 'result': seats })

    district_dict = {}
    for district in districts_seats:
        district_dict[ district['code'] ] = district

    return district_dict


def get_country_results( results, districts_seats ):
    # Get the results for each district
    for district in results:
        seats = districts_seats[ district ]['result']
        results[ district ] = hondt_method( seats, results[ district ] )

def get_totals( results ):
    # Compute the totals
    totals_tmp = {}
    for district in results:
        for party in results[district]:
            initials = party['initials']
            if not totals_tmp.has_key(initials):
                totals_tmp[initials] = {
                        'initials': initials,
                        'party': party['party'],
                        'result': 0,
                        'votes': 0
                        }
            totals_tmp[initials]['result'] += party['result']
            if district != 'national_circle':
                totals_tmp[initials]['votes'] += party['votes']
    results[ 'total' ] = [ totals_tmp[ r ] for r in totals_tmp ]

def get_national_circle_votes( national_circle_result, results):
    nc = {}
    for district in results:
        for party_votes in results[district]:
            if not party_votes['result'] and party_votes['votes']:
                if party_votes['initials'] not in nc:
                    nc[party_votes['initials']] = {
                            'party': party_votes['party'],
                            'votes': party_votes['votes'],
                            'result': 0,
                            'initials': party_votes['initials'],
                            }
                else:
                    nc[party_votes['initials']]['votes'] += party_votes['votes']

    for party in nc:
        national_circle_result.append(nc[party])


def process_election_results( date, seats, national_circle  ):
    '''
    year, month, day - date of the election to analyze
    seats - number of total seats to consider
    '''
    uni_district = seats == national_circle
    if national_circle > 0 and national_circle < seats:
        seats = seats - national_circle

    # Get the raw results:
    results, total_seats, parties = get_election_results( date, uni_district )

    # Get the seat distribution per electoral district
    districts_seats = get_district_seats( date, seats, total_seats, national_circle )

    # Get country results
    get_country_results( results, districts_seats )

    # Get the results for the national circle
    if national_circle > 0 and national_circle != seats:
        # Get the "non used votes" for each district for each party
        national_circle_result = []
        get_national_circle_votes( national_circle_result, results)
        # Calculate the seats dist
        results['national_circle'] = hondt_method( national_circle, national_circle_result)

    # Make the total sum
    get_totals( results )

    return results, districts_seats


##
# Views

def svg_hemicycle( request ):

    # Get the parameters
    try:
        date = datetime.datetime.strptime(request.GET.get('date', LAST_ELECTION), '%Y-%m-%d').date()
        seats = int(request.GET.get('seats', 0))
        national_circle = int(request.GET.get('national_circle',0))
        attachment = request.GET.get('attachment','no')
    except ValueError:
        raise Http404

    try:
        uni = request.GET.get('uni','M')
    except:
        pass
    uni_district = True if uni=='U' else False
    if uni == 'U':
        national_circle = seats

    # Argument testing

    election_results = ElectionResult.objects.filter(date__exact = date).aggregate(Count('date'))['date__count']
    if election_results == 0:
        raise Http404

    if seats == 0:
        seats = ElectionResult.objects.filter(date__exact = date).aggregate(Sum('seats'))['seats__sum']
    if seats < 10 or seats > 1000:
        raise Http404
    if national_circle < 0 or national_circle > seats:
        raise Http404

    attachment = 'attachment; ' if attachment == 'yes' else ''
    uni_str = ( 'circulo_unico'   if national_circle == seats else
                'varios_circulos' if national_circle == 0     else
                'varios_circulos_mais_circulo_nacional_%d' % national_circle )

    # Process the results
    results, districts_seats = process_election_results(date , seats, national_circle)

    # Format the Hemicycle data
    parties = results[ 'total' ]
    for party in parties:
        p = party['party']
        party['order'] = p.order
        party['color_1'] = p.color_1
        party['color_2'] = p.color_2

    # Create the hemicycle
    nrows = ( 16 if       seats > 600  else
               8 if 200 < seats <= 600 else
               6 if  80 < seats <= 200 else
               3 if  40 < seats <=  80 else 1 )

    hc = Hemicycle( chair_width = 60,
                    chair_height = 60,
                    nchairs = seats,
                    nrows = nrows,
                    hangle = pi )

    # Graphical representation of the hemicycle
    hc_svg = HemicycleSGV(hc, parties)
    hc_svg.chair_dist()

    response = HttpResponse(hc_svg.svg(), content_type='image/svg+xml')
    response['Content-Disposition'] = '%sfilename="%s-eleicoes-%d_deputados-%s.svg"' % ( attachment, date.isoformat() , seats, uni_str )

    return response

def results( request ):

    # Get the parameters
    try:
        seats = int(request.GET.get('seats', 0))
    except ValueError:
        seats = 0
    try:
        date = datetime.datetime.strptime(request.GET.get('date', LAST_ELECTION), '%Y-%m-%d').date()
    except ValueError:
        raise Http404
    try:
        national_circle = int(request.GET.get('national_circle',0))
    except ValueError:
        # Compatibility
        national_circle = 0
    try:
        uni = request.GET.get('uni','')=='U'
        if uni:
            national_circle = seats
    except ValueError:
        pass

    # Parameter testing
    election_results = ElectionResult.objects.filter(date__exact = date).aggregate(Count('date'))['date__count']
    if election_results == 0:
        raise Http404

    if seats == 0:
        seats = ElectionResult.objects.filter(date__exact = date).aggregate(Sum('seats'))['seats__sum']
    if seats < 10:
        seats = 10
    elif seats > 1000:
        seats = 1000

    if national_circle < 0:
        national_circle = 0
    if national_circle > seats:
        national_circle = seats

    # Process the results
    results, districts_seats = process_election_results(date , seats, national_circle)

    # Format the Hemicycle data
    votes = ElectionResult.objects.filter(date__exact = date).aggregate(Sum('votes'))['votes__sum']
    parties = results[ 'total' ]
    parties.sort( key = lambda party: -party['votes'] )
    max_seats = parties[0]['result']
    for party in parties:
        p = party['party']
        party['order'] = p.order
        party['color_1'] = p.color_1
        party['color_2'] = p.color_2
        party['percentage'] = float( party['votes'] ) / votes * 100
        party['percentage_seats'] = float( party['result'] ) / seats * 100
        party['graph'] = party['result'] * MAX_GRAPHWIDTH / max_seats

    # Next and previous elections
    next_date = ElectionResult.objects.filter(date__gt = date ).aggregate( Min('date') )['date__min']
    prev_date = ElectionResult.objects.filter(date__lt = date ).aggregate( Max('date') )['date__max']

    # Form

    form = ElectionForm({ 'date': date.isoformat(),
                          'national_circle': national_circle,
                          'seats': seats })

    # Context
    context = {}
    context['date'] = date
    context['next_date'] = next_date
    context['prev_date'] = prev_date
    context['seats'] = seats
    context['national_circle'] = national_circle
    context['real_seats'] = ElectionResult.objects.filter(date__exact = date).aggregate(Sum('seats'))['seats__sum']
    context['votes'] = votes
    context['results'] = results
    context['districts_seats'] = districts_seats
    context['form'] = form

    return render_to_response('hc_results.html', context,
        context_instance=RequestContext(request))


def election_results( request ):
    # Redirect to the latest election on file
    return HttpResponseRedirect(reverse('results'))
