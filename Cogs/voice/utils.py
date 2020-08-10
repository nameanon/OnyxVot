from discord.utils import get
from discord.ext import commands
import youtube_dl
import os
import discord
from pytube import YouTube

#
# queue_path = os.path.dirname(__file__) + "\queue" + "\\"
# song_path = queue_path
# song_num = 1
#
# url = "https://www.youtube.com/watch?v=kzeeV_Dl9gw"


def download_song_ydl(url, dl_path, queue_num, queue):
    format_out_string = os.path.join(dl_path, "%(title)s.%(ext)s")
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f'{format_out_string}'  # Output path
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio...")
        ydl.download([url])
        info_dict = ydl.extract_info(url, download=False)
        print('-------------------')
        audio_path = ydl.prepare_filename(info_dict)
        audio_path = audio_path[:len(audio_path) - 5] + ".mp3"

    queue[queue_num] = audio_path


def download_song_pytube(url, dl_path, queue_num, queue):
    try:
        yt = YouTube(url)
        yt.streams.filter(only_audio=True).first()
        dl_path = yt.streams.first().download(output_path=dl_path)
        queue[queue_num] = dl_path

    except KeyError as e:
        raise discord.ext.commands.BadArgument("This track produce a Key error, try another video")

def download_song_ydl_no_pp(url, dl_path, queue_num, queue):
    format_out_string = os.path.join(dl_path, "%(title)s.%(ext)s")
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{format_out_string}'  # Output path
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio...")
        ydl.download([url])
        info_dict = ydl.extract_info(url, download=False)
        print('-------------------')
        audio_path = ydl.prepare_filename(info_dict)


    queue[queue_num] = audio_path

