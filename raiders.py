import os 
import asyncio
from discord.ext import tasks
from discord.ext.commands import Cog, command

from file_handling import JSONFile
import defs
import logger

raiders_file = JSONFile('raiders.json')

def getRaiderAttribute(name, attribute):
    name = name.lower()
    raiders = getRaiders()
    if name not in raiders: return None
    raider = raiders[name]
    return raider.setdefault(attribute, None)

def getRaiders():
    raiders = raiders_file.get('raiders', {})
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

def all_with_attribute(attribute, value):
    raiders = getRaiders()
    return {raider:raiders[raider] for raider in raiders if raiders[raider][attribute] == value}

import gspread
from oauth2client.service_account import ServiceAccountCredentials

def update_raiders():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(defs.dir_path + '/client_secret.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open("Hive Mind Giga-Sheet").worksheet('Assessment Sheet')
    sheet_values = sheet.get_all_values()

    del_rows = []
    for i, row in sorted(enumerate(sheet_values), reverse=True):
        if all([cell == '' for cell in row]):
            del sheet_values[i]
            del_rows.append(i)
     
    sheet_values = [[cell.strip().lower() for cell in row] for row in sheet_values]

    header_row = -1 
    i = 0
    while (header_row is -1) and (i < len(sheet_values)):
        if set(['name', 'class', 'role']) <= set(sheet_values[i]): header_row = i
        i = i + 1

    if header_row is -1: return

    del_cols = []
    for i in sorted(range(0, len(sheet_values[0])), reverse=True):
        if sheet_values[header_row][i] is '':
            for j in range(0, len(sheet_values)):
                del sheet_values[j][i]
            del_cols.append(i)
    
    category_col = {}
    offset = 0
    for i, cell in enumerate(sheet_values[header_row]):
        while (i + offset in del_cols): offset += 1
        category_col[cell] = i + offset + 1
    raiders_file.set('category_col', category_col)

    raiders = {}
    offset = 0
    for i, row in enumerate(sheet_values[1:]):
        while (i + offset in del_rows or i + offset is 1): offset += 1 
        
        cells = {sheet_values[header_row][j]:row[j] for j in range(0, len(row))}

        raider =  {}
        raider['row'] = i + offset + 1 # 1-indexed
        raider['class'] = cells['class']
        raider['role'] = cells['role']
        raider['team'] = cells['team']
        raider['attendance'] = cells['attendance']

        raider['performance'] = {key:cells[key] for key in ['bwl', 'mc', 'ony']}

        raiders[cells['name']] = raider

    prev_raiders = list(raiders_file.get('raiders', on_error={}).keys())
    raiders_file.set('raiders', raiders)

    added = [name for name in raiders.keys() if not name in prev_raiders]
    removed = [name for name in prev_raiders if not name in raiders.keys()]

    message = 'update_raiders task finished with {} raiders.'.format(len(raiders))
    if (len(added) > 0): message += ' Added {} members: {}.'.format(len(added), ', '.join(added))
    if (len(removed) > 0): message += ' Removed {} members: {}.'.format(len(removed), ', '.join(removed))

    logger.log_event('raider_update', message)

def get_col(col_name):
    category_col = raiders_file.get('category_col', {})
    if col_name in category_col: return category_col[col_name]
    return None

class Raiders(Cog):
    @tasks.loop(minutes=15)
    async def update_raiders_task(self):
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, update_raiders)

    def __init__(self, bot):
        self.bot = bot
        self.update_raiders_task.start()

    def cog_unload(self):
        self.update_raiders_task.cancel()