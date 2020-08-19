from discord.ext import commands
from .Song import Song

class Queue:

    def __init__(self, path: str):

        self.queue = {}
        self.path = path
        self.song_num = 0
        self.loop = False

    def add_track(self, track: Song):
        if len(self.queue) == 0:
            self.queue[1] = track

        else:
            self.queue[max(self.queue, key=int) + 1] = track

    def rm_track(self, track_num: int):

        del self.queue[int(track_num)]
        new_queue = {}
        num_count = 0
        for k, s in self.queue.items():
            num_count += 1
            new_queue[num_count] = s

        self.queue = new_queue

    def clear(self):
        self.queue.clear()

    def get_song_to_play(self):

        try:
            self.song_num += 1

            if self.loop and (self.song_num == len(self.queue) + 1 or len(self.queue) == 1):
                self.song_num = 1

            elif self.loop is False and self.song_num == len(self.queue) + 1:
                return

        except Exception as e:
            raise commands.BadArgument(f"{e}")

        return self.queue[self.song_num]

    def get_playing(self):
        return self.queue[self.song_num]

    def get_song(self, num: int):
        return self.queue[num]
