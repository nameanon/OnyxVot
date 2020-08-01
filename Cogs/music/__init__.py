from discord.utils import get
from discord.ext import commands
import youtube_dl
import os


class MusicCog(commands.Cog, name="music"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx):
        global voice
        v_channel = ctx.author.voice.channel

        voice = get(self.bot.voice_clients, guild=ctx.guild)

        if voice and voice.is_connected():
            await voice.move_to(v_channel)

        else:
            voice = await v_channel.connect()

        await voice.disconnect()  # TODO: Fix this maybe

        if voice and voice.is_connected():
            await voice.move_to(v_channel)

        else:
            voice = await v_channel.connect()
            print(f"Bot has connected to {v_channel}")

        await ctx.send(f"Connection Established to {v_channel}")

    @commands.command()
    async def leave(self, ctx):
        v_channel = ctx.author.voice.channel
        voice = get(self.bot.voice_clients, guild=ctx.guild)

        if voice and voice.is_connected():
            await voice.disconnect()
            print(f"Bot disconnected from {v_channel}")
            await ctx.send(f"Connection to {v_channel} terminated")

        else:
            print("Bot was told to leave but wasn't connected")
            await ctx.send(f"No connection present")

    @commands.command()
    async def play(self,ctx, url: str):
        pass




def setup(bot):
    bot.add_cog(MusicCog(bot))
    print("MusicCog has been loaded")
