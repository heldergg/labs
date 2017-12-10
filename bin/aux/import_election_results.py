#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# Config

election_data = '../../labs_django/hcapp/static/data/resultados_legislativas-1975-2011.csv'
election_stats = '../../labs_django/hcapp/static/data/inscritos_votos_brancos_nulos_legislativas-1975-2011.csv'

##
# Imports

import csv
import sys
import os.path
import datetime

sys.path.append(os.path.abspath('../../lib/'))
sys.path.append(os.path.abspath('../../labs_django/'))

os.environ['DJANGO_SETTINGS_MODULE'] = 'labs_django.settings'

import django
django.setup()

from django.db import transaction
from hcapp.models import Party, District, ElectionResult, ElectionStats

##
# Party info
party_info = {
    'AOC': {'name': 'Aliança Operária Camponesa', 'wikipedia': 'Aliança_Operária_Camponesa', 'tendency': 'Esquerda', 'order': 0, 'color_1': 'red', 'color_2': 'yellow'},
    'APU': {'name': 'Aliança Povo Unido (PCP/MDP-CDE/PEV só depois de 1983)', 'wikipedia': 'Aliança_Povo_Unido', 'tendency': 'Esquerda', 'order': 10, 'color_1': 'red', 'color_2': 'red'},
    'BE': {'name': 'Bloco de Esquerda', 'wikipedia': 'Bloco_de_Esquerda_(Portugal)', 'tendency': 'Esquerda', 'order': 20, 'color_1': 'black', 'color_2': 'purple'},
    'CDU': {'name': 'Coligação Democrática Unitária (PCP/PEV)', 'wikipedia': 'CDU_-_Coligação_Democrática_Unitária', 'tendency': 'Esquerda', 'order': 30, 'color_1': 'red', 'color_2': 'red'},
    'FEC': {'name': 'Frente Eleitoral dos Comunistas (marxistas-leninistas)', 'wikipedia': 'Frente_Eleitoral_dos_Comunistas_(marxistas-leninistas)', 'tendency': 'Esquerda', 'order': 40, 'color_1': 'red', 'color_2': 'tomato'},
    'FER': {'name': 'Frente da Esquerda Revolucionária', 'wikipedia': 'Frente_da_Esquerda_Revolucionária', 'tendency': 'Esquerda', 'order': 50, 'color_1': 'red', 'color_2': 'white'},
    'FRS': {'name': 'Frente Republicana e Socialista (PS/UEDS/ASDI)', 'wikipedia': 'Frente_Republicana_e_Socialista', 'tendency': 'Esquerda', 'order': 60, 'color_1': 'hotpink', 'color_2': 'white'},
    'FSP': {'name': 'Frente Socialista Popular', 'wikipedia': 'Frente_Socialista_Popular', 'tendency': 'Esquerda', 'order': 70, 'color_1': 'red', 'color_2': 'green'},
    'LCI': {'name': 'Liga Comunista Internacionalista', 'wikipedia': 'Liga_Comunista_Internacionalista_(Portugal)', 'tendency': 'Esquerda', 'order': 80, 'color_1': 'red', 'color_2': 'white'},
    'LST': {'name': 'Liga Socialista dos Trabalhadores ', 'wikipedia': 'Liga_Socialista_dos_Trabalhadores', 'tendency': 'Esquerda', 'order': 90, 'color_1': 'red', 'color_2': 'blue'},
    'MDP': {'name': 'Movimento Democrático Português', 'wikipedia': 'Movimento_Democrático_Português', 'tendency': 'Esquerda', 'order': 100, 'color_1': 'black', 'color_2': 'red'},
    'MDP/CDE': {'name': 'Movimento Democrático Português - Comissão Democrática Eleitoral', 'wikipedia': 'Movimento_Democrático_Português', 'tendency': 'Esquerda', 'order': 110, 'color_1': 'black', 'color_2': 'red'},
    'MES': {'name': 'Movimento de Esquerda Socialista', 'wikipedia': 'Movimento_de_Esquerda_Socialista', 'tendency': 'Esquerda', 'order': 120, 'color_1': 'hotpink', 'color_2': 'yellow'},
    'MRPP': {'name': 'Movimento Reorganizativo do Proletariado', 'wikipedia': 'Partido_Comunista_dos_Trabalhadores_Portugueses', 'tendency': 'Esquerda', 'order': 130, 'color_1': 'crimson', 'color_2': 'red'},
    'MUT': {'name': 'Movimento para a Unidade dos Trabalhadores', 'wikipedia': 'Movimento_para_a_Unidade_dos_Trabalhadores', 'tendency': 'Esquerda', 'order': 140, 'color_1': 'black', 'color_2': 'red'},
    'OCMLP': {'name': 'Organização Comunista Marxista-Leninista Portuguesa', 'wikipedia': 'Organização_Comunista_Marxista-Leninista_Portuguesa', 'tendency': 'Esquerda', 'order': 150, 'color_1': 'red', 'color_2': 'moccasin'},
    'PAN': {'name': 'Partido pelos Animais e pela Natureza', 'wikipedia': 'Partido_pelos_Animais_e_pela_Natureza', 'tendency': 'Esquerda', 'order': 160, 'color_1': 'LightSteelBlue', 'color_2': 'pink'},
    'PC(R)': {'name': 'Partido Comunista (Reconstruído)', 'wikipedia': 'Partido_Comunista_(Reconstruído)', 'tendency': 'Esquerda', 'order': 170, 'color_1': 'yellow', 'color_2': 'red'},
    'PCP': {'name': 'Partido Comunista Português', 'wikipedia': 'Partido_Comunista_Português', 'tendency': 'Esquerda', 'order': 180, 'color_1': 'red', 'color_2': 'red'},
    'PCP (M-L)': {'name': 'Partido Comunista de Portugal (marxista-leninista)', 'wikipedia': 'Partido_Comunista_de_Portugal_(marxista-leninista)', 'tendency': 'Esquerda', 'order': 190, 'color_1': 'white', 'color_2': 'red'},
    'PCTP/MRPP': {'name': 'Partido Comunista dos Trabalhadores Portugueses', 'wikipedia': 'Partido_Comunista_dos_Trabalhadores_Portugueses', 'tendency': 'Esquerda', 'order': 200, 'color_1': 'red', 'color_2': 'black'},
    'PH': {'name': 'Partido Humanista', 'wikipedia': 'Partido_Humanista_(Portugal)', 'tendency': 'Esquerda', 'order': 210, 'color_1': 'white', 'color_2': 'orange'},
    'POUS': {'name': 'Partido Operário de Unidade Socialista', 'wikipedia': 'Partido_Operário_de_Unidade_Socialista', 'tendency': 'Esquerda', 'order': 220, 'color_1': 'purple', 'color_2': 'red'},
    'POUS/PST': {'name': 'Coligação POUS/PST', 'wikipedia': '', 'tendency': 'Esquerda', 'order': 230, 'color_1': 'black', 'color_2': 'red'},
    'PRT': {'name': 'Partido Revolucionário dos Trabalhadores', 'wikipedia': 'Partido_Revolucionário_dos_Trabalhadores_(Portugal)', 'tendency': 'Esquerda', 'order': 240, 'color_1': 'whitesmoke', 'color_2': 'red'},
    'PSR': {'name': 'Partido Socialista Revolucionário', 'wikipedia': 'Partido_Socialista_Revolucionário', 'tendency': 'Esquerda', 'order': 250, 'color_1': 'whitesmoke', 'color_2': 'red'},
    'PT': {'name': 'Partido Trabalhista', 'wikipedia': 'Partido_Trabalhista_(Portugal)', 'tendency': 'Esquerda', 'order': 260, 'color_1': 'red', 'color_2': 'yellow'},
    'PUP': {'name': 'Partido de Unidade Popular', 'wikipedia': 'Partido_de_Unidade_Popular', 'tendency': 'Esquerda', 'order': 270, 'color_1': 'yellow', 'color_2': 'pink'},
    'UDP': {'name': 'União Democrática Popular', 'wikipedia': 'União_Democrática_Popular', 'tendency': 'Esquerda', 'order': 280, 'color_1': 'Cyan', 'color_2': 'red'},
    'UDP/PSR': {'name': 'Coligação UDP/PSR', 'wikipedia': '', 'tendency': 'Esquerda', 'order': 290, 'color_1': 'Cyan', 'color_2': 'white'},
    'CDM': {'name': 'Centro Democrático de Macau', 'wikipedia': 'Centro_Democrático_de_Macau', 'tendency': 'Centro-Esquerda', 'order': 300, 'color_1': 'SeaGreen', 'color_2': 'yellow'},
    'PDA': {'name': 'Partido Democrático do Atlântico', 'wikipedia': 'Partido_Democrático_do_Atlântico', 'tendency': 'Centro-Esquerda', 'order': 310, 'color_1': 'blue', 'color_2': 'yellow'},
    'PRD': {'name': 'Partido Renovador Democrático', 'wikipedia': 'Partido_Renovador_Democrático_(Portugal)', 'tendency': 'Centro-Esquerda', 'order': 320, 'color_1': 'green', 'color_2': 'red'},
    'PS': {'name': 'Partido Socialista ', 'wikipedia': 'Partido_Socialista_(Portugal)', 'tendency': 'Centro-Esquerda', 'order': 330, 'color_1': 'hotpink', 'color_2': 'hotpink'},
    'PSN': {'name': 'Partido da Solidariedade Nacional', 'wikipedia': 'Partido_da_Solidariedade_Nacional', 'tendency': 'Centro-Esquerda', 'order': 340, 'color_1': 'SeaGreen', 'color_2': 'blue'},
    'PTP': {'name': 'Partido Trabalhista Português', 'wikipedia': 'Partido_Trabalhista_Português', 'tendency': 'Centro-Esquerda', 'order': 350, 'color_1': 'CornflowerBlue', 'color_2': 'red'},
    'UDA/PDA': {'name': 'Coligação UDA/PDA', 'wikipedia': '', 'tendency': 'Centro-Esquerda', 'order': 360, 'color_1': 'blue', 'color_2': 'yellow'},
    'UEDS': {'name': 'União da Esquerda para a Democracia Socialista', 'wikipedia': 'União_da_Esquerda_para_a_Democracia_Socialista', 'tendency': 'Centro-Esquerda', 'order': 370, 'color_1': 'PeachPuff', 'color_2': 'pink'},
    'MEP': {'name': 'Movimento Esperança Portugal', 'wikipedia': 'Movimento_Esperança_Portugal', 'tendency': 'Centro', 'order': 380, 'color_1': 'green', 'color_2': 'black'},
    'MPT': {'name': 'Partido da Terra', 'wikipedia': 'Partido_da_Terra', 'tendency': 'Centro', 'order': 390, 'color_1': 'DarkGreen', 'color_2': 'DarkGreen'},
    'MPT-PH': {'name': 'FEH - Frente Ecologia e Humanismo', 'wikipedia': 'FEH_-_Frente_Ecologia_e_Humanismo', 'tendency': 'Centro', 'order': 400, 'color_1': 'SaddleBrown', 'color_2': 'SaddleBrown'},
    'AD': {'name': 'Aliança Democrática (PPD/CDS/PPM)', 'wikipedia': 'Aliança_Democrática_(Portugal)', 'tendency': 'Centro-Direita', 'order': 410, 'color_1': 'orange', 'color_2': 'white'},
    'ADIM': {'name': 'Associação para a Defesa dos Interesses de Macau', 'wikipedia': 'Associação_para_a_Defesa_dos_Interesses_de_Macau', 'tendency': 'Centro-Direita', 'order': 420, 'color_1': 'DarkGreen', 'color_2': 'yellow'},
    'MMS': {'name': 'Movimento Mérito e Sociedade (PLD a partir de 2011)', 'wikipedia': 'Movimento_Mérito_e_Sociedade', 'tendency': 'Centro-Direita', 'order': 430, 'color_1': 'DarkBlue', 'color_2': 'yellow'},
    'PG': {'name': 'Partido da Gente', 'wikipedia': 'Partido_da_Gente', 'tendency': 'Centro-Direita', 'order': 440, 'color_1': 'SkyBlue', 'color_2': 'blue'},
    'PPD': {'name': 'Partido Popular Democrático', 'wikipedia': 'Partido_Social_Democrata_(Portugal)', 'tendency': 'Centro-Direita', 'order': 450, 'color_1': 'orange', 'color_2': 'orange'},
    'PPD/PSD': {'name': 'Partido Social Democrata', 'wikipedia': 'Partido_Social_Democrata_(Portugal)', 'tendency': 'Centro-Direita', 'order': 460, 'color_1': 'orange', 'color_2': 'orange'},
    'PPM': {'name': 'Partido Popular Monárquico', 'wikipedia': 'Partido_Popular_Monárquico', 'tendency': 'Centro-Direita', 'order': 470, 'color_1': 'white', 'color_2': 'blue'},
    'PPM/MPT': {'name': 'Coligação PPM/MPT', 'wikipedia': '', 'tendency': 'Centro-Direita', 'order': 480, 'color_1': 'white', 'color_2': 'blue'},
    'PSD': {'name': 'Partido Social Democrata', 'wikipedia': 'Partido_Social_Democrata_(Portugal)', 'tendency': 'Centro-Direita', 'order': 490, 'color_1': 'orange', 'color_2': 'orange'},
    'CDS': {'name': 'Centro Democrático Social', 'wikipedia': 'Centro_Democrático_Social', 'tendency': 'Direita', 'order': 500, 'color_1': 'blue', 'color_2': 'blue'},
    'CDS-PP': {'name': 'Centro Democrático Social-Partido Popular', 'wikipedia': 'Centro_Democrático_Social', 'tendency': 'Direita', 'order': 510, 'color_1': 'blue', 'color_2': 'blue'},
    'CDS-PP/PPM': {'name': 'Coligação CDS-PP / PPM nos Açores', 'wikipedia': '', 'tendency': 'Direita', 'order': 511, 'color_1': 'blue', 'color_2': 'darkBlue'},
    'PDC': {'name': 'Partido da Democracia Cristã', 'wikipedia': 'Partido_da_Democracia_Cristã', 'tendency': 'Direita', 'order': 520, 'color_1': 'black', 'color_2': 'SkyBlue'},
    'PDC/MIRN-PDP/FN': {'name': 'Coligação PDC/MIRN-PDP/FN', 'wikipedia': '', 'tendency': 'Direita', 'order': 530, 'color_1': 'black', 'color_2': 'SkyBlue'},
    'PND': {'name': 'Nova Democracia', 'wikipedia': 'Nova_Democracia_(Portugal)', 'tendency': 'Direita', 'order': 540, 'color_1': 'Chocolate', 'color_2': 'Cornsilk'},
    'PPV': {'name': 'Portugal pro Vida', 'wikipedia': 'Portugal_pro_Vida', 'tendency': 'Direita', 'order': 550, 'color_1': 'DodgerBlue', 'color_2': 'gold'},
    'PNR': {'name': 'Partido Nacional Renovador', 'wikipedia': 'Partido_Nacional_Renovador', 'tendency': 'Extrema-Direita', 'order': 560, 'color_1': 'blue', 'color_2': 'red'},
    'JPP': {'name': 'Juntos Pelo Povo', 'wikipedia': 'Juntos_pelo_Povo', 'tendency': 'Centro', 'order': 385, 'color_1': '#009486', 'color_2': '#009486'},
    'L/TDA': {'name': 'LIVRE/Tempo de Avançar', 'wikipedia': 'Tempo_de_Avançar', 'tendency': 'Esquerda', 'order': 25, 'color_1': '#a4c660', 'color_2': '#a4c660'},
    'NC': {'name': 'Nós os Cidadãos!', 'wikipedia': 'Nós,_Cidadãos!', 'tendency': 'Centro', 'order': 391, 'color_1': '#fdad19', 'color_2': 'black'},
    'PDR': {'name': 'Partido Democrático Republicano', 'wikipedia': 'Partido_Democrático_Republicano_(Portugal)', 'tendency': 'Centro', 'order': 392, 'color_1': 'black', 'color_2': 'white'},
    'PaF': {'name': 'Portugal à Frente', 'wikipedia': 'Portugal_à_Frente', 'tendency': 'Direita', 'order': 459, 'color_1': 'orange', 'color_2': 'blue'},
    'PPV/CDC': {'name': 'Partido Cidadania e Democracia Cristã', 'wikipedia': 'Partido_Cidadania_e_Democracia_Cristã', 'tendency': 'Direita', 'order': 551, 'color_1': 'blue', 'color_2': 'blue'},
    'PTP-MAS': {'name': 'Coligação PTP / MAS', 'wikipedia': '', 'tendency': 'Esquerda', 'order': 295, 'color_1': 'pink', 'color_2': 'pink'},
    'PURP': {'name': 'Partido Unido dos Reformados e Pensionistas', 'wikipedia': 'Partido_Unido_dos_Reformados_e_Pensionistas', 'tendency': 'Centro', 'order': 401, 'color_1': 'yellow', 'color_2': 'yellow'},
}


