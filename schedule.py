import math
from datetime import datetime, date, time, timedelta

from discord.ext.commands import Cog, command, has_permissions, has_any_role, dm_only

import defs
import raiders
import logger

from file_handling import JSONFile

schedule_file = JSONFile('schedule.json', on_error={})

def addDate(channelid, dayStart, dayEnd, timeStart, timeEnd):
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    dayStart = days.index(dayStart) + 1
    dayEnd = days.index(dayEnd) + 1
    if (dayEnd < dayStart): dayEnd += 7

    hourStart, minuteStart = map(int, timeStart.split('.'))
    hourEnd, minuteEnd = map(int, timeEnd.split('.'))

    startDate = datetime(year=1, month=1, day=dayStart, hour=hourStart, minute=minuteStart)
    endDate = datetime(year=1, month=1, day=dayEnd, hour=hourEnd, minute=minuteEnd)

    entry = {'id': channelid, 'start': startDate.strftime('%d-%H:%M:%S'), 'end': endDate.strftime('%d-%H:%M:%S')}
    dates = schedule_file.get('dates')
    dates.append(entry)
    schedule_file.set('dates', dates)

def isNow(dateStart, dateEnd):
    now = datetime.now()
    dayNow = now.weekday() + 1
    hourNow = now.hour
    minuteNow = now.minute
    dateNow = datetime(year=1, month=1, day=dayNow, hour=hourNow, minute=minuteNow).strftime('%d-%H:%M:%S')
    if dateNow < dateStart: dateNow = datetime(year=1, month=1, day=dayNow + 7, hour=hourNow, minute=minuteNow).strftime('%d-%H:%M:%S')
    return (dateStart <= dateNow <= dateEnd)

def getDateFromtimestamp(timestamp):
    date = datetime.utcfromtimestamp(timestamp/1000)
    dateString = date.strftime('%d/%m/%Y')
    return dateString

def get_date_from_string(date_str):
    delimiters = ['.', '/']
    assigned = False
    for delim in delimiters:
        if delim in date_str:
            assigned = True
            dates = date_str.split(delim)
    if not assigned or len(dates) > 2:
        raise TypeError(date_str)
    year = datetime.now().year
    date = datetime(year, int(dates[1]), int(dates[0]))
    if date < datetime.now():
        date.replace(year=year + 1)
    return date

def has_signed_off(name, date):
    if isinstance(date, int): date = datetime.fromtimestamp(date / 1000).date

    return False

