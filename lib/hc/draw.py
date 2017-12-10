# -*- coding: utf-8 -*-

'''
This module produces SVG files with hemicycles representations.
'''

##
# Imports
##

from pysvg.structure import svg, g, defs, use, title
from pysvg.builders import TransformBuilder, ShapeBuilder
from pysvg.shape import path
from pysvg.style import style

from math import sin, cos, pi, floor
import os.path

from chairs import Hemicycle

##
#  Config
##

SVGBASE = '/home/helder/prg/hc/hc/share/hc'
TRANSX = 0
TRANSY = -50

##
# Exceptions
##


class SVGError(Exception):
    pass

##
#  Utils
##


def degrees(angle):
    '''Converts radians to degrees'''
    return angle * 180 / pi

##
#  SGV
##


class HemicycleSGV(object):
    '''
    This class creates svg representations of hemicycles.
    '''

    def __init__(self, hc, parties=None):
        '''
        hc - hemicycle object
        parties - list with the following structure:
            [ { 'initials': '<legend name>',
                'result': <number of chairs>,
                'image': '<svg filename>,
                'color': <foreground color>,
                'background': <background color>
              }, ...
            ]
        '''
        self.hc = hc
        self.parties = parties
        self.chairs = []

        # Check if the number of chairs in the results matches the
        # calculated hemicycle number of chairs.
        nchairs = sum([party['result'] for party in parties])
        if nchairs != hc.nchairs:
            raise SVGError(
                'Results chair number don\'t match the hemicycle size.')

    def chair_dist(self):
        '''Chair distribution on the hemicycle'''

        def smallest(parties, first_row):
            '''Returns the number of chairs for the smalest party in parties'''
            remaining = (sum([party['result'] for party in parties]) -
                         sum([sum(party['seats']) for party in parties]))

            smallest_party = parties[0]

            dist_seats = sum(smallest_party['seats'])
            remaining_seats = smallest_party['result'] - dist_seats

            percent = float(remaining_seats) / remaining
            nc = int(floor(percent * first_row))

            if sum(smallest_party['seats']) == smallest_party['result']:
                return 0

            return 1 if not nc else nc

        def fill_row(parties, seats):
            parties.sort(key=lambda party: party['result'])

            # Find how many seats we have for each party on this row
            for i in range(len(parties)):
                party = parties[i]

                party_row_seats = smallest(parties[i:], seats)
                party['seats'].append(party_row_seats)
                seats -= party_row_seats

        parties = self.parties
        for party in parties:
            party['seats'] = []

        hc = [row['nchairs'] for row in self.hc.rows()]
        for row in hc:
            fill_row(parties, row)
            parties.sort(key=lambda party: party['order'])

        # Create an hemicicle matrix, each row is empty, we'll fill the
        # rows afterwards
        chairs = []
        for i in range(self.hc.nrows):
            row = []
            for j in range(len(parties)):
                party = parties[j]
                for seat in range(party['seats'][i]):
                    row.append(j)

            chairs.append(row)

        self.chairs = chairs

    def svg_dimention(self):
        # The SVG coord system origin is on the lower left:
        height = self.hc.outer_radius()
        width = self.hc.outer_radius() * 2
        return width, height

    def chair_svg(self, row, column, id_attr):
        angle, x, y = self.hc.chair_location(row, column)

        width, height = self.svg_dimention()

        # This '30' is half the size of the svg chair, should be configured
        x = x + width / 2 - 30 * cos(pi / 2 - angle) + TRANSX
        y = height - y - 30 * sin(pi / 2 - angle) + TRANSY

        # Chair translation and rotation parametrization
        th = TransformBuilder()
        th.setRotation('%f' % (90 - degrees(angle)))
        th.setTranslation('%f,%f' % (x, y))

        u = use()
        u._attributes['xlink:href'] = '#%s' % id_attr
        u.set_transform(th.getTransform())

        return u

    def chair(self, id_attr, color_1, color_2):
        head = ShapeBuilder().createCircle(30, 25, 20, stroke='black', strokewidth=5.0, fill=color_1)
        head.set_class('head')
        body = path(pathData="M 19.264266,38.267870 C 12.892238,41.659428 9.0221978,48.396703 6.6126745,55.405840 L 51.476471,55.405840 C 49.270169,48.545436 45.682644,41.911786 39.811885,38.267870 C 33.901416,38.010889 26.459633,38.267870 19.264266,38.267870 z ")
        body.set_style('stroke-width:5.0;stroke:black;fill:%s;' % color_2)
        body.set_class('body')

        th = TransformBuilder()
        th.setScaling('0.8', '0.8')

        group = g()
        group.addElement(body)
        group.addElement(head)
        group.set_id(id_attr)
        group.set_transform(th.getTransform())

        return group

    def defs(self):
        d = defs()
        for party in self.parties:
            d.addElement(self.chair(party['initials'], party['color_1'], party['color_2']))
        return d

    def svg(self):
        if not self.chairs:
            raise SVGError('You need to calculate the chair distribution.')

        width, height = self.svg_dimention()

        # SVG doc
        s = svg(height="100%", width="100%")
        s.set_viewBox("0 0 %d %d" % (width, height))
        t = title()
        t.appendTextContent('Parlamento')
        s.addElement(t)

        # Create the party groups
        groups = {}
        for i in range(len(self.parties)):
            party = self.parties[i]
            groups[i] = g()
            # groups[i].set_fill(party['color'])
            groups[i].set_id('%s_group' % party['initials'])
            t = title()
            t.appendTextContent('Grupo Parlamentar do %s' % party['initials'])
            groups[i].addElement(t)

        # Add the chair shape definition
        s.addElement(self.defs())

        # Distribute the chairs
        for row in range(len(self.chairs)):
            for col in range(len(self.chairs[row])):
                angle, x, y = self.hc.chair_location(row, col)
                x = x + width / 2
                y = height - y

                groups[self.chairs[row][col]].addElement(self.chair_svg(
                    row, col, self.parties[self.chairs[row][col]]['initials']))

        # Insert the party groups into the svg
        for i in range(len(self.parties)):
            s.addElement(groups[i])

        return s.getXML()


