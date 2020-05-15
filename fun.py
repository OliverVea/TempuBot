import discord
import os

import json

from random import choice

import defs

from discord.ext.commands import Cog, command, has_any_role

from pattern.text import conjugate, pluralize
try: conjugate('do')
except: pass

try: pluralize('i')
except: pass

class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = None

    @command()
    @has_any_role('Officer', 'Admin')
    async def join(self, ctx):
        await ctx.message.delete()

        user = ctx.message.author
        channel = user.voice.channel

        if channel != None:
            if self.client == None or not self.client.is_connected(): 
                self.client = await channel.connect()
            else:
                await self.client.move_to(channel)

    @command()
    @has_any_role('Officer', 'Admin')
    async def leave(self, ctx):
        await ctx.message.delete()

        if self.client.is_connected():
            await self.client.disconnect()

    @command()
    @has_any_role('Officer', 'Admin')
    async def play(self, ctx, *args):
        await ctx.message.delete()

        clipname = ' '.join(args)
        
        user = ctx.message.author
        channel = user.voice.channel
        
        if self.client.channel != channel:
            return

        for filename in os.listdir(defs.dir_path + '/soundboard_files'):
            if filename[:-4] == clipname:
                self.client.stop()
                audiosource = discord.FFmpegPCMAudio(defs.dir_path + '/soundboard_files/' + filename)
                self.client.play(audiosource)
    
    @command()
    async def classic(self, ctx, *args):
        await ctx.message.delete()

        with open('words.json') as f:
            words = json.load(f)

        verb = choice(words['verbs'])['word']
        verb = conjugate(verb, aspect='progressive')

        noun = choice(words['nouns'])['word']
        if choice([True, False]):
            noun = pluralize(noun)

        s = '{} {} takes more skill than classic.'.format(verb, noun).capitalize()

        await ctx.send(s)
    
    @command()
    async def kys(self, ctx, *args):
        await ctx.message.delete()

        responses = [
            '{} kys'.format(ctx.author.mention),
            'fuck off {}'.format(ctx.author.name.lower()),
            'literally lootbanned.',
            '{} has been removed from the guild by Peanut.'.format(ctx.author.name)]

        await ctx.send(choice(responses))

    @command()
    async def clownfiesta(self, ctx, *args):
        await ctx.message.delete()
        await ctx.send('https://www.twitch.tv/bambibuttqt/clip/ResourcefulBigRabbitNerfRedBlaster')

    @command()
    async def self_destruct(self, ctx, *args):
        await ctx.send('fuck off {}'.format(ctx.author.name.lower()))

        to_leave = self.bot.get_guild(ctx.guild.id)
        await to_leave.leave()

