from os.path import dirname, realpath
from datetime import datetime

import json

dir_path = dirname(realpath(__file__))

colors = {
    'Death Knight': '#C41F3B', 
    'Demon Hunter': '#A330C9', 
    'Druid': '#FF7D0A', 
    'Hunter': '#A9D271', 
    'Mage': '#40C7EB', 
    'Monk': '#00FF96', 
    'Paladin': '#F58CBA', 
    'Priest': '#FFFFFF',
    'Rogue': '#FFF569', 
    'Shaman': '#0070DE', 
    'Warlock': '#8787ED', 
    'Warrior': '#C79C6E',
    'Discord': '#36393f'
    }

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

def load_json_file(filename, on_error = {}):
    try:
        with open(filename) as f:
            content = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(timestamp(), 'tried to load file:', filename, 'raised error', e)
        content = on_error
    
    return content