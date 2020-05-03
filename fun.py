import discord
import os

import defs

from discord.ext.commands import Cog, command, has_any_role

class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command()
    @has_any_role('Officer', 'Admin')
    async def join(self, ctx):
        await ctx.message.delete()

        user = ctx.message.author
        channel = user.voice.channel

        if channel != None:
            if self.bot == None or not self.bot.is_connected(): 
                self.bot = await channel.connect()
            else:
                await self.bot.move_to(channel)

    @command()
    @has_any_role('Officer', 'Admin')
    async def leave(self, ctx):
        await ctx.message.delete()

        if self.bot.is_connected():
            await self.bot.disconnect()

    @command()
    @has_any_role('Officer', 'Admin')
    async def play(self, ctx, *args):
        await ctx.message.delete()

        clipname = ' '.join(args)
        
        user = ctx.message.author
        channel = user.voice.channel
        
        if self.bot.channel != channel:
            return

        for filename in os.listdir(defs.dir_path + '/soundboard_files'):
            if filename[:-4] == clipname:
                self.bot.stop()
                audiosource = discord.FFmpegPCMAudio(defs.dir_path + '/soundboard_files/' + filename)
                self.bot.play(audiosource)