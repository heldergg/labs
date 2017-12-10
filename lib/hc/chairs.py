# -*- coding: utf-8 -*-

'''
On this module the necessary calcs are made in order to obtain the chair
distribution in an hemicycle.
'''

##
# Imports
##

from math import asin, pi, floor, cos, sin

##
# Constantes
##

MAXCYCLE = 10000

##
# Exception
##


class ChairError(Exception):
    pass

##
# Hemicycle calculus
##


class Hemicycle(object):
    '''
    This class makes the necessary calculations to define an hemicycle filled
    with chairs.
    '''

    def __init__(self, chair_width, chair_height, nchairs=230,
                 nrows=8, hangle=pi):
        self.chair_width = float(chair_width) / 2
        self.chair_height = float(chair_height)
        self.hangle = hangle
        self.nchairs = nchairs
        self.nrows = nrows
        self.N = 230

        self.b = None

    def width(self):
        '''Hemicycle width'''
        return 2 * self.outer_radius

    def heigh(self):
        '''Hemicycle height'''
        if self.start_angle <= 0:
            return self.outer_radius * (1 - sin(self.start_angle))
        else:
            return self.outer_radius - self.inner_radius * sin(self.start_angle)

    def outer_radius(self):
        return self.inner_radius + self.nrows * self.chair_height

    def start_angle(self):
        '''Start angle of the hemicycle'''
        if self.hangle >= pi:
            return (pi - self.hangle) / 2.0
        else:
            return (self.hangle - pi) / 2.0

    def minimum_angle(self, row):
        '''
        This method returns the minimum angle between chairs.
        '''
        return 2 * asin(self.chair_width / (row + self.chair_width))

    def chairs_per_row(self, row):
        '''
        Number of chairs in a row
        '''
        return floor(self.hangle / self.minimum_angle(row))

    def angle(self, row):
        '''
        Angle between chairs enough to have a integer number of chairs
        '''
        return self.hangle / self.chairs_per_row(row)

    def solve_b(self):
        if self.b:
            return self.b

        def calc_chairs(b):
            '''
            For a given b, calculates the number of possible chairs on the
            hemicycle. Being b the distance from the centre to the first
            row of chairs.
            '''
            N = 0
            for row in range(self.nrows):
                b_tmp = b + self.chair_height * row
                N += self.chairs_per_row(b_tmp)
            return floor(N)

        ncycle = 0
        step = 0.5
        b = 10
        target = self.nchairs

        while True:
            ncycle += 1
            if ncycle >= MAXCYCLE:
                raise ChairError('Maximum number of cycles reached. Aborting.')
            if b <= 0:
                raise ChairError('Could not find a solution. Aborting.')

            N = calc_chairs(b)

            if N == target:
                break
            elif N > target:
                b -= step
                if ncycle == 1:
                    direccao = 1
                elif direccao == 0:
                    step = step / 2
            else:
                b += step
                if ncycle == 1:
                    direccao = 0
                elif direccao == 1:
                    step = step / 2
        self.b = b
        return b

    inner_radius = property(solve_b)

    def row_radius(self, row):
        return self.inner_radius + self.chair_height * row

    def row_chairs(self, row):
        '''Number of chairs in a row '''
        radius = self.row_radius(row)
        return int(self.chairs_per_row(radius))

    def row_angle(self, row):
        return self.hangle / (self.row_chairs(row) - 1)

    def rows(self):
        for r in range(self.nrows):
            row = {}
            row['number'] = r + 1
            row['radius'] = self.row_radius(r)
            row['nchairs'] = int(self.chairs_per_row(row['radius']))

            yield row

    def chair_location(self, row, column):
        '''Returns the angle of the chair (in order to point to the center of
        the hemicycle and its x,y coordinate. The origin of the coordinate
        system used is the hemicycle center'''

        chair_angle = self.start_angle() + self.hangle - (self.row_angle(row) * column)
        radius = self.row_radius(row)

        x = cos(chair_angle) * radius
        y = sin(chair_angle) * radius

        return chair_angle, x, y


if __name__ == '__main__':
    hc = Hemicycle(chair_width=60,
                   chair_height=60,
                   nchairs=230,
                   nrows=8,
                   hangle=pi)

    print 'Inner radius: ', hc.inner_radius
    print

    for row in hc.rows():
        print 'Row ', row['number']
        print '    radius ', row['radius']
        print '    chairs ', row['nchairs']
