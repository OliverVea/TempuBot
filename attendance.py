from time import time as time_now
import json
import os
import numpy as np
from contextlib import suppress
from datetime import datetime, date, time
import matplotlib.pyplot as plt
plt.style.use('discord')

import discord
from discord.ext import tasks
from discord.ext.commands import Cog, command, has_permissions, has_any_role

import defs
from wrapper_warcraftlogs import getReportsGuild, getReportFightCode
import raiders
import schedule
from file_handling import JSONFile
import logger

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread.models import Cell

earliest_next_update = 2 * 60
last_update = 0

attendance_file = JSONFile('attendance.json')

def get_query_start(days, months):
    query_start = 0
    if days != None and months != None:
        raise ValueError('Both days and months set.')
    elif days != None:
        if not isinstance(days, (int, float)): raise TypeError('days is not a number.')
        else: query_start = int(time_now() * 1000 - float(days) * 24 * 60 * 60 * 1000)
    elif months != None:
        if not isinstance(months, (int, float)): raise TypeError('months is not a number.')
        else: query_start = int(time_now() * 1000 - float(months) * 31 * 24 * 60 * 60 * 1000)
    return query_start

def get_raids(guild = 'Hive Mind', days = None, months = None):
    return getReportsGuild(guild, queryStart=get_query_start(days, months))

def get_attendance(update_attendance = True, days = None, months = None):
    global last_update, earliest_next_update
    reports_file = attendance_file.read()

    if update_attendance and last_update + earliest_next_update < time_now():
        last_update = time_now()
        reports = get_raids(days=days, months=months)

        for report_info in reports:
            report_info['exclude'] = report_info['title'].startswith('_')

            if '[MC]' in report_info['title']: report_info.setdefault('raids', []).append('MC')
            if '[BWL]' in report_info['title']: report_info.setdefault('raids', []).append('BWL')
            if '[ONY]' in report_info['title']: report_info.setdefault('raids', []).append('ONY')

            if '[R]' in report_info['title']: report_info['team'] = 'team red'
            elif '[B]' in report_info['title']: report_info['team'] = 'team blue'
            
            if not 'raids' in report_info or not 'team' in report_info: report_info['exclude'] = True
        
        reports = [report_info for report_info in reports if not report_info['exclude']]

        for raid in list(reports_file.keys()): 
            if not raid in [report_info['id'] for report_info in reports]: 
                del reports_file[raid]

        for report_info in reports:
            if report_info['id'] not in reports_file:
                print(defs.timestamp(), 'Adding raid (' + report_info['id'] + ') to the attendance file.') 
                report = getReportFightCode(report_info['id'])

                participants = [participant['name'].strip().lower() for participant in report['exportedCharacters']]

                raid_entry = {'start': report_info['start'], 'title': report['title'], 'participants': participants, 'team': report_info['team'], 'raids': report_info['raids']}

                reports_file[report_info['id']] = raid_entry
            attendance_file.write(reports_file)

    if days != None or months != None: last_update = 0

    start = get_query_start(days, months)
    filtered_attendance = [reports_file[raid_id] for raid_id in reports_file if reports_file[raid_id]['start'] > start]

    return filtered_attendance

def get_participants(update_attendance=True, days = None, months = None):
    attendance = get_attendance(update_attendance, days, months)
    participants = {}

    # Count attendance
    for report in attendance:
        for participant in report['participants']:
            team = raiders.getRaiderAttribute(participant, 'team')
            if team == report['team']:
                participants.setdefault(participant, {})
                for raidname in report['raids']:
                    participants[participant].setdefault(raidname, {'raids':[]})
                    participants[participant][raidname]['raids'].append(report['start'])
    
    for name in participants:
        for raid in participants[name]:
            participants[name][raid]['first_raid'] = min(participants[name][raid]['raids'])   

    # Count absence
    for name in participants:
        for raid_name in participants[name]:
            missed_raids = []
            signed_raids = []
            reports = [report for report in attendance if raid_name in report['raids']]
            for report in reports:
                start = report['start']
                if not start in participants[name][raid_name]['raids']:
                    if start > participants[name][raid_name]['first_raid']:
                        if (schedule.has_signed_off(name, start)): signed_raids.append(start)
                        else: missed_raids.append(start)
            participants[name][raid_name]['missed_raids'] = missed_raids
            participants[name][raid_name]['signed_raids'] = signed_raids

    result = {}

    for name in participants:
        total_attended = 0
        total_missed = 0
        total_signed = 0

        for raid in participants[name]:
            raid_info = participants[name][raid]

            total_attended += len(raid_info['raids'])
            total_missed += len(raid_info['missed_raids'])
            total_signed += len(raid_info['signed_raids'])

            try: raid_info['attendance'] = len(raid_info['raids']) / (len(raid_info['raids']) + len(raid_info['missed_raids']) + len(raid_info['signed_raids']))
            except ZeroDivisionError: raid_info['attendance'] = -1

            try: raid_info['sign_rate'] = len(raid_info['signed_raids']) / (len(raid_info['signed_raids']))
            except ZeroDivisionError: raid_info['sign_rate'] = 1
        
        try: att = total_attended / (total_attended + total_missed + total_signed)
        except ZeroDivisionError: att = -1

        try: sr = total_signed / (total_missed + total_signed)
        except ZeroDivisionError: sr = 1

        result[name] = {'attendance': att, 'sign_rate': sr, 'raids': participants[name]}

    return result

