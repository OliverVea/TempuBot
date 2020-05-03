from discord.ext.commands import Cog, command, has_permissions, has_any_role
from random import choice
import discord
import re
from contextlib import suppress

import defs
import logger
from file_handling import JSONFile

admin_file = JSONFile('admin.json')

admin_file.get('welcome_message', on_error='')

def get_role(rolename, roles):
    for role in roles:
        if role.name == rolename:
            return role
    return None

async def reaction_change(payload, guild, status):
    reactions = admin_file.get('reactions', {})

    channel_id = str(payload.channel_id)
    if channel_id not in reactions:
        return
    
    message_id = str(payload.message_id)
    if message_id not in reactions[channel_id]:
        return

    reactions = reactions[channel_id][message_id]

    emoji = str(payload.emoji)
    for reaction in reactions:
        if reaction['reaction'] == emoji:
            role = get_role(reaction['role'], guild.roles)

            member = guild.get_member(payload.user_id)

            if status: 
                await member.add_roles(role)
                logger.log_event('addrole', 'added role {} to user {}.'.format(role, member))
            else: 
                await member.remove_roles(role)
                logger.log_event('removerole', 'removed role {} from user {}.'.format(role, member))
            

class Admin(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reaction_dict = {}

    @Cog.listener()
    async def on_member_join(self, member):
        await member.send(admin_file.get('welcome_message', on_error=''))
        print(defs.timestamp(), member, 'joined server.')
        
    @Cog.listener()
    async def on_message(self, message):
        if (isinstance(message.channel, discord.DMChannel)):
            logger.log_message(message)
            return

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

    @command(name = 'echo', help='Echoes your input. Example:\'!echo Echo\'')
    @has_any_role('Officer', 'Admin')
    async def echo(self, ctx, *args):
        logger.log_command(ctx, args)
        with suppress(): await ctx.message.delete()

        if len(ctx.message.content) == len(ctx.command.name) + 1:
            emojis = list(ctx.message.guild.emojis)
            await ctx.send(choice(emojis))
        else:
            await ctx.send(ctx.message.content[len(ctx.command.name) + 2:])

    @command(name = 'announcementchannel', help='Sets the announcement channel to the channel this command is sent in.')
    @has_any_role('Admin')
    async def announcementchannel(self, ctx, *args):
        logger.log_command(ctx, args)
        with suppress(): await ctx.message.delete()
        admin_file.set('announcement_channel_id', ctx.message.channel.id)

    @command(name = 'annend', help='Sets the ending of all announcements to this message. Example: \'!annend Thank you for listening~\'')
    @has_any_role('Admin')
    async def announementend(self, ctx, *args):
        logger.log_command(ctx, args)
        with suppress(): await ctx.message.delete()
        admin_file.set('announcement_end', ctx.message.content[len(ctx.command.name) + 2:])

    @command(name = 'ann', help='Makes an announcement in the announcement channel. Example:\'!ann This is an announcement.\'')
    @has_any_role('Officer', 'Admin')
    async def announcement(self, ctx, *args):
        logger.log_command(ctx, args)
        with suppress():
            await ctx.message.delete()
            channel_id = admin_file.get('announcement_channel_id', on_error=-1)
            if channel_id is -1:
                channel = ctx
                message = 'Announcement channel not set.'
            else:
                channel = self.bot.get_channel(channel_id)
                message = ctx.message.content[len(ctx.command.name) + 2:] + '\n'
                message += admin_file.get('announcement_end', on_error='')
            await channel.send(message)

    @command(name='welcome', help='Displays the welcome message.')
    @has_any_role('Officer', 'Admin')
    async def welcome(self, ctx, *args):
        logger.log_command(ctx, args)
        with suppress(): await ctx.message.delete()
        await ctx.send(admin_file.get('welcome_message', on_error=''))

    @command(name='setwelcome', help='Sets the welcome message.')
    @has_permissions(administrator=True)
    async def setwelcome(self, ctx, *args):
        logger.log_command(ctx, args)
        with suppress(): await ctx.message.delete()

        message = ctx.message.content[len(ctx.command.name) + 2:]
        
        admin_file.set('welcome_message', message)
        await ctx.send('Welcome message set to \'{}\'.'.format(admin_file.get('welcome_message', on_error='')))

    @command(name='clear', help='Clears X messages, where X is the argument. Example: \'!clear 50\'')
    @has_permissions(administrator=True)
    async def clear(self, ctx, *args):
        logger.log_command(ctx, args)
        with suppress(): await ctx.message.delete()
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
        logger.log_command(ctx, args)
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
        
    @command(name='clearreactions', help='Clears all role assignments and all reactions from the message. Template: \'!clearreactions MESSAGE_ID\'.')
    @has_permissions(administrator=True)
    async def clear_reactions(self, ctx, *args):
        await ctx.message.delete()
        logger.log_command(ctx, args)

        message_id, *_ = args

        try: message = await ctx.channel.fetch_message(message_id)
        except discord.NotFound: 
            await ctx.send('Message with id \'{}\' not found in this channel. Please use \'!help {}\' for help on how to use this command.'.format(message_id, ctx.command.name))
            return

        reactions = admin_file.get('reactions', on_error={})

        channel_id = str(ctx.channel.id)
        if not channel_id in reactions:
            await ctx.send('This channel has no reaction assignments.')
            return

        if not message_id in reactions[channel_id]:
            await ctx.send('This message has no reaction assignments.')
            return

        await message.clear_reactions()
        del reactions[channel_id][message_id]
        if len(reactions[channel_id]) is 0:
            del reactions[channel_id]
        admin_file.set('reactions', reactions)

    @command(name='reactionassignment', help='Assigns a specific role to a user depending on the reaction. Template: \'!reactionassignment MESSAGE_ID EMOJI ROLE\'.')
    @has_permissions(administrator=True)
    async def reaction_message(self, ctx, *args):
        await ctx.message.delete()
        logger.log_command(ctx, args)

        if len(args) < 3:
            await ctx.send('Too few arguments. Please use \'!help {}\' for help on how to use this command.'.format(ctx.command.name))
            return

        message_id, emoji, *args = args
        rolename = ' '.join(args)

        try: message = await ctx.channel.fetch_message(message_id)
        except discord.NotFound: 
            await ctx.send('Message with id \'{}\' not found in this channel. Please use \'!help {}\' for help on how to use this command.'.format(message_id, ctx.command.name))
            return

        try: await message.add_reaction(emoji)
        except discord.HTTPException:
            await ctx.send('Emoji \'{}\' is not valid. Please use \'!help {}\' for help on how to use this command.'.format(emoji, ctx.command.name))
            return

        roles = ctx.guild.roles
        role = get_role(rolename, roles)

        if role is None:
            await ctx.send('Role \'{}\' not found on this server. Please use \'!help {}\' for help on how to use this command.'.format(rolename, ctx.command.name))
            return

        reactions = admin_file.get('reactions', on_error={})

        channel_id = str(ctx.channel.id)
        if not channel_id in reactions:
            reactions[channel_id] = {}

        if not message_id in reactions[channel_id]:
            reactions[channel_id][message_id] = []

        reaction_list = reactions[channel_id][message_id]
        reaction_list.append({
            'reaction': emoji,
            'role': rolename
        })

        admin_file.set('reactions', reactions)

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if (payload.user_id == self.bot.user.id): return
        guild = self.bot.get_guild(payload.guild_id)

        await reaction_change(payload, guild, True)

    @Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if (payload.user_id == self.bot.user.id): return
        guild = self.bot.get_guild(payload.guild_id)

        await reaction_change(payload, guild, False)
    
    @Cog.listener()
    async def on_member_update(self, before, after):
        if after.id == defs.get_tempia(self.bot).id and after.nick != 'Tempia':
            await after.edit(nick=None)
        
        #if after.id == 652701117188145162 and after.nick != 'Poopooga':
            #await after.edit(nick='Poopooga')