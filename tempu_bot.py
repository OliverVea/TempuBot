import discord
import asyncio
import datetime
import time

from discord.ext.tasks import loop
from discord.ext.commands import Bot

from wrapper_warcraftlogs import getReportsGuild, getReportFightCode

import raiders

# DEFINITIONS
debug = []
discord_token = 'NjU2ODgwNzM1MTM4ODczMzg1.XfpTpw.hiPmACInCE9vw-8QlbDjEBgD9hA'
channel_id_general = 539007626827005985

# SETUP
client = Bot('!')

# FUNCTIONS
dates = []
def addDate(channelid, dayStart, dayEnd, timeStart, timeEnd):
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    dayStart = days.index(dayStart)
    dayEnd = days.index(dayEnd)
    if (dayEnd < dayStart): dayEnd += 7

    hourStart, minuteStart = map(int, timeStart.split('.'))
    hourEnd, minuteEnd = map(int, timeEnd.split('.'))

    startDate = datetime.datetime(1, 1, dayStart, hourStart, minuteStart, 0, 0)
    endDate = datetime.datetime(1, 1, dayEnd, hourEnd, minuteEnd, 0, 0)

    entry = {'id': channelid, 'start': startDate, 'end': endDate}
    if 'addDate' in debug: print ('adddate', entry)
    dates.append(entry)

def isNow(dateStart, dateEnd):
    now = datetime.datetime.now()
    dayNow = now.weekday()
    hourNow = now.hour
    minuteNow = now.minute
    dateNow = datetime.datetime(1, 1, dayNow, hourNow, minuteNow, 0, 0)
    if 'isNow' in debug: print('isNow', dateStart, dateNow, dateEnd)
    return (dateStart <= dateNow <= dateEnd)

def getDateFromTimestamp(timestamp):
    date = datetime.utcfromtimestamp(timestamp/1000)
    dateString = date.strftime('%Y/%m/%d')
    return dateString

bossEncounterIDs = {663: 'Lucifron', 664: 'Magmadar', 665: 'Gehennas', 666: 'Garr', 667: 'Baron Geddon', 668: 'Shazzrah', 669: 'Sulfuron Harbinger', 670: 'Golemagg',671: 'Majordomo Executus', 672: 'Ragnaros', 1084: 'Onyxia'}

def getRecap(guildName):
    reports = getReportsGuild(guildName)
    latest_index = np.argmax([a['start'] for a in reports])
    latest_report_id = reports[latest_index]['id']
    latest_report = getReportFightCode(latest_report_id)

    print([key for key in latest_report])

    dateString = getDateFromTimestamp(int(latest_report['start']))
    participants = [a['name'] for a in latest_report['friendlies']]
    encounterIDs = [a['boss'] for a in latest_report['fights']]
    bossIDs = []
    for encounterID in encounterIDs:
        if encounterID in bossEncounterIDs: bossIDs.append(encounterID)

    playerResults = {}

    for name in participants:
        playerParses = getParses(name, queryTimeframe='historic')
        currentParses = []
        for parse in playerParses:
            parseDate = getDateFromTimestamp(parse['startTime'])
            if (parseDate == dateString):
                currentParses.append(parse)
        print(currentParses)
        return

def getRaids(months = 0):
    if (months == 0): queryStart = 0
    else: queryStart = int(time.time() - float(months) * 31 * 24 * 60 * 60) * 1000

    raids = getReportsGuild('Hive Mind', queryStart=queryStart)

    return raids

# LOOPS
@loop(seconds=5)
async def wclRaidTask():
    for entry in dates:
        if 'wclRaidTask' in debug: print('wclRaidTask', entry, entry['start'], entry['end'])

        if (isNow(entry['start'], entry['end'])):
            pass
            #Check warcraftlogs

# COMMANDS
@client.command(name = 'inspect')
async def wcl_inspect(ctx, *args):
    print('inspect', args)
    await ctx.send(args)

@client.command(name = 'addraid', help = 'Adds raid to the schedule. Example: \'!addraid sunday 19.30 sunday 22.00\'')
async def wcl_addraid(ctx, *args):
    print('addraid', len(args), args)

    if len(args) == 4:
        id = ctx.message.channel.id
        addDate(id, args[0], args[2], args[1], args[3])
    else:
        await ctx.send('Incorrect number of arguments. Use \'!help {}\' for help on how to use this feature.'.format(ctx.command.name))

@client.command(name = 'attendance', help = 'Creates a graph displaying raid attendance. Optionally includes amount of months to go back. Example: \'!attendance 3\'')
async def wcl_attendance(ctx, *args):
    # Argument handling
    if (len(args) == 0): 
        queryStart = 0
    elif (len(args) == 1): 
        queryStart = int(args[0])
    else: 
        await ctx.send('Incorrect number of arguments. Use \'!help {}\' for help on how to use this feature.'.format(ctx.command.name))
        return
    
    # Get raids from wcl
    raids = getRaids(queryStart)

    # Indentifying duplicate raids
    toIgnore = []
    for iA, raidA in enumerate(raids):
        if raidA['title'][0] is '_': toIgnore.append(iA)
        else:
            for iB, raidB in enumerate(raids):
                if iA is not iB:
                    if raidB['start'] <= raidA['start'] <= raidB['end']:
                        toIgnore.append(iA)
                        break
    
    removed = 0
    for i in toIgnore:
        del raids[i - removed]
        removed += 1

    participants = {}
    for i, raid in enumerate(raids):
        report = getReportFightCode(raid['id'])
        for friendly in report['friendlies']:
            name = friendly['name']
            if raiders.raiderExists(name):
                if name in participants:
                    participants[name]['earliestAttendance'] = i + 1
                    participants[name]['attendance'] += 1
                else:
                    participants[name] = {'attendance': 1, 'earliestAttendance': i + 1}
    
    print(participants)


# HANDLERS
@client.event
async def on_ready():
    print('on_ready')
    wclRaidTask.start()

# 
client.run(discord_token)