class Schedule(Cog):
    def __init__(self, bot):
        self.bot = bot
                
    @dm_only()
    @command(name='signoff', help= 'This command allows you to sign off. Date is in the format DD.MM or DD/MM.\nWays to use this command:\n!signoff NAME DATE\n!signoff NAME DATE REASON\n!signoff NAME START-END\n!signoff NAME START-END REASON\n\nExamples:\n!signoff Tempia 12.01\n!signoff Matitka 19.01 I\'m ill.\n!signoff Bambiqt 11.03-29.03\n!signoff Peanut 23.04-13.05 Away on holiday.')
    async def signoff(self, ctx, *args):
        logger.log_command(ctx, args)
        if len(args) < 2:
            await ctx.send('Too few arguments. Use \'!help {}\' for info on how to use this function.'.format(ctx.command.name))
            return
        
        name = args[0].lower()

        raider_names = raiders.getRaiderNames()
        for raider_name in raider_names:
            if raider_name.lower() in name:
                name = raider_name

        if not raiders.raiderExists(name):
            await ctx.send('{} is not a raider. Use \'!help {}\' for info on how to use this function.'.format(name, ctx.command.name))
            return

        reason = ' '.join(args[2:])

        signoff = {'name': name, 'reason': reason}

        dates_str = args[1].split('-')

        if len(dates_str) == 1:
            date = get_date_from_string(dates_str[0])

            if (date < (datetime.now() - timedelta(days=1))):
                await ctx.send('It is too late to sign off for {}. Use \'!help {}\' for info on how to use this function.'.format(date.strftime('%d/%m'), ctx.command.name))
                return
            
            epoch = datetime(1970, 1, 1)
            diff = date - epoch
            timestamp = int(diff.total_seconds() * 1000)

            signoff['start'] = timestamp
            signoff['end'] = timestamp

            ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(math.floor(n/10)%10!=1)*(n%10<4)*n%10::4])
            message = '{} signed off for {} the {} of {}.'.format(name.capitalize(), date.strftime('%A'), ordinal(date.day), date.strftime('%B'))
            if (reason != ''): message += ' Reason: "{}"'.format(reason)
            
        else:
            start = get_date_from_string(dates_str[0])
            end = get_date_from_string(dates_str[1])

            if (end < start):
                await ctx.send('End \'{}\' is earlier than start \'{}\'. Use \'!help {}\' for info on how to use this function.'.format(end.strftime('%d/%m'), start.strftime('%d/%m'), ctx.command.name))
                return

            if (end < (datetime.now() - timedelta(days=1))):
                await ctx.send('It it too late to sign off for {}. Use \'!help {}\' for info on how to use this function.'.format(end.strftime('%d/%m'), ctx.command.name))
                return

            if start > end:
                start.replace(year=start.year - 1)

            epoch = datetime(1970, 1, 1)
            ts_start = int((start - epoch).total_seconds() * 1000)
            ts_end = int((end - epoch).total_seconds() * 1000)

            signoff['start'] = ts_start
            signoff['end'] = ts_end

            ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(math.floor(n/10)%10!=1)*(n%10<4)*n%10::4])
            message = '{} signed off from the {} of {} to the {} of {}.'.format(name.capitalize(), ordinal(start.day), start.strftime('%B'), ordinal(end.day), end.strftime('%B'))
            if (reason != ''): message += ' Reason: "{}"'.format(reason)

        signoffs = schedule_file.get('signoffs')
        signoffs.append(signoff)
        schedule_file.set('signoffs', signoffs)

        await ctx.send(message)
        channel_id = schedule_file.get('signoffs_channel')
        channel = self.bot.get_channel(channel_id)
        await channel.send(message)  

    @command(name='setsignoffschannel', help='Sets the signoff channel to the message this command is sent in.')
    @has_permissions(administrator=True)
    async def set_signoffs_channel(self, ctx, *args):
        logger.log_command(ctx, args)
        try: await ctx.message.delete()
        except: pass
        if (len(args) != 0):
            await ctx.send('This command takes does not take any arguments.')
            return
        
        schedule_file.set('signoffs_channel', ctx.message.channel.id)

    @command(name='signoffs', help='Reports the raiders that have signed off for a given date. Example: \'!signoffs 18.01\'')
    @has_any_role('Officer', 'Admin')
    async def signoffs(self, ctx, *args):
        logger.log_command(ctx, args)
        try: await ctx.message.delete()
        except: pass

        if len(args) is 1: query_date = get_date_from_string(args[0])
        elif len(args) is 0: query_date = datetime.combine(date.today(), time())
        else:
            await ctx.send('This command takes at most one argument: the date. Use \'!help {}\' for help on how to use this command.'.format(ctx.command.name))
            return

        epoch = datetime(1970, 1, 1)
        timestamp = int((query_date - epoch).total_seconds() * 1000)

        signoffs = schedule_file.get('signoffs')

        names = [so['name'].lower().capitalize() for so in signoffs if so['start'] <= timestamp <= so['end']]
        
        message = 'Sign offs: ' + ', '.join(names) + '\n'
        
        roles_so = {}
        for name in names:
            role = raiders.getRaiderAttribute(name, 'role')
            roles_so[role] = roles_so.get(role, 0) + 1

        all_raiders = raiders.getRaiders()
        roles_at = {}
        for raider in all_raiders:
            if not raider.capitalize() in names:
                role = all_raiders[raider]['role']
                roles_at[role] = roles_at.get(role, 0) + 1

        roles = ['{}: {}'.format(role.capitalize(), roles_so[role]) for role in roles_so]
        message += 'Signed off ({}): '.format(sum(roles_so.values())) + ', '.join(roles) + '\n'
        roles = ['{}: {}'.format(role.capitalize(), roles_at[role]) for role in roles_at]
        message += 'Attending ({}): '.format(sum(roles_at.values())) + ', '.join(roles)

        await ctx.send(message)
        
    @command(name='ar', help='Adds a raid to the schedule. Example: \'!ar sunday 12.00 sunday 14.30\'')
    @has_permissions(administrator=True)
    async def add_raid(self, ctx, *args):
        logger.log_command(ctx, args)
        try: await ctx.message.delete()
        except: pass

        if len(args) == 4:
            id = ctx.message.channel.id
            addDate(id, args[0], args[2], args[1], args[3])
        else:
            await ctx.send(content='Incorrect number of arguments. Use \'!help {}\' for help on how to use this feature.'.format(ctx.command.name))

    @command(name = 'rr', help="Removes a raid from the schedule. You select raid by index in \'!lr\'. Example: \'!rr -1\' would remove the last raid.")
    @has_permissions(administrator=True)
    async def wcl_remove_raid(self, ctx, *args):
        logger.log_command(ctx, args)
        try: await ctx.message.delete()
        except: pass

        if len(args) == 1:
            i = int(args[0])
            dates = schedule_file.get('dates')
            del dates[i]
            schedule_file.set('dates', dates)
        else:
            await ctx.send(content='Incorrect number of arguments. Use \'!help {}\' for help on how to use this feature.'.format(ctx.command.name))

    @command(name = 'lr', help='Lists the raids on the schedule. Example: \'!lr\'')
    @has_any_role('Officer', 'Admin')
    async def wcl_list_raids(self, ctx, *args):
        logger.log_command(ctx, args)
        try: await ctx.message.delete()
        except: pass

        if len(args) == 0:
            dates = schedule_file.get('dates')
            message = "**Raid Times:**\n"
            for i, entry in enumerate(dates):
                message += '{} - id: {}, start: {}, end: {}\n'.format(i, entry['id'], entry['start'], entry['end'])
            await ctx.send(content=message)
        else:
            await ctx.send(content='Incorrect number of arguments. Use \'!help {}\' for help on how to use this feature.'.format(ctx.command.name))