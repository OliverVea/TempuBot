import os 
import asyncio
from discord.ext import tasks
from discord.ext.commands import Cog, command

from file_handling import JSONFile
import defs

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

def all_with_attribute(attribute, value):
    raiders = getRaiders()
    return {raider:raiders[raider] for raider in raiders if raiders[raider][attribute] == value}

import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(defs.dir_path + '/client_secret.json', scope)
client = gspread.authorize(creds)

def update_raiders():
    print(defs.timestamp(), 'update_raiders_task started')
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
    print(defs.timestamp(), 'update_raiders_task finished')


class Raiders(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_raiders_task.start()

    def cog_unload(self):
        self.update_raiders_task.cancel()
    
    @tasks.loop(hours=1)
    async def update_raiders_task(self):
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, update_raiders)
