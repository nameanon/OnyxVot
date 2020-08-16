import os
from spotdl.command_line.core import Spotdl
import youtube_dl


class Song:

    def __init__(self, link, dl_path):
        self.link = link
        self.path = ""
        self.dir_location = dl_path

        if "https://open.spotify.com/" in link:

            dir_list_b = os.listdir(self.dir_location)
            print(dir_list_b)
            self.download_from_spotify()
            dir_list_a = os.listdir(self.dir_location)
            print(dir_list_a)
            song = list(set(dir_list_a).symmetric_difference(set(dir_list_b)))[0]
            print(song)
            self.path = os.path.join(self.dir_location, song)

        elif "https://www.youtube.com" in link or "https://youtu.be/" in link:
            self.download_from_ydl()

    def download_from_spotify(self):

        args = {
            "song": [self.link],
            "overwrite": "skip",
            "output_file": f"{self.dir_location}" + "\\{artist} - {track-name}.{output-ext}"
        }

        with Spotdl(args) as spdl:
            spdl.match_arguments()

    def download_from_ydl(self):
        format_out_string = os.path.join(self.dir_location, "%(title)s.%(ext)s")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{format_out_string}'  # Output path
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.link])
            info_dict = ydl.extract_info(self.link, download=False)
            self.path = ydl.prepare_filename(info_dict)

    def __str__(self):
        return str({
            "dir_location": self.dir_location,
            "link": self.link,
            "path": self.path
        })

