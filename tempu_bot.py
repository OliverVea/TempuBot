import defs
print(defs.timestamp(), 'dir_path: ' + defs.dir_path)

import os
import psutil
import asyncio
import socket
from urllib.request import urlopen, Request
import discord

pid = 0
process_name = ''
ext_ip = ''
host_name = ''
host_ip = ''

try:
    r = Request('https://ipapi.co/ip/', headers={'User-Agent': 'Mozilla/5.0'})
    ext_ip = str(urlopen(r).read())[2:-1]
    print(defs.timestamp(), 'external ip:', ext_ip)
except: print (defs.timestamp(), 'External IP could not be determinated.')

try:
    host_name = socket.gethostname() 
    print(defs.timestamp(), 'hostname:', host_name)
    host_ip = socket.gethostbyname(host_name)
    print(defs.timestamp(), 'local ip:', host_ip)
except: print(defs.timestamp(), 'Local network information could not be found.')

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
    tempia = admin.get_tempia(client)
    message = 'Bot rebooted.\n **Process Name**: {}\n **PID**: {}\n **Hostname**: {}\n **Local IP**: {}\n **External IP**: {}'.format(process_name, str(pid), host_name, host_ip, ext_ip)
    await tempia.send(message)
    print(defs.timestamp(), 'connected')

import logger
import admin
import raiders
import attendance
import schedule
import performance

logger.set_info(hostname=host_name, local_ip=host_ip, external_ip=ext_ip, pid=pid, process_name=process_name)
logger.log_event('reboot', 'Rebooted with pid {} and public ip {}.'.format(str(pid), ext_ip))

client.add_cog(logger.Logger(client))
client.add_cog(admin.Admin(client))
client.add_cog(raiders.Raiders(client))
client.add_cog(attendance.Attendance(client, error_messages_lifetime=10))
client.add_cog(schedule.Schedule(client))
client.add_cog(performance.Performance(client))

with open(defs.dir_path + '/discord_token.txt') as f:
    discord_token = f.readline().strip()
print(defs.timestamp(), 'starting discord bot with token:', discord_token)

client.run(discord_token)