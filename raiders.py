import os 
from defs import dir_path

from file_handling import JSONFile

raiders_file = JSONFile('raiders.json')

def getRaiderAttribute(name, attribute):
    name = name.lower()
    raiders = getRaiders()
    if name not in raiders: return None
    raider = raiders[name]
    return raider[attribute]

def getRaiders():
    raiders = raiders_file.read()
    return raiders

def getRaiderNames():
    raiders = getRaiders()
    raiderNames = [key for key in raiders]
    return raiderNames

def raiderExists(name : str):
    name = name.lower()
    raiders = getRaiders()
    return (name in raiders)

def getRaiderAmount():
    raiders = getRaiders()
    return len(raiders)

import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(dir_path + '/client_secret.json', scope)
client = gspread.authorize(creds)

def update_raiders():
    sheet = client.open("Hive Mind Officer docs").get_worksheet(3)
    sheet = sheet.get_all_values()

    header_row = [cell.strip().lower() for cell in sheet[2]]

    col_name = header_row.index('name')
    col_class = header_row.index('class')
    col_role = header_row.index('role')
    col_rank = header_row.index('rank')

    names = [row[col_name].strip().lower() for row in sheet[3:] if row[col_name] != '']
    classes = [row[col_class].strip().lower() for row in sheet[3:] if row[col_name] != '']
    roles = [row[col_role].strip().lower() for row in sheet[3:] if row[col_name] != '']
    ranks = [row[col_rank].strip().lower() for row in sheet[3:] if row[col_name] != '']

    raiders = {}

    for i, name in enumerate(names):
        raiders[name] = {'class': classes[i], 'role': roles[i], 'rank': ranks[i]}

    raiders_file.write(raiders)