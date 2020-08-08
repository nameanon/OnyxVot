from discord.utils import get
from discord.ext import commands
import discord
import youtube_dl
import os
import discord
from .utils import download_song
import shutil
from .._menus_for_list import menus, QueueListSource


class VoiceCog(commands.Cog, name="voice"):

    def __init__(self, bot):
        self.bot = bot
        self.song_path = os.path.join(os.path.dirname(__file__), "song.mp3")
        self.queue = {}
        self.loop = False
        self.embed_colour = 1741991

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

    @commands.command()
    async def pause(self, ctx):
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
    async def resume(self, ctx):
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
    async def skip(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)

        if voice and voice.is_playing():
            print("Track skipped")
            voice.stop()
            await ctx.send(f"Track skipped")

        else:
            print("Audio not playing failed skip")
            await ctx.send("Audio not playing failed skip")

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

    def check_queue(self, song_num):
        try:
            song_num += 1
            if self.loop and song_num == len(self.queue) + 1:
                song_num = 1

            voice.play(discord.FFmpegPCMAudio(self.queue[song_num]), after=lambda e: self.check_queue(song_num))
            voice.source = discord.PCMVolumeTransformer(voice.source)
            voice.source.volume = 0.07

        except Exception as e:
            print(e)

    @commands.command()
    async def p(self, ctx, url: str = ""):
        queue_path = os.path.dirname(__file__) + "\\queue" + "\\"
        queue_is_dir = os.path.isdir(queue_path)

        global voice
        voice = get(self.bot.voice_clients, guild=ctx.guild)

        if not voice:
            v_channel = ctx.author.voice.channel
            voice = await v_channel.connect()

        if voice and voice.is_playing():
            await ctx.send("Attempting to add")
            try:
                queue_num = len(self.queue) + 1
                print(len(self.queue))
                print(queue_num)
                download_song(url, queue_path, queue_num, self.queue)
                print("Song downloaded and added to queue")
                print(self.queue)
                await ctx.send(f"Added to queue")

            except Exception as e:
                await ctx.send(e)

            return

        elif voice and not voice.is_playing() and not voice.is_paused():

            msg = await ctx.send("Attempting to play")

            self.queue.clear()

            if queue_is_dir:
                shutil.rmtree(queue_path)
                print("Removed old queue")
                os.mkdir(queue_path)
                print("Made new queue")
                print(self.queue)

            if not voice:
                v_channel = ctx.author.voice.channel
                voice = await v_channel.connect()

            queue_num = 1
            download_song(url, queue_path, queue_num, self.queue)
            await msg.edit(content="Song downloaded")
            print("Song downloaded")
            print(self.queue)


            voice.play(discord.FFmpegPCMAudio(self.queue[1]), after=lambda e: self.check_queue(1))
            voice.source = discord.PCMVolumeTransformer(voice.source)
            voice.source.volume = 0.07

            await msg.edit(content="Playing Track")
            return

    @commands.command()
    async def queue(self, ctx):

        queue_ls = [self.queue[a] for a in range(1, len(self.queue) + 1)]

        source = QueueListSource(queue_ls, self.embed_colour)

        menu = menus.MenuPages(source, clear_reactions_after=True)
        await menu.start(ctx)

    @commands.command()
    async def queue_ls(self, ctx):

        queue_ls = [self.queue[a] for a in range(1, len(self.queue) + 1)]

        await ctx.send(queue_ls)


    @commands.command()
    async def loop(self, ctx):

        if self.loop == False:
            self.loop = True
            await ctx.send(f"Looping through the queue")

        else:
            self.loop = False
            await ctx.send(f"Stopped Looping through the queue")

    async def cog_check(self, ctx):
        voice_c = get(self.bot.voice_clients, guild=ctx.guild)
        if voice_c and ctx.channel.type != "private":
            if ctx.author.voice.channel == voice.channel and voice_c:
                return True
            else:
                return False
        else:
            return True


def setup(bot):
    bot.add_cog(VoiceCog(bot))
    print("VoiceCog has been loaded")
