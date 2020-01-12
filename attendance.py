from time import time
import json
import os
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('discord')

import discord
from discord.ext import tasks
from discord.ext.commands import Cog, command, has_permissions, has_any_role

import defs
from wrapper_warcraftlogs import getReportsGuild, getReportFightCode
import raiders
from file_handling import JSONFile

earliest_next_update = 30 * 60 #Minutes
last_update = 0

attendance_file = JSONFile('attendance.json')

def get_query_start(days, months):
    query_start = 0
    if days != None and months != None:
        raise ValueError('Both days and months set.')
    elif days != None:
        if not isinstance(days, (int, float)): raise TypeError('days is not a number.')
        else: query_start = int(time() * 1000 - float(days) * 24 * 60 * 60 * 1000)
    elif months != None:
        if not isinstance(months, (int, float)): raise TypeError('months is not a number.')
        else: query_start = int(time() * 1000 - float(months) * 31 * 24 * 60 * 60 * 1000)
    return query_start

def get_raids(guild = 'Hive Mind', days = None, months = None):
    return getReportsGuild(guild, queryStart=get_query_start(days, months))

def filter_raids(raids):
    filtered = [raid for raid in raids if not any([_raid['start'] < raid['start'] <= _raid['end'] for _raid in raids])]
    filtered = [raid for raid in filtered if not raid['title'].startswith('_')]

    return filtered

def get_attendance(guild='Hive Mind', update_attendance = True, days = None, months = None):
    global last_update, earliest_next_update
    attendance = attendance_file.read()

    if guild not in attendance:
        attendance[guild] = {}
        last_update = 0

    if update_attendance and last_update + earliest_next_update < time():
        last_update = time()
        raids = get_raids(guild, days, months)
        raids = filter_raids(raids)
        for raid in raids:
            if raid['id'] not in attendance[guild]:
                print(defs.timestamp(), 'Adding raid (' + raid['id'] + ') to the attendance file.') 
                report = getReportFightCode(raid['id'])

                participants = [participant['name'] for participant in report['exportedCharacters']]

                raid_entry = {'start': raid['start'], 'title': raid['title'], 'participants': participants}

                attendance[guild][raid['id']] = raid_entry
            attendance_file.write(attendance)

    
    start = get_query_start(days, months)
    filtered_attendance = [attendance[guild][raid_id] for raid_id in attendance[guild] if attendance[guild][raid_id]['start'] > start]

    return filtered_attendance

def get_participants(guild = 'Hive Mind', update_attendance=True, days = None, months = None):
    attendance = get_attendance(guild, update_attendance, days, months)
    participants = {}

    # Count attendance
    for raid in attendance:
        for participant in raid['participants']:
            if (raiders.raiderExists(participant)):
                if not participant in participants:
                    participants[participant] = {'raids':[]}
                participants[participant]['raids'].append(raid['start'])
    
    for name in participants:
        participants[name]['first_raid'] = min(participants[name]['raids'])   

    # Count absence
    for name in participants:
        missed_raids = []
        for raid in attendance:
            start = raid['start']
            if not start in participants[name]['raids']:
                if start > participants[name]['first_raid']:
                    missed_raids.append(start)
        participants[name]['missed_raids'] = missed_raids

    for name in participants:
        participants[name]['attendance'] = len(participants[name]['raids']) / (len(participants[name]['raids']) + len(participants[name]['missed_raids']))

    return participants


def get_participant(name, guild = 'Hive Mind', update_attendance=True, days = None, months = None):
    attendance = get_attendance(guild, update_attendance, days, months)
    participant = {'raids': [], 'missed_raids': []}

    participant['raids'] = [raid['start'] for raid in attendance if name in raid['participants']]

    if (len(participant['raids']) > 0):
        participant['first_raid'] = min(participant['raids'])

        possible_raids = [raid['start'] for raid in attendance if raid['start'] > participant['first_raid']]
        participant['missed_raids'] = [raid for raid in possible_raids if raid not in participant['raids']]
        participant['attendance'] = len(participant['raids']) / (len(participant['raids']) + len(participant['missed_raids']))
    
    else: 
        participant['first_raid'] = time() * 1000
        participant['attendance'] = 0

    return participant

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
            if category['type'] is 'player':
                message += '__**{}**__ - '.format(name.capitalize())
            else:
                message += '**{}** - '.format(name.capitalize())
            attended_raids = len(player_attendance['raids'])

            if (attended_raids == 0):
                message += 'no raids registered.\n'
            else:
                attendance = round(player_attendance['attendance'] * 100)
                missed_raids = len(player_attendance['missed_raids'])
                message += 'attendance: **{}%**, attended raids: **{}**, missed raids: **{}**\n'.format(attendance, attended_raids, missed_raids)
        
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
    def __init__(self, bot, error_messages_lifetime):
        self.bot = bot
        self.error_messages_lifetime = error_messages_lifetime

    @command(name='attendance')
    @has_any_role('Officer', 'Admin')
    async def cmd_attendance(self, ctx, *args):
        await ctx.message.delete()
        print(defs.timestamp(), 'attendance', ctx.author, ctx.channel.name, args)
        args = list(args)
        _ = defs.get_options(args)

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
        
        categories = []
        for arg in args:
            if (arg in defs.classes) or ((arg[-1] is 's') and (arg[:-1] in defs.classes)):
                class_raiders = raiders.all_with_attribute('class', arg)
                class_names = [raider for raider in class_raiders]
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

    @command(name='attendanceplot')
    async def cmd_attendance_plot(self, ctx, *args):
        await ctx.message.delete()
        print(defs.timestamp(), 'attendanceplot', ctx.author, ctx.channel.name, args)
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
