import os

from defs import dir_path
past_file_path = dir_path + r'/past_raid.json'
from wrapper_warcraftlogs import getReportsGuild, getReportFightCode

from selenium import webdriver
from selenium.webdriver.common.keys import Keys  
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import json

past_title = ""
past_bosses = []
def get_new_parses(metric):
    past = json.load(open(past_file_path))
    past_title = past['title']
    past_bosses = past['bosses']

    new_parses = []
    report_info = getReportsGuild('Hive Mind')[0]
    if (report_info['title'] is not past_title): past_bosses = []

    report = getReportFightCode(report_info['id'])

    fights = []
    for fight in report['fights']:
        boss = fight['boss']
        if boss is not 0 and boss not in past_bosses:
            fights.append(fight['id'])
            past_bosses.append(boss)

    for fight in fights:
        url_dps = 'https://classic.warcraftlogs.com/reports/' + report_info['id'] + '#fight=' + str(fight) + '&view=rankings&playermetric=' + metric

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.binary_location = r'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'

        print('*' + url_dps)
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url_dps)

        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "player-table")))
        driver.get_screenshot_as_file(r'D:\\WindowsFolders\\Code\\Python\\TempuBot\\file.png')

        row_elements = element.find_elements_by_tag_name('tr')[1:]

        stats = {}

        for row_element in row_elements:
            row_stats = {}
            cell_elements = row_element.find_elements_by_tag_name('td')
            
            name = cell_elements[4].find_element_by_tag_name('a').get_attribute('innerHTML')

            row_stats['percentile'] = int(cell_elements[0].text)
            row_stats['rank'] = cell_elements[1].text
            row_stats['out_of'] = int(cell_elements[2].text.replace(',', ''))
            row_stats['best_rank'] = cell_elements[3].text
            row_stats['dps'] = float(cell_elements[5].text)
            row_stats['ilvl'] = int(cell_elements[6].text)
            row_stats['ipercentile'] = int(cell_elements[7].text)

            stats[name] = row_stats    
        new_parses.append(stats)
    json.dump({'title': report_info['title'], 'bosses': past_bosses}, open(past_file_path, 'w'), ensure_ascii=False, indent=4)
    return new_parses

parses = get_new_parses('hps')
for parse in parses: 
    for key in parse: 
        print(key, parse[key])