
import defs
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(defs.dir_path + '/client_secret.json', scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.
sheet = client.open("Hive Mind Officer docs").sheet1


content = {}

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
