from discord.utils import get
from discord.ext import commands
import youtube_dl
import os
import discord


class VoiceCog(commands.Cog, name="voice"):

    def __init__(self, bot):
        self.bot = bot
        self.song_path = os.path.join(os.path.dirname(__file__), "song.mp3")

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
    async def play(self, ctx, url: str):
        song_there = os.path.isfile(self.song_path)

        try:
            if song_there:
                os.remove(self.song_path)
                print("Removed")

        except PermissionError:

            print("Trying to remove song file, but it's being played")
            await ctx.send("Error, Music Playing")
            return

        await ctx.send("Getting audio...")

        voice = get(self.bot.voice_clients, guild=ctx.guild)

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': f'{self.song_path}'
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            print("Downloading audio...")
            ydl.download([url])

        voice.play(discord.FFmpegPCMAudio(self.song_path), after=lambda e: print("song has finished playing"))
        voice.source = discord.PCMVolumeTransformer(voice.source)
        voice.source.volume = 0.07

        await ctx.send(f"Playing {url}")





def setup(bot):
    bot.add_cog(VoiceCog(bot))
    print("VoiceCog has been loaded")
