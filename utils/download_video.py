import json
from pytube import YouTube
import threading
import http.client
http.client.HTTPConnection._http_vsn = 10
http.client.HTTPConnection._http_vsn_str = 'HTTP/1.0'
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import ssl
import argparse
ssl._create_default_https_context = ssl._create_unverified_context

def download(item, download_path):
    try:
        link = f"https://www.youtube.com/watch?v={item}"
        yt = YouTube(link, use_oauth=True, allow_oauth_cache=True)
    except Exception as e:
        print(f"[{item}] Error1:{e}")
        return

    try:
        # Ensures the download path exists
        Path(download_path).mkdir(parents=True, exist_ok=True)
        # Downloads the highest resolution progressive stream available
        yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution')[-1].download(download_path,
                                                                                                     filename=f"{item}.mp4")
    except Exception as e:
        print(f"[{item}] Error2:{e}")

def main(max_workers, target_folder, video_ids_file):
    # Read the video IDs from a file
    with open(video_ids_file, 'r') as file:
        items = file.read().splitlines()

    # Use ThreadPoolExecutor to parallelize downloads
    with ThreadPool_then runoolExecutor(max_workers=max_workers) as executor:
        executor.map(lambda item: download(item, target_folder), items)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download YouTube videos")
    parser.add_argument("--max_workers", type=int, help="Maximum number of download threads")
    parser.add_argument("--target_folder", type=str, help="Folder to download the videos into")
    parser.add_argument("--video_ids_file", type=str, help="File containing YouTube video IDs, one per line")

    args = parser.parse_args()
    main(args.max_workers, args.target_folder, args.video_ids_file)