def get_participant(name, update_attendance=True, days = None, months = None):
    name = name.strip().lower()
    participants = get_participants(update_attendance, days, months)
    if name in participants: return participants[name]
    return {'attendance': 0, 'sign_rate': 0, 'raids': {}}

def make_attendance_plot(participants, figurename):
    attendances = []

    for p in participants:
        attended_raids = len(participants[p]['raids'])
        missed_raids = len(participants[p]['missed_raids'])
        attendance = attended_raids / (attended_raids + missed_raids)

        attendances.append([p, attendance])

    attendances.sort(key= lambda x: x[1], reverse=True)
    names = [entry[0] for entry in attendances]
    attendances = [entry[1] * 100 for entry in attendances]

    cols = [defs.colors[raiders.getRaiderAttribute(name, 'class')] for name in names]
    
    y_pos = np.arange(len(names))

    names = ['{} ({}%)'.format(name, round(attendances[i],1)) for i, name in enumerate(names)]

    _, ax = plt.subplots(figsize=(20,15))

    ax.barh(y_pos, attendances, color=cols, edgecolor='white', linestyle='-', linewidth=0)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel('Attendance [%]', color='white')

    plt.savefig(defs.dir_path + '/' + figurename)

def get_message_brief(categories):
    message = 'Attendance:\n'
    prev_type = ''
    for category in categories:
        if category['type'] is 'class':
            if prev_type is 'player':
                message += '\n'
            message += '__**{}:**__\n'.format(category['title'])

        for name, player_attendance in category['attendance']:
            if raiders.getRaiderAttribute(name, 'team') == 'team red': message += ':red_circle:'
            if raiders.getRaiderAttribute(name, 'team') == 'team blue': message += ':blue_circle:'

            if category['type'] is 'player':
                message += '__**{}**__ - '.format(name.capitalize())
            else:
                message += '**{}** - '.format(name.capitalize())

            raids = player_attendance['raids']

            attended_raids = sum([len(raids[raid]['raids']) for raid in raids.keys()])

            if (attended_raids == 0):
                message += 'no raids registered.\n'
            else:
                attendance = round(player_attendance['attendance'] * 100)

                missed_raids = sum([len(raids[raid]['missed_raids']) for raid in raids.keys()])
                signed_raids = sum([len(raids[raid]['signed_raids']) for raid in raids.keys()])

                message += 'attendance: **{}%**, attended raids: **{}**, signed off: **{}**, didn\'t sign off: **{}**\n'.format(attendance, attended_raids, signed_raids, missed_raids)

        if category['type'] is 'class':
            message += '\n'

        prev_type = category['type']        
    return message

def get_message_normal(categories):
    message = ''
    for _ in categories:
        pass
    return message

def get_message_verbose(categories):
    message = ''
    for _ in categories:
        pass
    return message

