import defs
import admin
import raiders
import attendance
import schedule
import performance

from discord.ext import tasks
from discord.ext.commands import Bot, has_permissions, has_any_role

with open(defs.dir_path + '/discord_token.txt') as f:
    discord_token = f.readline()

client = Bot('!')

print(defs.timestamp(), 'dir_path: ' + defs.dir_path)

@client.event
async def on_ready():
    print(defs.timestamp(), 'connected')

print(defs.timestamp(), 'starting discord bot with token:', discord_token.strip())
client.add_cog(admin.Admin(client))
client.add_cog(raiders.Raiders(client))
client.add_cog(attendance.Attendance(client, error_messages_lifetime=10))
client.add_cog(schedule.Schedule(client))
client.add_cog(performance.Performance(client))
client.run(discord_token.strip())