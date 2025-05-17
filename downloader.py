import os
from pytube import YouTube
from utils import format_progress

def get_streams(url):
    yt = YouTube(url)
    streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
    buttons = []
    stream_map = {}
    for stream in streams:
        label = f"{stream.resolution} ({round(stream.filesize / 1024 / 1024, 2)} MB)"
        buttons.append([{'text': label, 'callback_data': str(stream.itag)}])
        stream_map[str(stream.itag)] = stream
    return buttons, stream_map

def download_video(url, itag):
    yt = YouTube(url)
    stream = yt.streams.get_by_itag(itag)
    file_path = "video.mp4"
    total = stream.filesize
    downloaded = 0

    def on_progress(stream, chunk, bytes_remaining):
        nonlocal downloaded
        downloaded = total - bytes_remaining

    yt.register_on_progress_callback(on_progress)
    stream.download(filename=file_path)

    yield format_progress(downloaded, total)
    yield "Download complete. Sending file..."