##
# Process the file

# Read the file
data = csv.reader(open(election_data, 'r'))
stats = csv.reader(open(election_stats, 'r'))

districts = []
parties = []


# with transaction.atomic(): # Use on Django >= 1.6
with transaction.commit_on_success():
    for row in data:
        code = int(row[0])
        district_name = row[1].upper()
        election_type = row[2].lower()
        election_date = datetime.datetime.strptime(row[3], '%Y-%m-%d').date()
        party_initials = row[4].replace('.', '')
        votes = int(row[5])

        vote_percent = float(row[6])
        seats = int(row[7])

        if code not in districts:
            district = District(code=code, name=district_name)
            district.save()
            districts.append(code)
        else:
            district = District.objects.get(code=code)

        if party_initials not in parties:
            p = party_info[party_initials]
            party = Party(
                name=p['name'],
                initials=party_initials,
                wikipedia=p['wikipedia'],
                tendency=p['tendency'],
                order=p['order'],
                color_1=p['color_1'],
                color_2=p['color_2']
            )
            party.save()
            parties.append(party_initials)
        else:
            party = Party.objects.get(initials=party_initials)

        ElectionResult(
            district=district,
            party=party,

            election_type=election_type,
            date=election_date,
            votes=votes,

            vote_percent=vote_percent,
            seats=seats
        ).save()

        print code, district, election_type, election_date, party_initials, votes, vote_percent, seats

print "*** Importing stats"

districts = {}

for district in District.objects.all():
    districts[district.code] = district

# with transaction.atomic(): # Use on Django >= 1.6
with transaction.commit_on_success():
    for row in stats:
        code = int(row[0])
        date = datetime.datetime.strptime(row[2], '%Y-%m-%d').date()

        registered_voters = int(row[3])
        voters = int(row[4])
        blank_voters = int(row[5])
        invalid_votes = int(row[6])

        ElectionStats(
            district=districts[code],
            date=date,
            registered_voters=registered_voters,
            voters=voters,
            blank_voters=blank_voters,
            invalid_votes=invalid_votes
        ).save()

        print code, date, registered_voters, voters, blank_voters, invalid_votes
