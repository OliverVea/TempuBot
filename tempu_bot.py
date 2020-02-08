import defs
print(defs.timestamp(), 'dir_path: ' + defs.dir_path)

import os
import psutil

pid = 0
process_name = ''

try:
    pid = os.getpid()
    print(defs.timestamp(), 'os pid:', pid)
    process_name = psutil.Process(pid).name()
    print(defs.timestamp(), 'process name:', process_name)
except AttributeError: print(defs.timestamp(), 'pid could not be identified.')
try: print(defs.timestamp(), 'os info:', os.uname())
except AttributeError: print(defs.timestamp(), 'system status could not be found.')

from discord.ext.commands import Bot
client = Bot('!')

@client.event
async def on_ready():
    print(defs.timestamp(), 'connected')

import logger
logger.set_info(pid, process_name)
logger.log_event('reboot', 'Rebooted with pid {}.'.format(str(pid)))
client.add_cog(logger.Logger(client))

import admin
client.add_cog(admin.Admin(client))

import raiders
client.add_cog(raiders.Raiders(client))

import attendance
client.add_cog(attendance.Attendance(client, error_messages_lifetime=10))

import schedule
client.add_cog(schedule.Schedule(client))

import performance
client.add_cog(performance.Performance(client))

with open(defs.dir_path + '/discord_token.txt') as f:
    discord_token = f.readline().strip()
print(defs.timestamp(), 'starting discord bot with token:', discord_token)

client.run(discord_token)