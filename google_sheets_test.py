
import defs
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(defs.dir_path + '/client_secret.json', scope)
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

    with open(defs.dir_path + '/raiders.json', 'w', encoding=defs.encoding) as file:
        json.dump(raiders, file, ensure_ascii=False, indent=4)

"""
bosses = ['Lucifron', 'Magmadar', 'Gehennas', 'Garr', 'Baron Geddon', 'Shazzrah', 'Golemagg', 'Sulfuron Harbinger', 'Majordomo', 'Ragnaros', 'Onyxia']

sheet = sheet.get_all_values()
for row in range(0, len(sheet) - 1):
    date = sheet[row + 1][0]

    if ('/' in date): 
        print(date)
        loot = {}
        for col in range(0, len(sheet[row])):
            name = sheet[row][col]
            if (name in bosses):
                print(name)

                drops = []
                for j in range(0, 7):
                    item = sheet[row + j + 1][col]
                    player = sheet[row + j + 1][col + 1]
                    note = sheet[row + j + 1][col + 2]

                    if item != '':
                        drops.append({'item': item, 'player': player, 'note': note})
                
                loot[name] = drops
        content[date] = loot

json.dump(content, open(defs.dir_path + '/loot.json', 'w'), ensure_ascii=False, indent=4)
"""