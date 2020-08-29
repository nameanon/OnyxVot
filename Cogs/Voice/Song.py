import os
from functools import partial

import spotipy
import json
import youtube_dl
from discord.ext import commands
import asyncio
from discord import FFmpegPCMAudio, PCMVolumeTransformer

ffmpegopts = {
    'before_options': '-nostdin',
    'options': '-vn'
}


class Song:
    __slots__ = ("link", "path", "dir_location", "thumbnail", "title", "source", "func",
                 "spot_client_id", "spot_client_secret", "ydl_opts", "dl_link")

    def __init__(self, link, dl_path):
        self.link = link
        self.path = None
        self.dir_location = dl_path
        self.thumbnail = None
        self.title = None
        self.source = None
        self.func = None
        self.dl_link = None

        self.ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'nocheckcertificate': True,
            #  'restrictfilenames': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0'
        }

        loop = asyncio.get_event_loop()

        if "https://open.spotify.com/" in self.link:
            if "track" in self.link:

                with open('TOKEN.json') as json_file:
                    data = json.load(json_file)
                    self.spot_client_id = f'{data["spotify"]["client_id"]}'
                    self.spot_client_secret = f'{data["spotify"]["client_secret"]}'

                self.func = self.download_from_spotify(loop=loop)

            else:
                raise commands.BadArgument("Only individual track links are supported")

        elif "https://www.youtube.com" in link or "https://youtu.be/" in link:
            self.func = self.download_from_ydl(loop=loop)

        elif "ytsearch:" in self.link:
            self.func = self.download_from_ydl(loop=loop)

        else:
            self.link = f"ytsearch:{self.link}"
            self.func = self.download_from_ydl(loop=loop)

    #
    #
    #
    #
    #

    async def download_song(self):
        loop = asyncio.get_event_loop()
        to_run = self.func
        await loop.create_task(to_run)

    async def download_from_spotify(self, loop):
        sp = spotipy.Spotify(auth_manager=spotipy.SpotifyClientCredentials(client_id=self.spot_client_id,
                                                                           client_secret=self.spot_client_secret))

        try:
            song = sp.track(self.link)
            self.link = f'ytsearch:{song["artists"][0]["name"]} {song["name"]}'

            to_run = self.download_from_ydl(loop)
            await loop.create_task(to_run)

            self.link = song["external_urls"]["spotify"]
            self.thumbnail = song["album"]["images"][0]["url"]

        except Exception as e:
            raise commands.CommandError(f"{e}")

    #
    #
    #
    #
    #

    async def download_from_ydl(self, loop):
        format_out_string = os.path.join(self.dir_location, "%(title)s.%(ext)s")
        self.ydl_opts['outtmpl'] = f'{format_out_string}'

        with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:

            info_dict = ydl.extract_info(url=self.link, download=False)

            try:
                assert info_dict["_type"]
                info_dict = info_dict["entries"][0]

            except KeyError:
                pass

            self.path = ydl.prepare_filename(info_dict)
            self.title = info_dict.get("title", None)
            self.thumbnail = info_dict.get("thumbnail", None)
            self.link = info_dict.get("webpage_url", None)
            self.dl_link = info_dict.get("webpage_url", None)

            await self.remake_source(True)

    async def remake_source(self, download=False):
        # del self.source

        loop = asyncio.get_event_loop()
        to_run = partial(youtube_dl.YoutubeDL(self.ydl_opts).extract_info, url=self.dl_link, download=download)

        if download:
            data = await loop.run_in_executor(None, to_run)
            self.source = PCMVolumeTransformer(FFmpegPCMAudio(self.path))

        else:
            data = await loop.run_in_executor(None, to_run)
            self.source = PCMVolumeTransformer(FFmpegPCMAudio(data['url']))

            if "https://manifest.googlevideo.com/api/" in data["url"]:
                print("Manifest Error")
                raise Exception("Manifest Error")

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

    def __str__(self):
        return str({
            "dir_location": self.dir_location,
            "link": self.link,
            "path": self.path,
            "thumbnail": self.thumbnail,
            "title": self.title
        })
