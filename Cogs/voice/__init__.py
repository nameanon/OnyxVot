from discord.utils import get
from discord.ext import commands
import youtube_dl
import os
import discord


class VoiceCog(commands.Cog, name="voice"):

    def __init__(self, bot):
        self.bot = bot
        self.song_path = os.path.join(os.path.dirname(__file__), "song.mp3")

    #
    #
    #
    #
    #
    #
    #
    #
    #
    #

    @commands.command()
    async def join(self, ctx):
        global voice
        v_channel = ctx.author.voice.channel

        voice = get(self.bot.voice_clients, guild=ctx.guild)

        if voice and voice.is_connected():
            await voice.move_to(v_channel)

        else:
            voice = await v_channel.connect()

        # await voice.disconnect()  # TODO: Fixed probably
        #
        # if voice and voice.is_connected():
        #     await voice.move_to(v_channel)
        #
        # else:
        #     voice = await v_channel.connect()
        #     print(f"Bot has connected to {v_channel}")

        await ctx.send(f"Connection Established to {v_channel}")

    #
    #
    #
    #
    #

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

    #
    #
    #
    #
    #

    @commands.command()
    async def play(self, ctx, url: str):
        song_there = os.path.isfile(self.song_path)

        try:
            if song_there:
                os.remove(self.song_path)
                print("Removed")

        except PermissionError:

            print("Trying to remove song file, but it's being played")
            await ctx.send("Error, Audio Playing")
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
            'outtmpl': f'{self.song_path}'  # Output path
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            print("Downloading audio...")
            ydl.download([url])

        voice.play(discord.FFmpegPCMAudio(self.song_path), after=lambda e: print("song has finished playing"))
        voice.source = discord.PCMVolumeTransformer(voice.source)
        voice.source.volume = 0.07

        await ctx.send(f"Playing {url}")

    #
    #
    #
    #
    #

    @commands.command()
    async def pause(self,ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)

        if voice and voice.is_playing():
            print("Audio paused")
            voice.pause()
            await ctx.send(f"Audio paused...")

        else:
            print("Audio not playing failed pause")
            await ctx.send("Audio not playing failed pause")

    #
    #
    #
    #
    #

    @commands.command()
    async def resume(self,ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)

        if voice and voice.is_paused():
            print("Resumed audio...")
            voice.resume()
            await ctx.send(f"Resumed audio...")

        else:
            print("Audio is not paused")
            await ctx.send("Audio is not paused")

    #
    #
    #
    #
    #

    @commands.command()
    async def stop(self,ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)

        if voice and voice.is_playing():
            print("Audio stopped")
            voice.stop()
            await ctx.send(f"Audio stopped...")

        else:
            print("Audio not playing failed stopped")
            await ctx.send("Audio not playing failed stopped")



def setup(bot):
    bot.add_cog(VoiceCog(bot))
    print("VoiceCog has been loaded")
