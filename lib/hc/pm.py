# -*- coding: utf-8 -*-

'''
In this module we find the pm distribution on the parliament according to
various methodologies.
'''


def hondt_method(seats, parties):
    '''
    seat_number - number of seats on the electoral district being considerd
    parties - vote distribution, list in the form:
        [ { 'initials': '<party initials>',
            'votes': '<number of votes>' },
            ...
            ]

    This function will return the parties list with a new attribute 'result'
    that will contain the number of MPs.

    As described in "Lei 14/79 Artigo 16"

    Additionally a remaining_votes key will be added to each party identifying
    the votes that didn't contribute to gain a seat.
    '''

    for party in parties:
        party['result'] = 0

    while seats:
        # calculate each party quotient
        for party in parties:
            party['quotient'] = float(party['votes']) / (party['result'] + 1)
        parties.sort(key=lambda party: -party['quotient'])

        # Atribute the MP seat
        parties[0]['result'] += 1
        seats -= 1

    # Cleanup
    for party in parties:
        try:
            del party['quotient']
        except KeyError:
            # This will be triggered for hemicycles with less seats than
            # parties
            pass

    return parties


if __name__ == '__main__':
    parties = [
        {'initials': 'CDS', 'votes': 36602},
        {'initials': 'FEC', 'votes': 2003},
        {'initials': 'MDP', 'votes': 12849},
        {'initials': 'MES', 'votes': 3269},
        {'initials': 'PCP', 'votes': 10479},
        {'initials': 'PPD', 'votes': 141872},
        {'initials': 'PS',  'votes': 105098},
        {'initials': 'PUP', 'votes': 1694},
    ]

    import pprint
    pprint.pprint(hondt_method(14, parties))
