import youtube_dl
import os
from spotdl.command_line.core import Spotdl


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


def download_song_ydl_no_pp(url, dl_path, queue_num, queue, links):
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
    links[queue_num] = url


def download_spotify(url, dl_path, queue_num, queue, links):
    files_before = os.listdir(dl_path)

    args = {
        "song": [url],
        "overwrite": "force",
        "OUTPUT_FILE": dl_path
    }

    with Spotdl(args) as spdl:
        spdl.match_arguments()

    files_after = os.listdir(dl_path)

    audio_path = list(set(files_before) - set(files_after))

