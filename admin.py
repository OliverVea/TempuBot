from discord.ext.commands import Cog, command, has_permissions, has_any_role
from random import choice
import discord
import re

import defs
from file_handling import JSONFile

admin_file = JSONFile('admin.json')

admin_file.get('welcome_message', on_error='')

class Admin(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_member_join(self, member):
        await member.send(admin_file.get('welcome_message'))
        print(defs.timestamp(), member, 'joined server.')
        
    @Cog.listener()
    async def on_message(self, message):
        if ('bambi' in message.content.lower() and admin_file.get('reaction_bambi', False)):
            emojis = list(message.guild.emojis)
            for emoji in emojis:
                if (emoji.name.lower() == 'bambi'):
                    await message.add_reaction(emoji)
                    return      
                    
        if ('temp' in message.content.lower() and admin_file.get('reaction_tempia', False)):
            emojis = list(message.guild.emojis)
            for emoji in emojis:
                if (emoji.name.lower() == 'ayaya'):
                    await message.add_reaction(emoji)
                    return      

    @command(name = 'echo')
    @has_any_role('Officer', 'Admin')
    async def echo(self, ctx, *args):
        try: await ctx.message.delete()
        except: pass
        if len(ctx.message.content) == len(ctx.command.name) + 1:
            emojis = list(ctx.message.guild.emojis)
            await ctx.send(choice(emojis))
        else:
            await ctx.send(ctx.message.content[len(ctx.command.name) + 2:])
        print(defs.timestamp(), 'echo', ctx.author, ctx.channel.name, args)

    @command(name = 'announcementchannel')
    @has_any_role('Admin')
    async def announcementchannel(self, ctx, *args):
        try: 
            admin_file.set('announcement_channel_id', ctx.message.channel.id)
            await ctx.message.delete()
        except:
            pass    
        print(defs.timestamp(), 'announcement_channel', ctx.author, ctx.channel.name, args)

    @command(name = 'annend')
    @has_any_role('Admin')
    async def announementend(self, ctx, *args):
        try: 
            admin_file.set('announcement_end', ctx.message.content[len(ctx.command.name) + 2:])
            await ctx.message.delete()
        except:
            pass
        print(defs.timestamp(), 'announcement_channel', ctx.author, ctx.channel.name, args)

    @command(name = 'ann')
    @has_any_role('Officer', 'Admin')
    async def announcement(self, ctx, *args):
        print(defs.timestamp(), 'ann', ctx.author, ctx.channel.name, args)
        try: 
            await ctx.message.delete()
            channel_id = admin_file.get('announcement_channel_id')
            channel = self.bot.get_channel(channel_id)
            message = ctx.message.content[len(ctx.command.name) + 2:] + '\n'
            message += admin_file.get('announcement_end', on_error='')
            await channel.send(message)
        except: 
            pass

    @command(name='welcome', help='Displays the welcome message.')
    @has_any_role('Officer', 'Admin')
    async def welcome(self, ctx, *args):
        try: await ctx.message.delete()
        except: pass
        await ctx.send(admin_file.get('welcome_message'))
        print(defs.timestamp(), 'welcome', ctx.author, ctx.channel.name, args)

    @command(name='setwelcome', help='Sets the welcome message.')
    @has_permissions(administrator=True)
    async def setwelcome(self, ctx, *args):
        try: await ctx.message.delete()
        except: pass

        message = ' '.join(args)
        
        admin_file.set('welcome_message', message)
        await ctx.send('Welcome message set to \'{}\'.'.format(admin_file.get('welcome_message')))
        print(defs.timestamp(), 'welcome', ctx.author, ctx.channel.name, args)

    @command(name='disable', help='Disables command. Example: \'!disable clear\'')
    @has_permissions(administrator=True)
    async def disable(self, ctx, *args):
        try: await ctx.message.delete()
        except: pass
        print(defs.timestamp(), 'disable', ctx.author, ctx.channel.name, args)
        if (len(args) != 1):
            await ctx.send('Incorrect amount of arguments received. ({})'.format(len(args)), delete_after=10)
            return
            
        admin_file.set(args[0], False)

    @command(name='enable', help='Enables command that was previously disabled. Example: \'!enable clear\'')
    @has_permissions(administrator=True)
    async def enable(self, ctx, *args):
        try: await ctx.message.delete()
        except: pass
        print(defs.timestamp(), 'enable', ctx.author, ctx.channel.name, args)
        if (len(args) != 1):
            await ctx.send('Incorrect amount of arguments received. ({})'.format(len(args)), delete_after=10)
            return      
            
        admin_file.set(args[0], True)

    @command(name='clear', help='Clears X messages, where X is the argument. Example: \'!clear 50\'')
    @has_permissions(administrator=True)
    async def clear(self, ctx, *args):
        try: await ctx.message.delete()
        except: pass
        print(defs.timestamp(), 'clear', ctx.author, ctx.channel.name, args)
        if (not admin_file.get(ctx.command.name, True)):
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
                messages = await ctx.message.channel.history(limit=100).flatten()
                messages = [message for message in messages if message.author.id == mention_id][:to_clear]
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
        
    @command(name='clearuntil', help='Clears messages until a message starting with the argument is found. Example: \'!clearuntil Matitka Sucks\'')
    @has_permissions(administrator=True)
    async def clear_until(self, ctx, *args):
        print(defs.timestamp(), 'clearuntil', ctx.author, ctx.channel.name, args)
        if (len(args) == 0):
            await ctx.send()
            return 

        arg = ' '.join(args)
        messages = await ctx.message.channel.history(limit=100).flatten()
        matches = [message.content.startswith(arg) for message in messages]

        if True in matches:
            messages = messages[:matches.index(True) + 1]
            await ctx.message.channel.delete_messages(messages)
        else:
            await ctx.send('Message \'{}\' not found.'.format(arg), delete_after=10)

        
