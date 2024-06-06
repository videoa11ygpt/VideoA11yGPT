from moviepy.editor import VideoFileClip
import shutil
import json
import os

# Load the dataset
# These examples show the format of the input. The format is the same as the metadata field "Video_ID" in VALOR32K-BLV dataset.
examples = ["njoCaIgSf7Q_000124_000134","NqE4FpM7Ypk_000251_000261","1tZdoKrBtM0_000081_000091","p-OVfu6lcCk_000312_000322","5qMcueWULmw_000125_000135","xCNaxH4PmeE_000041_000051","2EzgIJXmZVs_000001_000011","_WVQEPWXS0A_000238_000248","id4lBOJLHkc_000217_000227","SNY312f5LSU_000076_000086","rig5bcr8ukk_000029_000039","Xh-2PXRC6X8_000060_000070"]

video_json = []
i = 0

for item in examples:
    i += 1
    video_id = item
    video = video_id.rsplit("_", 2)[0]
    start_time = float(video_id.rsplit("_", 2)[1])
    end_time = float(video_id.rsplit("_", 2)[2])
    # Define paths, modify it as you need.
    original_video_path = f'./{video}.mp4'
    new_video_path = f'./videos/{video}.mp4'
    temp_path = f'./videos/temp_{video.replace("-", "_")}.mp4'

    # shutil.move(new_video_path, temp_path)

    # Check if the original video exists and the new video does not
    if not os.path.exists(original_video_path) or os.path.exists(new_video_path):
        continue

    # Load the video file
    clip = VideoFileClip(original_video_path)

    end_time = min(end_time, clip.duration)
    print(i, video, start_time, end_time)
    # Cut the clip to the desired subclip
    subclip = clip.subclip(start_time, end_time)

    # Check if the directory exists before saving, create if it doesn't
    os.makedirs(os.path.dirname(new_video_path), exist_ok=True)

    # Write the subclip to a file with the original audio
    subclip.write_videofile(temp_path, codec="libx264", audio_codec="aac")

    shutil.move(temp_path, new_video_path)