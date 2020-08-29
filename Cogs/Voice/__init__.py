import os
import shutil
import discord

from discord.ext import commands, tasks
from discord.utils import get

from .Song import Song
from .Queue import Queue
from .._menus_for_list import menus, QueueListSource


class VoiceCog(commands.Cog, name="Voice"):

    def __init__(self, bot):
        self.bot = bot
        self.embed_colour = 1741991
        self.server_queues = {}
        # 15641651954 : Queue(queue: - - - -,
        #                     path: - - - - )
        self.prune_queues.start()

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

    @tasks.loop(hours=3)
    async def prune_queues(self):
        queue_dir = os.path.join(os.path.dirname(__file__), "queue")
        print("\nPrune_queues task started")

        for filename in os.listdir(queue_dir):
            print(f"\n{filename}")
            if filename not in self.server_queues.keys():
                print(f"\n{filename} not active, will delete")
                shutil.rmtree(os.path.join(queue_dir, filename))

    #
    #
    #
    #
    #

    @commands.command()
    async def join(self, ctx):
        v_channel = ctx.author.voice.channel
        voice = get(self.bot.voice_clients, guild=ctx.guild)

        if voice and voice.is_connected() and len(v_channel.members):
            raise Exception("Already in a Voice channel")

        else:
            await ctx.guild.change_voice_state(channel=v_channel, self_mute=False, self_deaf=True)

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
            self.server_queues[ctx.guild.id].leave = True
            await self.cleanup_disconnect(ctx.guild)
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

    @commands.command(aliases=["unpause"])
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
        voice = ctx.voice_client
        try:
            queue_obj = self.server_queues[ctx.guild.id]
        except KeyError:
            raise commands.CommandError("The bot does not have a queue to skip with in this server")

        if voice and voice.is_playing():
            if tracks_to_skip:
                queue_obj.song_num += int(tracks_to_skip)

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

    @commands.command(aliases=["p"])
    async def play(self, ctx, *, url: str = ""):
        guild_id = ctx.guild.id
        queue_fld_path = os.path.join(os.path.dirname(__file__), "queue", str(guild_id))
        queue_is_dir = os.path.isdir(queue_fld_path)

        e = discord.Embed(title="",
                          description="",
                          colour=self.embed_colour)

        voice = ctx.guild.voice_client

        if not voice:
            v_channel = ctx.author.voice.channel
            voice = await v_channel.connect()
            await ctx.guild.change_voice_state(channel=v_channel, self_mute=False, self_deaf=True)

        if voice and voice.is_playing():  # If it's connected and playing

            queue_obj = self.server_queues[guild_id]
            e.title = "Attempting to add"
            msg = await ctx.send(embed=e)
            song_in_queue = [song for num, song in queue_obj.queue.items() if song.link == url]

            if song_in_queue:
                s = song_in_queue[0]
                await queue_obj.add_track(s)

            else:
                s = Song(link=url, dl_path=queue_fld_path)
                await queue_obj.add_track(s)

            e.title = f"Added to queue by {ctx.author.display_name} ✅"
            e.description = f"[{s.title}]({s.link})"
            e.set_thumbnail(url=s.thumbnail)
            e.set_footer(text=f"Song Number: {len(queue_obj.queue)}")

            await msg.edit(embed=e)

        elif voice and not voice.is_playing() and not voice.is_paused():
            # If not connected and not playing

            e.title = "Attempting to play..."
            msg = await ctx.send(embed=e)

            if queue_is_dir:
                e.title = "Queue initialization"
                await msg.edit(embed=e)
                print(f"\nRemoved: {queue_fld_path}\n")
                shutil.rmtree(queue_fld_path)
                os.mkdir(queue_fld_path)
                e.title = "Getting audio track..."
                await msg.edit(embed=e)

            s = Song(link=url, dl_path=queue_fld_path)
            self.server_queues[guild_id] = Queue(path=queue_fld_path, ctx=ctx, s=s)
            queue_obj = self.server_queues[guild_id]

            e.title = "Audio obtained"
            await msg.edit(embed=e)

            if not voice or not voice.is_connected():
                v_channel = ctx.author.voice.channel
                await v_channel.connect()
                await ctx.guild.change_voice_state(channel=v_channel, self_mute=False, self_deaf=True)

            e.title = f"Playing Audio and added to queue by {ctx.author.display_name} ✅"
            e.description = f"[{s.title}]({s.link})"
            e.set_thumbnail(url=s.thumbnail)
            e.set_footer(text=f"Song Number: {1}")

            await msg.edit(embed=e)

    #
    #
    #
    #
    #

    @commands.command(aliases=["q"])
    async def queue(self, ctx):
        try:
            queue_obj = self.server_queues[ctx.guild.id]
        except KeyError:
            raise commands.CommandError("The bot does not have a queue on this server to show")

        queue_ls = [f"[{s.title}]({s.link})" for k, s in queue_obj.queue.items()]

        source = QueueListSource(queue_ls, self.embed_colour, queue_obj.loop, queue_obj.song_num)

        menu = menus.MenuPages(source, clear_reactions_after=True)
        await menu.start(ctx)

    #
    #
    #
    #
    #

    @commands.command()
    async def loop(self, ctx):
        try:
            queue_obj = self.server_queues[ctx.guild.id]
        except KeyError:
            raise commands.CommandError("The bot does not have a queue on this server to loop over")

        if not queue_obj.loop:
            queue_obj.loop = True
            await ctx.send(f"Looping through the queue")

        else:
            queue_obj.loop = False
            await ctx.send(f"No longer looping through the queue")

    #
    #
    #
    #
    #

    @commands.command(aliases=["np"])
    async def now_playing(self, ctx):
        try:
            queue_obj = self.server_queues[ctx.guild.id]

        except KeyError:
            raise commands.CommandError("The bot does not have a queue on this server")

        song_obj = queue_obj.get_playing()

        e = discord.Embed(title="Now playing...",
                          colour=self.embed_colour)

        e.set_image(url=song_obj.thumbnail)

        e.add_field(name=f"{queue_obj.song_num}. {song_obj.link}",
                    value=f"{song_obj.title}")

        await ctx.send(embed=e)

    #
    #
    #
    #
    #

    @commands.command(aliases=["prune", "rm_song"])
    async def prune_song(self, ctx, song_num: int):

        queue_obj = self.server_queues[ctx.guild.id]

        try:

            e = discord.Embed(title=f"Removed the song number {song_num} from the queue:",
                              description=f"[{queue_obj.queue[int(song_num)].title}]({queue_obj.queue[int(song_num)].link})",
                              colour=self.embed_colour)

            e.set_image(url=queue_obj.queue[int(song_num)].thumbnail)

            msg = await ctx.send(embed=e)

            queue_obj.rm_track(int(song_num))
            if queue_obj.song_num == song_num:
                await self.cleanup_disconnect(ctx.guild)
                e.set_footer(text=f"No more audio on queue, Disconnecting..")
                await msg.edit(embed=e)



        except KeyError:
            await ctx.send(embed=discord.Embed(title="That song is not on the queue",
                                               colour=self.embed_colour))

    #
    #
    #
    #
    #

    @commands.command()
    async def vol(self, ctx, new_vol: int):
        queue_obj = self.server_queues[ctx.guild.id]

        if new_vol not in [r for r in range(1, 41)]:
            raise commands.BadArgument("Please select a volume in between 1 and 40\nDefault Volume is 7")

        new_vol = new_vol / 100

        e = discord.Embed(title="Volume changed:",
                          description=f"From `{queue_obj.volume / 20 * 10000}%` ===> `{new_vol / 20 * 10000}%`",
                          colour=self.embed_colour)

        e.set_footer(text="Changes to volume will take effect on the next track")

        await ctx.send(embed=e)

        queue_obj.volume = new_vol

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

        if ctx.author.voice is None:  # User is not in Voice channel
            raise commands.CommandError("You need to be in a Voice channel to run this command")

        if voice_c and ctx.channel.type != "private":  # Not in a DM

            if len(voice_c.channel.members) > 1:  # More than 2 users in Voice

                if ctx.author.voice.channel == voice_c.channel:
                    # Bot and User are in same Voice
                    return True

                else:
                    raise commands.CommandError("You need to be in the same Voice channel as the bot to run this "
                                                "command.")
                    # return False

            else:
                # Disconnects the bot if it's alone in a channel
                await self.cleanup_disconnect(ctx.guild)
                return True

        elif voice_c is None:
            return True

        else:
            raise commands.CommandError("Command needs to be run in a server")

    #
    #
    #
    #
    #

    async def cleanup_disconnect(self, guild):
        self.server_queues[guild.id].leave = True
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.server_queues[guild.id]
        except KeyError:
            pass


def setup(bot):
    bot.add_cog(VoiceCog(bot))
    print("VoiceCog has been loaded")
