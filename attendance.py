from time import time
import json
import numpy as np
import matplotlib.pyplot as plt

from defs import dir_path, timestamp, load_json_file, colors
import defs
from wrapper_warcraftlogs import getReportsGuild, getReportFightCode
from raiders import raiderExists, getRaiderAttribute

earliest_next_update = 30 * 60 #Minutes
last_update = 0

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
    # Indentifying duplicate raids
    to_remove = []
    for iA, raidA in enumerate(raids):
        if raidA['title'].startswith('_'): to_remove.append(iA)
        else:
            for iB, raidB in enumerate(raids):
                if iA is not iB:
                    if raidB['start'] <= raidA['start'] <= raidB['end']:
                        to_remove.append(iA)
                        break
    
    for removed, i in enumerate(to_remove): del raids[i - removed]

    return raids

def get_attendance(guild='Hive Mind', update_attendance = True, days = None, months = None):
    global last_update, earliest_next_update
    attendance = load_json_file(dir_path + '/attendance.json')

    if guild not in attendance:
        attendance[guild] = {}
        last_update = 0

    if update_attendance and last_update + earliest_next_update < time():
        last_update = time()
        raids = get_raids(guild, days, months)
        raids = filter_raids(raids)
        for raid in raids:
            if raid['id'] not in attendance[guild]:
                print(timestamp(), 'Adding raid (' + raid['id'] + ') to the attendance file.') 
                report = getReportFightCode(raid['id'])

                participants = [participant['name'] for participant in report['exportedCharacters']]

                raid_entry = {'start': raid['start'], 'title': raid['title'], 'participants': participants}

                attendance[guild][raid['id']] = raid_entry
            json.dump(attendance, open(dir_path + '/attendance.json', 'w', encoding=defs.encoding), ensure_ascii=False, indent=4)

    ids = [raid_id for raid_id in attendance[guild]]
    for raid_id in ids:
        raid_start = attendance[guild][raid_id]['start']
        if raid_start < get_query_start(days, months):
            del attendance[guild][raid_id]

    return attendance[guild]

def get_participants(guild = 'Hive Mind', update_attendance=True, days = None, months = None):
    attendance = get_attendance(guild, update_attendance, days, months)
    participants = {}

    # Count attendance
    for raid_id in attendance:
        raid = attendance[raid_id]
        for participant in raid['participants']:
            if (raiderExists(participant)):
                if not participant in participants:
                    participants[participant] = {'raids':[]}
                participants[participant]['raids'].append(raid['start'])
    
    for name in participants:
        participants[name]['first_raid'] = min(participants[name]['raids'])   

    # Count absence
    for name in participants:
        missed_raids = []
        for raid_id in attendance:
            start = attendance[raid_id]['start']
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

    for raid_id in attendance:
        raid = attendance[raid_id]
        if name in raid['participants']: 
            participant['raids'].append(raid['start'])
    
    if (len(participant['raids']) > 0):
        participant['first_raid'] = min(participant['raids'])

        for raid_id in attendance:
            raid = attendance[raid_id]
            if not name in raid['participants'] and raid['start'] > participant['first_raid']: 
                participant['missed_raids'].append(raid['start'])
        
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
    attendances = [entry[1] for entry in attendances]

    cols = [colors[getRaiderAttribute(name, 'class')] for name in names]
    
    y_pos = np.arange(len(names))

    for i in y_pos:
        names[i] = names[i] + ' (' + str(round(attendances[i] * 100, 1)) + '%)'

    _, ax = plt.subplots(figsize=(20,15))

    ax.barh(y_pos, attendances, color=cols, edgecolor='black', linestyle='-', linewidth=1)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel('Attendance', color='white')

    plt.savefig(dir_path + '/' + figurename)