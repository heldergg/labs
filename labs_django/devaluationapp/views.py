# -*- coding: utf-8 -*-

# Global imports
import datetime
import decimal

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max
from django.shortcuts import render_to_response
from django.template import RequestContext

# Local imports
from forms import DevalForm

##
# Data
##

# WARNING: This data is valid for 2015
#          After 2015 this should be updated

# Government coefficients published on:
# http://dre.tretas.org/dre/320012/
# Let Ci be the coefficient published for the ith year
# The following rates are calculated with:
# Ti = Ci/C(i+1)
GOV_VAR = {
    1903: 1.07424924959754, 1904: 1.0, 1905: 1.0, 1906: 1.0, 1907: 1.0,
    1908: 1.0, 1909: 1.0, 1910: 1.0426313561884, 1911: 1.0, 1912: 1.0,
    1913: 1.0, 1914: 1.12398264585474, 1915: 1.2217402856194, 1916:
    1.25266258403781, 1917: 1.40159537248682, 1918: 1.30482683060442,
    1919: 1.51340894697449, 1920: 1.53265799551736, 1921:
    1.35027642741397, 1922: 1.63404851835988, 1923: 1.18794523082616,
    1924: 1.16019964578973, 1925: 1.0, 1926: 1.0, 1927: 1.0, 1928:
    1.0, 1929: 1.0, 1930: 1.0, 1931: 1.0, 1932: 1.0, 1933: 1.0, 1934:
    1.0, 1935: 1.0, 1936: 1.0297319701575, 1937: 1.0, 1938: 1.0, 1939:
    1.18842768947852, 1940: 1.12585034013605, 1941: 1.15827338129496,
    1942: 1.17441158720579, 1943: 1.17796208530806, 1944: 1.0, 1945: 1.0,
    1946: 1.0, 1947: 1.0, 1948: 1.0, 1949: 1.0, 1950: 1.09001678935813,
    1951: 1.0, 1952: 1.0, 1953: 1.0, 1954: 1.0, 1955: 1.0, 1956: 1.0,
    1957: 1.0635989010989, 1958: 1.0, 1959: 1.0, 1960: 1.0, 1961: 1.0,
    1962: 1.0, 1963: 1.04627766599598, 1964: 1.03819755296926, 1965:
    1.04653341661462, 1966: 1.06929370512606, 1967: 1.0, 1968: 1.0, 1969:
    1.07987738910927, 1970: 1.05057776093957, 1971: 1.06970618034448,
    1972: 1.10008916629514, 1973: 1.30369078756176, 1974:
    1.17080639673358, 1975: 1.19374492282697, 1976: 1.30402542372881,
    1977: 1.27740189445196, 1978: 1.26758147512865, 1979:
    1.10941960038059, 1980: 1.22209302325581, 1981: 1.20617110799439,
    1982: 1.24868651488616, 1983: 1.28893905191874, 1984:
    1.19407008086253, 1985: 1.10746268656716, 1986: 1.09120521172638,
    1987: 1.11231884057971, 1988: 1.10843373493976, 1989:
    1.12162162162162, 1990: 1.13265306122449, 1991: 1.0828729281768,
    1992: 1.07738095238095, 1993: 1.05, 1994: 1.03896103896104, 1995:
    1.02666666666667, 1996: 1.01351351351351, 1997: 1.03496503496504,
    1998: 1.01418439716312, 1999: 1.02173913043478, 2000:
    1.06976744186047, 2001: 1.04032258064516, 2002: 1.03333333333333,
    2003: 1.01694915254237, 2004: 1.01724137931034, 2005:
    1.03571428571429, 2006: 1.01818181818182, 2007: 1.02803738317757,
    2008: 0.99074074074074, 2009: 1.00934579439252, 2010:
    1.03883495145631, 2011: 1.03, 2012: 1.0, 2013: 1.0, 2014: 1.0,
}

# Notes:
# - The government published devaluation coefficients are only available until
#   the year before last. We assume coefficients equal to 1.00 for the last
#   year

# Inflation values taken from:
# http://www.pordata.pt/Portugal/Taxa+de+Infla%C3%A7%C3%A3o+%28Taxa+de+Varia%C3%A7%C3%A3o+++%C3%8Dndice+de+Pre%C3%A7os+no+Consumidor%29-138
# These are the inflation values plus 1
INFLATION = {
    1960: 1.027, 1961: 1.019, 1962: 1.026, 1963: 1.018, 1964: 1.035, 1965: 1.034,
    1966: 1.053, 1967: 1.053, 1968: 1.06, 1969: 1.09, 1970: 1.064, 1971: 1.119,
    1972: 1.106, 1973: 1.131, 1974: 1.251, 1975: 1.152, 1976: 1.2, 1977: 1.274,
    1978: 1.2268, 1979: 1.2352, 1980: 1.1668, 1981: 1.2003, 1982: 1.2276,
    1983: 1.2509, 1984: 1.2888, 1985: 1.1963, 1986: 1.1175, 1987: 1.0933,
    1988: 1.0967, 1989: 1.1258, 1990: 1.1337, 1991: 1.1076, 1992: 1.0889,
    1993: 1.0647, 1994: 1.0517, 1995: 1.0412, 1996: 1.0306, 1997: 1.0216,
    1998: 1.0257, 1999: 1.0231, 2000: 1.0282, 2001: 1.0438, 2002: 1.0354,
    2003: 1.0319, 2004: 1.0234, 2005: 1.0224, 2006: 1.031, 2007: 1.0243,
    2008: 1.0256, 2009: 0.9902, 2010: 1.0138, 2011: 1.0373, 2012: 1.028,
    2013: 1.00025, 2014: 0.9996,
}

# Notes:
# - The current year inflation is made equal to 0.0

MAXYEAR = max(list(INFLATION)) + 1
MINYEAR = min(list(GOV_VAR))

##
# Calc
##


def coef_calc(COEF, year_0, year_1):
    coef = 1
    if year_0 > year_1:
        year_0, year_1 = year_1, year_0
    for year in range(year_0, year_1):
        coef *= COEF[year]
    return coef


def devaluation(COEF, year_0, year_1, value):
    '''
    COEF  - dict containing the devaluation coefficients
    value - value to devaluate/appreciate
    '''
    coef = coef_calc(COEF, year_0, year_1)
    if year_0 > year_1:
        return value / coef
    else:
        return value * coef

##
# Views
##


def devaluation_calc(request):
    context = {}

    value = request.GET.get('value', 1.0)
    try:
        value = float(value)
    except ValueError:
        value = 1.0

    year_0 = request.GET.get('year_0', MINYEAR)
    try:
        year_0 = int(year_0)
    except ValueError:
        year_0 = MINYEAR
    if not (MINYEAR <= year_0 <= MAXYEAR):
        year_0 = MINYEAR
    context['year_0'] = year_0

    year_1 = request.GET.get('year_1', MAXYEAR)
    try:
        year_1 = int(year_1)
    except ValueError:
        year_1 = MAXYEAR
    if not (MINYEAR <= year_1 <= MAXYEAR):
        year_1 = MINYEAR
    context['year_1'] = year_1

    to_value_gov = devaluation(GOV_VAR, year_0, year_1, value)
    context['to_value_gov'] = to_value_gov
    try:
        to_value_inf = devaluation(INFLATION, year_0, year_1, value)
    except KeyError:
        to_value_inf = None
    context['to_value_inf'] = to_value_inf

    context['form'] = DevalForm({
        'value': value,
        'year_0': year_0,
        'year_1': year_1,
    })

    return render_to_response('devaluation_calc.html', context,
                              context_instance=RequestContext(request))
