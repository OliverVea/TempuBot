import json
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))

file_path = dir_path + '/raiders.json'

def newRaider():
    raider = {}
    raider['class'] = ''
    raider['role'] = ''
    raider['signoffs'] = []

def getRaiderAttribute(name, attribute):
    name = name.lower()
    raiders = getRaiders()
    if name not in raiders: return None
    raider = raiders[name]
    return raider[attribute]

def setRaiderAttribute(name, attribute, value):
    name = name.lower()
    raiders = getRaiders()
    if name not in raiders: return None
    raiders[name][attribute] = value
    json.dump(raiders, open(file_path, 'w'), ensure_ascii=False, indent=4)

def addRaider(name : str):
    name = name.lower()
    raiders = json.load(open(file_path))
    if name not in raiders: 
        raiders[name]  = {}
    json.dump(raiders, open(file_path, 'w'), ensure_ascii=False, indent=4)

def removeRaider(name : str):
    name = name.lower()
    raiders = json.load(open(file_path))
    if name in raiders: 
        del raiders[name]
    json.dump(raiders, open(file_path, 'w'), ensure_ascii=False, indent=4)

def getRaiders():
    raiders = json.load(open(file_path))
    return raiders

def getRaiderNames():
    raiders = getRaiders()
    raiderNames = [key for key in raiders]
    return raiderNames

def raiderExists(name : str):
    name = name.lower()
    raiders = json.load(open(file_path))
    return (name in raiders)

def getRaiderAmount():
    raiders = json.load(open(file_path))
    return len(raiders)

def resetFile():
    emptyObj = {}
    json.dump(emptyObj, open(file_path, 'w'))


setRaiderAttribute('merven', 'role', 'tank')