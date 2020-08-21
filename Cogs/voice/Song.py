import os
from spotdl.command_line.core import Spotdl
import youtube_dl


class Song:

    def __init__(self, link, dl_path):
        self.link = link
        self.path = ""
        self.dir_location = dl_path
        self.thumbnail = ""
        self.title = ""

        if "https://open.spotify.com/" in link:

            raise Exception("Spotify not yet Implemented")

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

        else:
            self.link = f"ytsearch:{self.link}"
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
