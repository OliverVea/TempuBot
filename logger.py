import defs
import file_handling
import os

from datetime import datetime
from discord.ext.commands import Cog

log_file = file_handling.JSONFile(
    filename='log.json', 
    #location=os.getenv('TEMPUBOT_LOG_PATH', defs.dir_path),
    encoding='utf-16-le'
)

def append_entry(entry):
    print(defs.timestamp(), list(entry.values()))
    log = log_file.get('log')
    log.append(entry)
    log_file.set('log', log)


def log_message(message):
    append_entry({
        'type': 'message',
        'date': str(datetime.now().strftime('%Y/%m/%d')),
        'time': str(datetime.now().strftime('%H:%M:%S')),
        'author': str(message.author), 
        'channel': str(message.channel), 
        'message': str(message.content)
    })

def log_command(ctx, args):
    append_entry({
        'type': 'command',
        'date': str(datetime.now().strftime('%Y/%m/%d')),
        'time': str(datetime.now().strftime('%H:%M:%S')),
        'author': str(ctx.author), 
        'command': str(ctx.command.name), 
        'channel': str(ctx.channel), 
        'args': str(args), 
        'message': str(ctx.message.content)
    })

def log_error(error, message):
    append_entry({
        'type': 'error',
        'date': str(datetime.now().strftime('%Y/%m/%d')),
        'time': str(datetime.now().strftime('%H:%M:%S')),
        'event': str(error), 
        'message': str(message)
    })

def log_event(event, description):
    append_entry({
        'type': 'event',
        'date': str(datetime.now().strftime('%Y/%m/%d')),
        'time': str(datetime.now().strftime('%H:%M:%S')),
        'event': str(event), 
        'message': str(description)
    })

class Logger(Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # @Cog.listener()
    # async def on_error(self, event, *args, **kwargs):
    #     log_error(event, 'args: {}, kwargs: {}'.format(args, kwargs))

    # @Cog.listener()
    # async def on_command_error(self, ctx, exc):
    #     message = '{} ({}): \'{}\'. {}'.format(ctx.author, ctx.message.channel, ctx.message.content, exc)
    #     log_error('command_error', message)