if __name__ == '__main__':
    # Vote count
    parties = [{'initials': 'BE',  'order': 0, 'result': 8,   'image': 'cadeira-BE.svg'},
               {'initials': 'CDU', 'order': 1, 'result': 16,  'image': 'cadeira-CDU.svg'},
               {'initials': 'PS',  'order': 2, 'result': 74,  'image': 'cadeira-PS.svg'},
               {'initials': 'PSD', 'order': 3, 'result': 108, 'image': 'cadeira-PSD.svg'},
               {'initials': 'CDS', 'order': 4, 'result': 24,  'image': 'cadeira-CDS.svg'},
               ]

    parties = [
        {'name': 'Bloco de Esquerda', 'initials': 'BE',
         'order': 0, 'result': 7,  'color_1': 'purple', 'color_2': 'red'},
        {'name': 'Coligação Democratica Unitária', 'initials': 'CDU',
         'order': 1, 'result': 16, 'color_1': 'red', 'color_2': 'yellow'},
        {'name': 'Partido Socialista', 'initials': 'PS',
         'order': 2, 'result': 74, 'color_1': 'pink', 'color_2': 'pink'},
        {'name': 'Partido Social Democrata', 'initials': 'PSD',
         'order': 3, 'result': 109, 'color_1': 'orange', 'color_2': 'orange'},
        {'name': 'Centro Democrático Social', 'initials': 'CDS',
         'order': 4, 'result': 24, 'color_1': 'blue', 'color_2': 'white'},
    ]

    # Create the hemicycle
    hc = Hemicycle(chair_width=60,
                   chair_height=60,
                   nchairs=230,
                   nrows=8,
                   hangle=(4 / 3) * pi)

    # Graphical representation of the hemicycle
    hc_svg = HemicycleSGV(hc, parties)

    hc_svg.chair_dist()

    print hc_svg.svg()
