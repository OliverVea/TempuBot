from discord.ext.commands import Cog, command, has_permissions, has_any_role
import discord
import re

import defs
from file_handling import JSONFile

admin_file = JSONFile('admin.json')

admin_file.get('welcome_message', on_error='')

class Admin(Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @Cog.listener()
    async def on_member_join(self, member):
        await member.send(admin_file.get('welcome_message'))
        
    @command(name = 'echo')
    @has_any_role('Officer', 'Admin')
    async def echo(self, ctx, *args):
        await ctx.message.delete()
        await ctx.send(content=' '.join(args) + ' :slight_smile:')
        print(defs.timestamp(), 'echo', ctx.author, args)

    @command(name='welcome', help='Displays the welcome message.')
    @has_any_role('Officer', 'Admin')
    async def welcome(self, ctx, *args):
        await ctx.message.delete()
        print(defs.timestamp(), 'welcome', ctx.author, args)
        await ctx.send(admin_file.get('welcome_message'))

    @command(name='setwelcome', help='Sets the welcome message.')
    @has_permissions(administrator=True)
    async def setwelcome(self, ctx, *args):
        await ctx.message.delete()
        print(defs.timestamp(), 'welcome', ctx.author, args)

        message = ' '.join(args)
        
        admin_file.set('welcome_message', message)
        await ctx.send('Welcome message set to \'{}\'.'.format(admin_file.get('welcome_message')))


    @command(name='disable', help='Disables command. Example: \'!disable clear\'')
    @has_permissions(administrator=True)
    async def disable(self, ctx, *args):
        await ctx.message.delete()
        print(defs.timestamp(), 'disable', ctx.author, args)
        if (len(args) != 1):
            await ctx.send('Incorrect amount of arguments received. ({})'.format(len(args)), delete_after=10)
            return
        
        command = args[0]

        disabled_commands = admin_file.get('disabled_commands')

        if (command in disabled_commands):
            await ctx.send('Command \'!{}\' already disabled.'.format(command), delete_after=10)
            return

        disabled_commands.append(command)
        admin_file.set('disabled_commands', disabled_commands)

        await ctx.send('Command \'!{}\' disabled.'.format(command), delete_after=10)

    @command(name='enable', help='Enables command that was previously disabled. Example: \'!enable clear\'')
    @has_permissions(administrator=True)
    async def enable(self, ctx, *args):
        await ctx.message.delete()
        print(defs.timestamp(), 'enable', ctx.author, args)
        if (len(args) != 1):
            await ctx.send('Incorrect amount of arguments received. ({})'.format(len(args)), delete_after=10)
            return
        
        command = args[0]
        
        disabled_commands = admin_file.get('disabled_commands')

        if (not command in disabled_commands):
            await ctx.send('Command \'!{}\' is not disabled.'.format(command), delete_after=10)
            return

        del disabled_commands[disabled_commands.index(command)]
        admin_file.set('disabled_commands', disabled_commands)

        await ctx.send('Command \'!{}\' enabled.'.format(command), delete_after=10)

    @command(name='clear', help='Clears X messages, where X is the argument. Example: \'!clear 50\'')
    @has_permissions(administrator=True)
    async def clear(self, ctx, *args):
        await ctx.message.delete()
        print(defs.timestamp(), 'clear', ctx.author, args)
        if (ctx.command.name in admin_file.get('disabled_commands')):
            await ctx.send('Command disabled. Enable with \'!enable {}\''.format(ctx.command.name), delete_after=5)
            return
            
        if (len(args) == 0 or len(args) > 2):
            await ctx.send('Incorrect amount of arguments received. ({})'.format(len(args)), delete_after=10)
            return
        
        mention_id = None
        to_clear = -1

        for arg in args:
            if (arg.isdigit()):
                to_clear = int(arg)
            elif (re.compile('^<@[0-9]{18}>$').match(arg.replace('!', ''))): 
                mention_id = arg.replace('!', '')
                mention_id = int(mention_id[2:-1])
            else:
                await ctx.send('Argument \'{}\' in message \'{}\' not understood.'.format(arg, ctx.message.content), delete_after=10)
                return


        if (mention_id != None and to_clear != -1):
            while to_clear > 0 :
                messages = await ctx.message.channel.history(limit=min(to_clear, 100)).flatten()
                messages = [message for message in messages if message.author.id == mention_id]
                if (len(messages) == 0): break
                to_clear -= len(messages)
                await ctx.message.channel.delete_messages(messages)

        elif (mention_id != None):
            messages = await ctx.message.channel.history(limit=100).flatten()
            messages = [message for message in messages if message.author.id == mention_id]
            await ctx.message.channel.delete_messages(messages)

        elif (to_clear != -1):
            while to_clear > 0:
                messages = await ctx.message.channel.history(limit=min(to_clear, 100)).flatten()
                to_clear -= len(messages)
                await ctx.message.channel.delete_messages(messages)
