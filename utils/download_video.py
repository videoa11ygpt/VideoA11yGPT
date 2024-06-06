import json
from pytube import YouTube
import threading
import http.client
http.client.HTTPConnection._http_vsn = 10
http.client.HTTPConnection._http_vsn_str = 'HTTP/1.0'
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

def download(item):
    try:
        link = f"https://www.youtube.com/watch?v={item}"
        yt = YouTube(link, use_oauth=True, allow_oauth_cache=True)
    except Exception as e:
        print(f"[{item}] Error1:{e}")

    try:
	# Modify the path in ".download(f'./'" to your path.
        yt.streams.filter(progressive=True, file_extension='mp4', ).order_by('resolution')[-1].download(f'./',
                                                                                                        filename=f"{item}.mp4")
    except Exception as e:
        print(f"[{item}] Error2:{e}")

# Add video ids to the 'items' before you run the code.
items = []

with ThreadPoolExecutor(max_workers=1) as executer:
    results = executer.map(download, items)