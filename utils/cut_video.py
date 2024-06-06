import argparse
import json
import os
import shutil
from moviepy.editor import VideoFileClip

def process_videos(video_ids, original_video_path, new_video_path):
    for i, item in enumerate(video_ids):
        video_id = item
        video = video_id.rsplit("_", 2)[0]
        start_time = float(video_id.rsplit("_", 2)[1])
        end_time = float(video_id.rsplit("_", 2)[2])
        temp_path = os.path.join(new_video_path, f'temp_{video.replace("-", "_")}.mp4')

        source_video_path = os.path.join(original_video_path, f'{video}.mp4')
        target_video_path = os.path.join(new_video_path, f'{video}.mp4')

        # Skip processing if source video does not exist or target already exists
        if not os.path.exists(source_video_path) or os.path.exists(target_video_path):
            continue

        # Load and cut the video file
        clip = VideoFileClip(source_video_path)
        end_time = min(end_time, clip.duration)
        subclip = clip.subclip(start_time, end_time)

        # Ensure target directory exists
        os.makedirs(os.path.dirname(target_video_path), exist_ok=True)

        # Save the subclip with original audio
        subclip.write_videofile(temp_path, codec="libx264", audio_codec="aac")

        # Move from temp path to final path
        shutil.move(temp_path, target_video_path)
        print(f'Processed {i}: {video} from {start_time} to {end_time}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process video clips from a JSON list of video IDs.')
    parser.add_argument('--json_file', type=str, required=True, help='Path to JSON file containing video IDs')
    parser.add_argument('--original_path', type=str, required=True, help='Directory path for original videos')
    parser.add_argument('--new_path', type=str, required=True, help='Directory path for processed videos')

    args = parser.parse_args()

    # Load video IDs from JSON file
    with open(args.json_file, 'r') as file:
        video_ids = json.load(file).keys()

    # Process videos
    process_videos(video_ids, args.original_path, args.new_path)
