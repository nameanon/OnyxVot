import os
import shutil

import discord
import youtube_dl
from discord.ext import commands
from discord.utils import get

from .Song import Song
from .utils import download_song_ydl, download_song_ydl_no_pp
from .._menus_for_list import menus, QueueListSource


class VoiceCog(commands.Cog, name="voice"):

    def __init__(self, bot):
        self.bot = bot
        self.song_path = os.path.join(os.path.dirname(__file__), "song.mp3")
        self.queue = {}
        self.loop = False
        self.embed_colour = 1741991
        self.song_num = 1

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
    async def skip(self, ctx, tracks_to_skip=None):
        """
        Skip the playing track or n number of tracks to skip
        """
        voice = get(self.bot.voice_clients, guild=ctx.guild)

        if tracks_to_skip:
            self.song_num += int(tracks_to_skip)

        if voice and voice.is_playing():
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
            self.song_num = song_num

            if self.loop and song_num == len(self.queue) + 1:
                song_num = 1
                self.song_num = 1

            voice.play(discord.FFmpegPCMAudio(self.queue[song_num].path),
                       after=lambda e: self.check_queue(song_num))
            voice.source = discord.PCMVolumeTransformer(voice.source)
            voice.source.volume = 0.07

        except Exception as e:
            raise commands.BadArgument(f"{e}")

    #
    #
    #
    #
    #

    @commands.command(aliases=["p"])
    async def play(self, ctx, url: str = ""):
        queue_path = os.path.join(os.path.dirname(__file__), "queue")
        queue_is_dir = os.path.isdir(queue_path)

        global voice
        voice = get(self.bot.voice_clients, guild=ctx.guild)

        if not voice:
            v_channel = ctx.author.voice.channel
            voice = await v_channel.connect()

        if voice and voice.is_playing():

            msg = await ctx.send("Attempting to add")

            queue_num = len(self.queue) + 1

            song_in_queue = [song for num, song in self.queue.items() if song.link == url]

            if song_in_queue:
                print("adding repeating")
                self.queue[queue_num] = song_in_queue[0]

            else:
                print("adding new")
                self.queue[queue_num] = Song(link=url, dl_path=queue_path)

            await msg.edit(content=f"Added to queue ✅")

        elif voice and not voice.is_playing() and not voice.is_paused():

            self.song_num = 1

            msg = await ctx.send("Attempting to play...")
            self.queue.clear()

            if queue_is_dir:
                await msg.edit(content=f"Queue init...")
                shutil.rmtree(queue_path)
                os.mkdir(queue_path)
                await msg.edit(content="Downloading song...")

            queue_num = 1
            self.queue[queue_num] = Song(link=url, dl_path=queue_path)
            await msg.edit(content="Song downloaded...")

            if not voice or not voice.is_connected():
                v_channel = ctx.author.voice.channel
                voice = await v_channel.connect()

            voice.play(discord.FFmpegPCMAudio(self.queue[self.song_num].path),
                       after=lambda e: self.check_queue(self.song_num))
            voice.source = discord.PCMVolumeTransformer(voice.source)
            voice.source.volume = 0.07

            await msg.edit(content="Playing Track ✅")

    #
    #
    #
    #
    #

    @commands.command(aliases=["q"])
    async def queue(self, ctx):
        queue_ls = []
        SongLinks = [s.link for k, s in self.queue.items()]

        for url in SongLinks:
            with youtube_dl.YoutubeDL() as ydl:
                info_dict = ydl.extract_info(url, download=False)
                title = info_dict.get("title", None)

            queue_ls.append(title)

        source = QueueListSource(queue_ls, self.embed_colour, self.loop)

        menu = menus.MenuPages(source, clear_reactions_after=True)
        await menu.start(ctx)

    #
    #
    #
    #
    #

    @commands.command()
    @commands.is_owner()
    async def queue_ls(self, ctx):

        queue_ls = [self.queue[a] for a in range(1, len(self.queue) + 1)]

        await ctx.send(queue_ls)

    #
    #
    #
    #
    #

    @commands.command()
    async def loop(self, ctx):

        if not self.loop:
            self.loop = True
            await ctx.send(f"Looping through the queue")

        else:
            self.loop = False
            await ctx.send(f"No longer looping through the queue")

    #
    #
    #
    #
    #

    @commands.command(aliases=["np"])
    async def now_playing(self, ctx):

        e = discord.Embed(title="Now playing...",
                          colour=self.embed_colour)

        with youtube_dl.YoutubeDL() as ydl:
            info_dict = ydl.extract_info(self.queue[self.song_num].link, download=False)
            title = info_dict.get("title", None)
            thumbnail = info_dict.get("thumbnail", None)
            e.set_image(url=thumbnail)

        e.add_field(name=f"{self.song_num}. {self.queue[self.song_num].link}",
                    value=f"{title}")

        await ctx.send(embed=e)

    #
    #
    #
    #
    #

    @commands.command(aliases=["prune", "rm_song"])
    async def prune_song(self, ctx, song_num):

        try:
            await ctx.send(embed=discord.Embed(title=f"Removed the song number {song_num} from the queue",
                                               description=self.queue[int(song_num)].link,
                                               colour=self.embed_colour))

            del self.queue[int(song_num)]
            new_queue = {}
            num_count = 0
            for k, s in self.queue.items():
                num_count += 1
                new_queue[num_count] = s

            self.queue = new_queue

        except KeyError:
            await ctx.send(embed=discord.Embed(title="That song is not on the queue",
                                               colour=self.embed_colour))

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

    async def cog_check(self, ctx):
        voice_c = get(self.bot.voice_clients, guild=ctx.guild)
        if voice_c and ctx.channel.type != "private":
            if ctx.author.voice.channel == voice_c.channel and voice_c:
                return True
            else:
                return False
        else:
            return True



def setup(bot):
    bot.add_cog(VoiceCog(bot))
    print("VoiceCog has been loaded")