class Attendance(Cog):
    @command(name='attendance', help='Reports the attendance for the raider(s) or class(es). Example:\'!attendance Matitka warriors Mage swiftshot\'')
    @has_any_role('Officer', 'Admin')
    async def cmd_attendance(self, ctx, *args):
        logger.log_command(ctx, args)
        await ctx.message.delete()
        args = list(args)
        options, args = defs.get_options(args)

        days = None
        months = None

        digits = [i for i, arg in enumerate(args) if arg.isdigit()]

        if len(digits) > 1:
            await ctx.send('Arguments \'{}\' not understood. Please use \'!help {}\' for help on how to use this command.'.format(args, ctx.command.name), delete_after=self.error_messages_lifetime)
            return
        
        if (len(args) - 1) in digits:
            months = int(args[-1]) 
            args = args[:-1]
            
        if (len(args) - 2) in digits:
            last_arg = args[-1].lower()
            if last_arg in ['day', 'days']:
                days = int(args[-2]) 
                args = args[:-2]

            elif last_arg in ['month', 'months']:
                months = int(args[-2]) 
                args = args[:-2]

            else:
                await ctx.send('Argument \'{}\' not understood. Please use \'!help {}\' for help on how to use this command.'.format(args[-1], ctx.command.name), delete_after=self.error_messages_lifetime)
                return
        
        team = ''
        if ('-r' in options): team = 'team red'
        if ('-b' in options): team = 'team blue'

        categories = []
        for arg in args:
            if (arg.lower()[-1] is 's') and (arg.lower()[:-1] in defs.classes): 
                arg = arg.lower()[:-1]
            if arg.lower() in defs.classes:
                class_raiders = raiders.all_with_attribute('class', arg.lower())
                class_names = [raider for raider in class_raiders if raiders.getRaiderAttribute(raider, 'team') == team or team == '']
                category = {'type': 'class', 'title': arg.capitalize() + 's', 'attendance': class_names}
            else:
                category = {'type': 'player', 'attendance': [arg]}
            categories.append(category)
        
        for category in categories:
            category['attendance'] = [(name, get_participant(name.capitalize(), days=days, months=months)) for name in category['attendance']]
            category['attendance'].sort(key=lambda x: len(x[1]['raids']), reverse=True)
            category['attendance'].sort(key=lambda x: x[1]['attendance'], reverse=True)

        message = get_message_brief(categories)
        
        await ctx.send(message)

    @command(name='attendanceplot', help='Plots the attendance of all raiders. Optionally include a timeframe. Example: \'!attendanceplot 40 days\'')
    async def cmd_attendance_plot(self, ctx, *args):
        logger.log_command(ctx, args)
        await ctx.message.delete()
        _ = defs.get_options(args)

        days = None
        months = None

        if (len(args) > 2):
            await ctx.send('Too many arguments. Please use \'!help {}\' for help on how to use this command.'.format(ctx.command.name), delete_after=self.error_messages_lifetime)
            return

        if (len(args) > 0):
            if not args[0].isdigit():
                await ctx.send('Argument \'{}\' not understood. Please use \'!help {}\' for help on how to use this command.'.format(args[0], ctx.command.name), delete_after=self.error_messages_lifetime)
                return

            if len(args) == 1 or args[1] in ['month', 'months']: 
                months=int(args[0])

            elif args[1] in ['day', 'days']: 
                days=int(args[0])

            else:
                await ctx.send('Argument \'{}\' not understood. Please use \'!help {}\' for help on how to use this command.'.format(args[1], ctx.command.name), delete_after=self.error_messages_lifetime)
                return
        
        participants = get_participants(days=days, months=months)
        make_attendance_plot(participants, 'attendance_plot.png')
        await ctx.send(content="Attendance plot: ", file=discord.File(defs.dir_path + '/attendance_plot.png'))
        os.remove(defs.dir_path + '/attendance_plot.png')

    @command(name='missing', help='Reports which raiders were missing for a given date. Example: \'!missing 12.01\'')
    @has_any_role('Officer', 'Admin')
    async def noshows(self, ctx, *args):
        logger.log_command(ctx, args)
        with suppress(): await ctx.message.delete()

        participants = get_participants()
        
        if (len(args) is 1): query_date = schedule.get_date_from_string(args[0])
        else: query_date = datetime.combine(date.today(), time())
            
        epoch = datetime(1970, 1, 1)
        timestamp = int((query_date - epoch).total_seconds() * 1000)

        noshows = []

        for participant in participants:
            missed_raids = participants[participant]['missed_raids']
            missed_dates = [date.fromtimestamp(raid / 1000) for raid in missed_raids]
            if query_date.date() in missed_dates:
                noshows.append(participant)
        
        if len(noshows) is 0:
            await ctx.send('All raiders attended on the {}.'.format(query_date.strftime('%d/%m')))
            return

        for signoff in schedule.schedule_file.get('signoffs'):
            if signoff['start'] <= timestamp <= signoff['end'] and signoff['name'].lower().capitalize() in noshows:
                noshows.remove(signoff['name'].lower().capitalize())

        if len(noshows) is 0:
            await ctx.send('All missing raiders signed off on the {}.'.format(query_date.strftime('%d/%m')))
            return

        names = ('**{}** ({}%)'.format(name, round(get_participant(name)['attendance'] * 100)) for name in noshows)

        message = "Missing raiders for the {}: {}".format(query_date.strftime('%d/%m'), ', '.join(names))
        await ctx.send(message)

    @tasks.loop(minutes=15)
    async def update_attendance_task(self):
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(defs.dir_path + '/client_secret.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open("Hive Mind Giga-Sheet").worksheet('Assessment Sheet')

        participants = get_participants()

        to_update = []
        col = raiders.get_col('attendance')

        for name in participants:
            attendance = round(participants[name]['attendance'] * 100)
            sheet_attendance = raiders.getRaiderAttribute(name, 'attendance')
            try: sheet_attendance = float(sheet_attendance.replace('%', ''))
            except ValueError: sheet_attendance = None
            if attendance != sheet_attendance:
                row = raiders.getRaiderAttribute(name, 'row')
                val = float(attendance) / 100
                to_update.append({'row': row, 'val': val})
        
        if len(to_update) > 0:
            min_row = min([u['row'] for u in to_update])
            max_row = max([u['row'] for u in to_update])
            first = gspread.utils.rowcol_to_a1(min_row, col)
            last = gspread.utils.rowcol_to_a1(max_row, col)

            cells = sheet.range('{}:{}'.format(first, last))

            for update in to_update:
                row = update['row'] - min_row 
                cells[row].value = update['val']
            
            sheet.update_cells(cells)
        
        logger.log_event('attendance_update', 'update_attendance task finished with {} updates.'.format(len(to_update)))

    def __init__(self, bot, error_messages_lifetime):
        self.bot = bot
        self.error_messages_lifetime = error_messages_lifetime
        self.update_attendance_task.start()