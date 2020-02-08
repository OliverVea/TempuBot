from os.path import dirname, realpath
from datetime import datetime

import json

dir_path = dirname(realpath(__file__))

bossEncounterIDs = {
    663: 'Lucifron', 
    664: 'Magmadar', 
    665: 'Gehennas', 
    666: 'Garr', 
    667: 'Baron Geddon', 
    668: 'Shazzrah', 
    669: 'Sulfuron Harbinger', 
    670: 'Golemagg the Incinerator',
    671: 'Majordomo Executus', 
    672: 'Ragnaros', 
    1084: 'Onyxia'}
    
colors = {
    'death knight': '#C41F3B', 
    'demon hunter': '#A330C9', 
    'druid': '#FF7D0A', 
    'hunter': '#A9D271', 
    'mage': '#40C7EB', 
    'monk': '#00FF96', 
    'paladin': '#F58CBA', 
    'priest': '#FFFFFF',
    'rogue': '#FFF569', 
    'shaman': '#0070DE', 
    'warlock': '#8787ED', 
    'warrior': '#C79C6E',
    'discord': '#36393f'
    }

classes = [
    'death knight', 
    'demon hunter', 
    'druid', 
    'hunter', 
    'mage', 
    'monk', 
    'paladin', 
    'priest',
    'rogue', 
    'shaman', 
    'warlock', 
    'warrior'
]

def getParseColor(parse):
    if (parse == 100): return '#e5cc80'
    elif (parse == 99): return '#e268a8'
    elif (parse >= 95): return '#ff8000'
    elif (parse >= 75): return '#a335ee'
    elif (parse >= 50): return '#0070dd'
    elif (parse >= 25): return '#1eff00'
    return '#9d9d9d'

def timestamp():
    return '[' + datetime.now().strftime('%H:%M:%S') + ']'

def get_options(args):
    options = [arg for arg in args if arg.startswith('-')]
    args = [arg for arg in args if not arg.startswith('-')]
    return options, args