from discord.utils import get
from discord.ext import commands
import youtube_dl
import os
import discord
#
# queue_path = os.path.dirname(__file__) + "\queue" + "\\"
# song_path = queue_path
# song_num = 1
#
# url = "https://www.youtube.com/watch?v=kzeeV_Dl9gw"


def download_song(url, dl_path, queue_num, queue):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f'{dl_path}%(title)s.%(ext)s'  # Output path
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio...")
        ydl.download([url])
        info_dict = ydl.extract_info(url, download=False)
        print('-------------------')
        audio_path = ydl.prepare_filename(info_dict)
        audio_path = audio_path[:len(audio_path) - 5] + ".mp3"

    queue[queue_num] = audio_path

