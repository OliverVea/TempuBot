import discord
import os

import defs

from discord.ext.commands import Cog, command, has_any_role

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