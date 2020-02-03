import gspread
from oauth2client.service_account import ServiceAccountCredentials

import defs

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(defs.dir_path + '/client_secret.json', scope)
client = gspread.authorize(creds)

headers = ['Name', 'Class', 'Role']

def read_sheet():
    sheet = client.open("Hive Mind Officer docs").worksheet('Assessment Sheet')
    sheet = sheet.get_all_values()

    header_row = -1

    for i, row in sorted(enumerate(sheet), reverse=True):
        if all([cell == '' for cell in row]):
            del sheet[i]

    for i in sorted(range(0, len(sheet[0])), reverse=True):
        if all([row[i] == '' for row in sheet]):
            for j in range(0, len(sheet)):
                del sheet[j][i]

    for i, row in enumerate(sheet):
        if set(headers) <= set(row):
            header_row = i
            break

    if header_row is -1: return



    pass

read_sheet()