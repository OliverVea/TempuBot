import raiders
import schedule
import defs
import ranking_html_factory

from file_handling import JSONFile
from wrapper_warcraftlogs import getReportsGuild, getReportFightCode

import asyncio
import os
import discord
from multiprocessing import Process
import gc


from discord.ext import tasks
from discord.ext.commands import Cog, command, has_any_role

from selenium import webdriver
from selenium.webdriver.common.keys import Keys  
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

performance_file = JSONFile('performance.json', on_error={})

loop = asyncio.get_event_loop()

def get_fight_summary(fight, metrics, report_info):
    summary = {'fight': fight, 'parses': {}, 'report': {'title': report_info['title'], 'id': report_info['id'], 'start': report_info['start']}}
    for metric in metrics:
        url_dps = 'https://classic.warcraftlogs.com/reports/' + report_info['id'] + '#fight=' + str(fight['id']) + '&view=rankings&playermetric=' + metric

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

        print(defs.timestamp(), '*' + url_dps)
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url_dps)

        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "primary")))
        fight['deaths'] = element.text

        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "player-table")))
        row_elements = element.find_elements_by_tag_name('tr')[1:]

        for row_element in row_elements:
            row_stats = {}
            cell_elements = row_element.find_elements_by_tag_name('td')
            
            name = cell_elements[4].find_element_by_tag_name('a').get_attribute('innerHTML').lower()
            role = raiders.getRaiderAttribute(name, 'role')

            if ((metric == 'dps' and role in ['melee', 'ranged']) or (metric == 'hps' and role == 'healer')):
                row_stats['percentile'] = int(cell_elements[0].text)
                row_stats['rank'] = cell_elements[1].text
                row_stats['out_of'] = int(cell_elements[2].text.replace(',', ''))
                row_stats['best_rank'] = cell_elements[3].text
                row_stats['dps'] = float(cell_elements[5].text.replace(',', ''))
                row_stats['ilvl'] = int(cell_elements[6].text)
                row_stats['ipercentile'] = int(cell_elements[7].text)

                summary['parses'][name] = row_stats
                
    driver.close()
    driver.quit()
    return summary

def get_new_parses(metrics, new_parses):
    report_info = getReportsGuild('Hive Mind')[0]

    past_start = performance_file.get('start', '')
    bosses = performance_file.get('bosses', [])

    if (report_info['start'] != past_start): 
        bosses = []

    report = getReportFightCode(report_info['id'])

    fights = [fight for fight in report['fights'] if fight['boss'] is not 0 and fight['kill'] and fight['name'] not in bosses]

    for fight in fights:
        summary = get_fight_summary(fight, metrics, report_info)
        bosses.append(fight['name'])
        past = {'start': report_info['start'], 'bosses': bosses}
        performance_file.write(past)
        new_parses.append(summary)

def plot_fight(f, image_path):
    fight = f['fight']
    parses = f['parses']

    melee_parses = []
    ranged_parses = []
    healer_parses = []

    for name in parses:
        if (raiders.getRaiderAttribute(name, 'role') == 'ranged'): ranged_parses.append(name)
        elif (raiders.getRaiderAttribute(name, 'role') == 'melee'): melee_parses.append(name)
        elif (raiders.getRaiderAttribute(name, 'role') == 'healer'): healer_parses.append(name)

    group_names = ['Melee', 'Ranged', 'Healers']
    metric = ['DPS', 'DPS', 'HPS']

    tables = ""
    for i, current_parses in enumerate([melee_parses, ranged_parses, healer_parses]):
        rows = ""
        for j, name in enumerate(current_parses[:3]):
            parse = parses[name]
            percentile = parse['percentile']
            class_color = defs.colors[raiders.getRaiderAttribute(name, 'class')]
            rows += ranking_html_factory.get_row(
                number=str(j + 1), 
                name=name.capitalize(),
                name_color=class_color,
                parse=str(percentile), 
                parse_color=defs.getParseColor(percentile), 
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
            avg_parse_color=defs.getParseColor(avg_parse),
            avg_rank=str(avg_rank),
            avg_dps=str(avg_dps)
        )

    html = ranking_html_factory.get_html(fight['name'], tables)

    html_path = defs.dir_path + '/boss_summaries/' + fight['name'] + '.html'
    with open(html_path, 'w') as file:
        file.write(html)

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = webdriver.Chrome(options=chrome_options)
    driver.get('file:///' + html_path)

    body = driver.find_element_by_tag_name('body')
    size = body.size
    driver.set_window_size(size['width'], size['height'])

    driver.save_screenshot(image_path)

    driver.close()
    driver.quit()

class Performance(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.to_plot = []
        self.wclRaidTask.start()

    @command(name = 'forget', help='Removes a specific boss from the list of cleared bosses this week. Example: \'!forget Rag\'')
    @has_any_role('Officer', 'Admin')
    async def forget_boss(self, ctx, *args):
        print(defs.timestamp(), 'forget', ctx.author, args)
        try: await ctx.message.delete()
        except: pass
        if len(args) == 0:
            await ctx.send(content='Incorrect number of arguments. Use \'!help {}\' for help on how to use this feature.'.format(ctx.command.name))
        else:
            boss_name = ' '.join(args)
            bosses = [defs.bossEncounterIDs[key] for key in defs.bossEncounterIDs]

            match = ''
            for boss in bosses:
                if boss_name.lower() in boss.lower():
                    match = boss

            if match == '':
                await ctx.send(content='Input \'' + boss_name + '\' not understood. Use \'!help {}\' for help on how to use this feature.'.format(ctx.command.name))
            else:
                past = performance_file.read()
                if 'bosses' in past and match in past['bosses']:
                    past['bosses'].remove(match)
                performance_file.write(past)

    @tasks.loop(seconds=20)
    async def wclRaidTask(self):
        dates = schedule.schedule_file.get('dates')
        for entry in dates:
            if (schedule.isNow(entry['start'], entry['end'])):
                await asyncio.wait(fs={loop.run_in_executor(None, get_new_parses, ['dps', 'hps'], self.to_plot)})

        while (len(self.to_plot) > 0):     
            f = self.to_plot[0]
            fight = f['fight']
            parses = f['parses']
            report = f['report']
            
            image_path = defs.dir_path + '/boss_summaries/' + fight['name'] + '.png'

            await asyncio.wait(fs={loop.run_in_executor(None, plot_fight, f, image_path)})

            link = 'https://classic.warcraftlogs.com/reports/' + str(report['id']) + '#fight=' + str(fight['id'])

            pre_message = "__**" + fight['name'] + "**__" + '\n'
            pre_message += 'Participants: ' + str(len(parses)) + '\n'
            pre_message += 'Time: ' + str(round((fight['end_time'] - fight['start_time'])/1000, 1)) + 's' + '\n'
            pre_message += 'Deaths: ' + fight['deaths'] + '\n'
            post_message = "Log link: " + link 

            channel = self.bot.get_channel(entry['id'])
            await channel.send(content=pre_message, file=discord.File(image_path))
            await channel.send(content=post_message)
            os.remove(image_path)

            del self.to_plot[0]
            gc.collect()