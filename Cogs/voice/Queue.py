import asyncio
from discord.ext import commands
from .Song import Song
import discord
from async_timeout import timeout


class Queue:

    def __init__(self, path: str, ctx, vol=0.1):

        self.queue = {}
        self.queue_async = asyncio.Queue()
        self.next = asyncio.Event()

        self.path = path
        self.song_num = 0
        self.loop = False
        self.volume = vol
        self.guild = ctx.guild
        self.bot = ctx.bot
        self.current = None
        self.cog = ctx.cog

        ctx.bot.loop.create_task(self.player_loop())

    #
    #
    #
    #
    #

    async def player_loop(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()  # Sets the flag to false

            try:

                if len(self.queue) > self.song_num and self.loop is False:
                    await asyncio.sleep(3)
                    return self.destroy(self.guild)

                # Wait for the next song. If we timeout cancel the player and disconnect...
                async with timeout(300):  # 5 minutes...
                    self.song_num += 1
                    # song = await self.queue_async.get()  # Retrieves song and deletes the song
                    # await self.queue_async.put(song)
                    song = self.queue[self.song_num]

            except asyncio.TimeoutError:
                return self.destroy(self.guild)

            song.source.volume = self.volume
            self.current = song.source

            self.guild.voice_client.play(song.source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            # After the song played the flag will set to true

            await self.next.wait()  # Waits until the flag is true

            # Make sure the FFmpeg process is cleaned up.
            song.source.cleanup()
            self.current = None

    #
    #
    #
    #
    #

    async def add_track(self, track: Song):

        await track.download_song()

        if len(self.queue) == 0:
            self.queue[1] = track
            # await self.queue_async.put(track)

        else:
            self.queue[max(self.queue, key=int) + 1] = track
            # await self.queue_async.put(track)

    #
    #
    #
    #
    #

    def rm_track(self, track_num: int):

        del self.queue[track_num]
        new_queue = {}
        num_count = 0
        for k, s in self.queue.items():
            num_count += 1
            new_queue[num_count] = s

        self.queue = new_queue

    #
    #
    #
    #
    #

    def clear(self):
        self.queue.clear()

    #
    #
    #
    #
    #

    def get_song_to_play(self):

        try:
            self.song_num += 1

            if self.loop:
                if self.song_num == len(self.queue) + 1 or len(self.queue) == 1:
                    self.song_num = 1

            elif self.loop is False and self.song_num == len(self.queue) + 1:
                return

            return self.queue[self.song_num]

        except Exception as e:
            raise commands.CommandError(f"{e}")

    #
    #
    #
    #
    #

    def get_playing(self):
        return self.queue[self.song_num]

    #
    #
    #
    #
    #

    def get_song(self, num: int):
        return self.queue[num]

    #
    #
    #
    #
    #

    def get_vol(self):
        return self.volume

    def destroy(self, guild):
        """Disconnect and cleanup the player."""
        return self.bot.loop.create_task(self.cog.cleanup(guild))
