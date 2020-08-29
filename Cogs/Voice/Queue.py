import asyncio
import os

from discord.ext import commands
from .Song import Song
import discord
from async_timeout import timeout


class Queue:
    __slots__ = ("queue", "next", "path", "song_num", "loop", "volume",
                 "guild", "bot", "cog", "s_init", "v_channel", "ctx")

    def __init__(self, path: str, s: Song, ctx, vol=0.1):

        self.queue = {}
        # self.queue_async = asyncio.Queue()
        self.next = asyncio.Event()

        self.path = path
        self.song_num = 0
        self.loop = True
        self.volume = vol
        self.guild = ctx.guild
        self.bot = ctx.bot
        self.cog = ctx.cog
        self.v_channel = ctx.author.voice.channel
        self.ctx = ctx

        self.s_init = s

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

            if self.song_num == 0:
                await self.add_track(self.s_init)

            self.song_num += 1

            try:

                if len(self.queue) < self.song_num and self.loop is False:
                    return self.destroy(self.guild)
                elif len(self.queue) < self.song_num:
                    self.song_num = 1

                # Wait for the next song. If we timeout cancel the player and disconnect...
                async with timeout(300):  # 5 minutes...
                    # song = await self.queue_async.get()  # Retrieves song and deletes the song
                    # await self.queue_async.put(song)
                    try:
                        song = self.queue[self.song_num]
                    except KeyError:
                        await self.guild.change_voice_state(channel=None, self_mute=False, self_deaf=True)

                if not isinstance(song.source, discord.PCMVolumeTransformer):
                    # Source was probably a stream (not downloaded)
                    # So we should regather to prevent stream expiration
                    try:
                        print("Regathering")
                        await song.remake_source(True)
                    except Exception as e:
                        self.rm_track(self.song_num)


            except asyncio.TimeoutError:
                return self.destroy(self.guild)

            song.source.volume = self.volume

            if self.guild.voice_client is None and self.loop:
                await self.v_channel.connect()
                await self.guild.change_voice_state(channel=self.v_channel, self_mute=False, self_deaf=True)

            await song.remake_source(True)

            self.guild.voice_client.play(song.source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            # After the song played the flag will set to true

            await self.next.wait()  # Waits until the flag is true

            # Make sure the FFmpeg process is cleaned up.
            song.source.cleanup()
            await song.remake_source(True)

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
        return self.bot.loop.create_task(self.cog.cleanup_disconnect(guild))
