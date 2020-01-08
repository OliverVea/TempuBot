import discord
import asyncio
import datetime
import time
import json
import matplotlib.pyplot as plt
import numpy as np
import os

from discord.ext.tasks import loop
from discord.ext.commands import Bot
from discord.ext.commands import has_permissions

import ranking_html_factory
from wrapper_warcraftlogs import getReportsGuild, getReportFightCode, getParses
import raiders
from defs import dir_path, colors, getParseColor
past_file_path = dir_path + r'/past_raid.json'

from selenium import webdriver
from selenium.webdriver.common.keys import Keys  
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_new_parses(metrics):
    past_title = ""
    past_bosses = []

    try:
        past = json.load(open(past_file_path))
        past_title = past['title']
        past_bosses = past['bosses']
    except FileNotFoundError:
        past = {}

    new_parses = []
    report_info = getReportsGuild('Hive Mind')[0]
    if (report_info['title'] != past_title): 
        past_bosses = []

    report = getReportFightCode(report_info['id'])

    fights = []
    for fight in report['fights']:
        if fight['boss'] is not 0 and fight['kill'] and fight['name'] not in past_bosses:
            fights.append(fight)
            past_bosses.append(fight['name'])

    for fight in fights:
        summary = {'fight': fight, 'parses': {}, 'report': {'title': report_info['title'], 'id': report_info['id']}}
        for metric in metrics:
            url_dps = 'https://classic.warcraftlogs.com/reports/' + report_info['id'] + '#fight=' + str(fight['id']) + '&view=rankings&playermetric=' + metric

            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("keep_alive=True")
            chrome_options.binary_location = r'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'

            print('*' + url_dps)
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url_dps)

            element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "player-table")))

            row_elements = element.find_elements_by_tag_name('tr')[1:]


            for row_element in row_elements:
                row_stats = {}
                cell_elements = row_element.find_elements_by_tag_name('td')
                
                name = cell_elements[4].find_element_by_tag_name('a').get_attribute('innerHTML')
                role = raiders.getRaiderAttribute(name, 'role')

                if ((metric == 'dps' and role in ['Melee', 'Ranged']) or (metric == 'hps' and role == 'Healer')):
                    row_stats['percentile'] = int(cell_elements[0].text)
                    row_stats['rank'] = cell_elements[1].text
                    row_stats['out_of'] = int(cell_elements[2].text.replace(',', ''))
                    row_stats['best_rank'] = cell_elements[3].text
                    row_stats['dps'] = float(cell_elements[5].text)
                    row_stats['ilvl'] = int(cell_elements[6].text)
                    row_stats['ipercentile'] = int(cell_elements[7].text)

                    summary['parses'][name] = row_stats    
        new_parses.append(summary)
        past = {'title': report_info['title'], 'bosses': past_bosses}
        json.dump(past, open(past_file_path, 'w'), ensure_ascii=False, indent=4)
    return new_parses

fights = get_new_parses(['dps', 'hps'])

for f in fights:
    fight = f['fight']
    parses = f['parses']
    report = f['report']

    melee_parses = []
    ranged_parses = []
    healer_parses = []

    for name in parses:
        if (raiders.getRaiderAttribute(name, 'role') == 'Ranged'): ranged_parses.append(name)
        elif (raiders.getRaiderAttribute(name, 'role') == 'Melee'): melee_parses.append(name)
        elif (raiders.getRaiderAttribute(name, 'role') == 'Healer'): healer_parses.append(name)

    group_names = ['Melee', 'Ranged', 'Healers']
    metric = ['DPS', 'DPS', 'HPS']

    tables = ""
    for i, current_parses in enumerate([melee_parses, ranged_parses, healer_parses]):
        rows = ""
        for j, name in enumerate(current_parses[:3]):
            parse = parses[name]
            percentile = parse['percentile']
            class_color = colors[raiders.getRaiderAttribute(name, 'class')]
            rows += ranking_html_factory.get_row(
                number=str(j + 1), 
                name=name,
                name_color=class_color,
                parse=str(percentile), 
                parse_color=getParseColor(percentile), 
                rank=parse['rank'],
                dps=str(parse['dps']), 
            )
        
        avg_parse = 0
        avg_rank = 0
        avg_dps = 0

        n = len(current_parses)

        for name in current_parses:
            avg_parse += parses[name]['percentile'] / n
            avg_rank += int(parses[name]['rank'].replace('~','')) / n
            avg_dps += parses[name]['dps'] / n
            
        avg_parse = round(avg_parse, 1)
        avg_rank = int(avg_rank)
        avg_dps = round(avg_dps, 1)

        tables += ranking_html_factory.get_table(
            group_name=group_names[i], 
            metric=metric[i],
            rows=rows, 
            avg_parse=str(avg_parse), 
            avg_parse_color=getParseColor(avg_parse),
            avg_rank=str(avg_rank),
            avg_dps=str(avg_dps)
        )

    html = ranking_html_factory.get_html(fight['name'], tables)
    link = 'https://classic.warcraftlogs.com/reports/' + str(report['id']) + '#fight=' + str(fight['id'])

    html_path = dir_path + '/boss_summaries/' + fight['name'] + '.html'
    image_path = dir_path + '/boss_summaries/' + fight['name'] + '.png'
    with open(html_path, 'w') as file:
        file.write(html)

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument("--window-size=360,600")
    chrome_options.binary_location = r'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(html_path)

    driver.save_screenshot(image_path)
    