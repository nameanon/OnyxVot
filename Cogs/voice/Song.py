import os
import spotipy
import json
import youtube_dl
from discord.ext import commands


class Song:

    def __init__(self, link, dl_path):
        self.link = link
        self.path = ""
        self.dir_location = dl_path
        self.thumbnail = ""
        self.title = ""

        with open('TOKEN.json') as json_file:
            data = json.load(json_file)
            self.spot_client_id = f'{data["spotify"]["client_id"]}'
            self.spot_client_secret = f'{data["spotify"]["client_secret"]}'

        if "https://open.spotify.com/" in self.link:
            if "track" in self.link:
                self.download_from_spotify()

            else:
                raise commands.BadArgument("Only individual track links are supported")

        elif "https://www.youtube.com" in link or "https://youtu.be/" in link:
            self.download_from_ydl()

        else:
            self.link = f"ytsearch:{self.link}"
            self.download_from_ydl()

    def download_from_spotify(self):
        sp = spotipy.Spotify(auth_manager=spotipy.SpotifyClientCredentials(client_id=self.spot_client_id,
                                                                           client_secret=self.spot_client_secret))

        try:
            song = sp.track(self.link)
            self.link = f'ytsearch:{song["artists"][0]["name"]} {song["name"]}'
            self.download_from_ydl()
            self.link = song["external_urls"]["spotify"]
            self.thumbnail = song["album"]["images"][0]["url"]


        except Exception as e:
            raise commands.CommandError(f"{e}")

    def download_from_ydl(self):
        format_out_string = os.path.join(self.dir_location, "%(title)s.%(ext)s")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{format_out_string}',  # Output path
            'noplaylist': 'true',
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:

            info_dict = ydl.extract_info(self.link, download=True)
            try:
                assert info_dict["_type"]
                info_dict = info_dict["entries"][0]

            except KeyError:
                pass

            self.path = ydl.prepare_filename(info_dict)
            self.title = info_dict.get("title", None)
            self.thumbnail = info_dict.get("thumbnail", None)
            self.link = info_dict.get("webpage_url", None)

    def __str__(self):
        return str({
            "dir_location": self.dir_location,
            "link": self.link,
            "path": self.path,
            "thumbnail": self.thumbnail,
            "title": self.title
        })
