import cv2  # We're using OpenCV to read video, to install !pip install opencv-python
import base64
import time
import math
from openai import OpenAI
import os
import operator
import numpy as np
import sys
import json
from scipy.signal import argrelextrema
import argparse

def smooth(x, window_len=13, window='hanning'):
    print(len(x), window_len)
    s = np.r_[2 * x[0] - x[window_len:1:-1],
              x, 2 * x[-1] - x[-1:-window_len:-1]]
    # print(len(s))

    if window == 'flat':  # moving average
        w = np.ones(window_len, 'd')
    else:
        w = getattr(np, window)(window_len)
    y = np.convolve(w / w.sum(), s, mode='same')
    return y[window_len - 1:-window_len + 1]

class Frame:
    def __init__(self, id, diff):
        self.id = id
        self.diff = diff

    def __lt__(self, other):
        if self.id == other.id:
            return self.id < other.id
        return self.id < other.id

    def __gt__(self, other):
        return other.__lt__(self)

    def __eq__(self, other):
        return self.id == other.id and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

def extract_keyframes(video_path, max_frame):
    video = cv2.VideoCapture(video_path)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    curr_frame = None
    prev_frame = None
    frame_diffs = []
    frames = []
    success, frame = video.read()
    i = 0
    while (success):
        luv = cv2.cvtColor(frame, cv2.COLOR_BGR2LUV)
        curr_frame = luv
        if curr_frame is not None and prev_frame is not None:
            # logic here
            diff = cv2.absdiff(curr_frame, prev_frame)
            diff_sum = np.sum(diff)
            diff_sum_mean = diff_sum / (diff.shape[0] * diff.shape[1])
            frame_diffs.append(diff_sum_mean)
            frame = Frame(i, diff_sum_mean)
            frames.append(frame)
        prev_frame = curr_frame
        i = i + 1
        success, frame = video.read()
    video.release()

    # smoothing window size
    if i / 10 > max_frame:
        len_window = i // max_frame + 1
    elif i / 10 < 5:
        len_window = i // 5
    else:
        len_window = 10

    # compute keyframe
    keyframe_id_set = set()
    diff_array = np.array(frame_diffs)
    # print(diff_array)
    sm_diff_array = smooth(diff_array, len_window)
    # print(sm_diff_array)
    frame_indexes = np.asarray(argrelextrema(sm_diff_array, np.greater))[0]
    for i in frame_indexes:
        keyframe_id_set.add(frames[i - 1].id)
    # save all keyframes as image
    video = cv2.VideoCapture(video_path)
    curr_frame = None
    keyframes = []
    success, frame = video.read()
    idx = 0

    base64Frames = []
    #print(keyframe_id_set)
    while (success):
        if idx in keyframe_id_set:
            _, buffer = cv2.imencode(".jpg", frame)
            frame_base64 = base64.b64encode(buffer).decode("utf-8")
            base64Frames.append(frame_base64)
            keyframe_id_set.remove(idx)
        idx = idx + 1
        success, frame = video.read()
    video.release()
    print(len(base64Frames), "frames read.")
    return base64Frames

def generate(client, method, video_id, video_path, max_frame, desc=None):
    base64Frames = extract_keyframes(video_path, max_frame)

    if method == "GPT4V":
        PROMPT_MESSAGES = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Imagine your role is to generate descriptions for videos. You will watch a sequence of keyframes from a video and craft a description based on these keyframes.",
                    }
                ]
            }
        ]
        params = {
            "model": "gpt-4-vision-preview",
            "messages": PROMPT_MESSAGES,
            "max_tokens": 1500,
            "temperature": 0.01,
            "top_p": 1.0,
            "n": 1
        }

        result = client.chat.completions.create(**params)
        full_dict[video_id] = result.choices[0].message.content
        print(result.choices[0].message.content)
    elif method == "GPT4VHA":
        PROMPT_MESSAGES = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Imagine your role is to generate descriptions for videos. You will watch a sequence of keyframes from a video and read the current description of this video. Your task is to revise the description.",
                    },
                    {
                        "type": "text",
                        "text": "Current Description:\n\"{desc}\"\n\n".format(desc=desc)
                    },
                ]
            }
        ]
        params = {
            "model": "gpt-4-vision-preview",
            "messages": PROMPT_MESSAGES,
            "max_tokens": 1500,
            "temperature": 0.01,
            "top_p": 1.0,
            "n": 1
        }

        result = client.chat.completions.create(**params)
        full_dict[video_id] = result.choices[0].message.content
        print(result.choices[0].message.content)
    elif method == "GPT4VAD":
        PROMPT_MESSAGES = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Imagine your role is to generate descriptions for videos to make them accessible to blind and low vision individuals. You will watch a sequence of keyframes from a video. Based on these keyframes, craft a description. You must follow all the given instructions. You should avoid any prefatory language, such as 'the video shows'. Output your result as a dictionary format: {\"Video_Category\": A string representing the category of video you believe it to be, \"Revised_Desc\": A string of description.}",
                    },
                    {
                        "type": "text",
                        "text": "Instructions:\nInstruction #1. Avoid over-describing — Do not include non-essential visual details.\nInstruction #2. Description should not be opinionated unless content demands it.\nInstruction #3. Choose level of detail based on plot relevance when describing scenes.\nInstruction #4. Description should be informative and conversational, in present tense and third-person omniscient.\nInstruction #5. The vocabulary should reflect the predominant language/accent of the program and should be consistent with the genre and tone of the content while also mindful of the target audience. Vocabulary used should ensure accuracy, clarity, and conciseness.\nInstruction #6. Consider historical context and avoid words with negative connotations or bias.\nInstruction #7. Pay attention to verbs — Choose vivid verbs over bland ones with adverbs.\nInstruction #8. Use pronouns only when clear whom they refer to.\nInstruction #9. Use comparisons for shapes and sizes with familiar and globally relevant objects.\nInstruction #10. Maintain consistency in word choice, character qualities, and visual elements for all audio descriptions.\nInstruction #11. Tone and vocabulary should match the target audience's age range.\nInstruction #12. Ensure no errors in word selection, pronunciation, diction, or enunciation.\nInstruction #13. Start with general context, then add details.\nInstruction #14. Describe shape, size, texture, or color as appropriate to the content.\nInstruction #15. Use first-person narrative for engagement if required to engage the audience.\nInstruction #16. Use articles appropriately to introduce or refer to subjects.\nInstruction #17. Prefer formal speech over colloquialisms, except where appropriate.\nInstruction #18. When introducing new terms, objects, or actions, label them first, and then follow with the definitions.\nInstruction #19. Describe objectively without personal interpretation or comment. Also, do not censor content.\nInstruction #20. Deliver narration steadily and impersonally (but not monotonously), matching the program's tone.\nInstruction #21. It can be important to add emotion, excitement, lightness of touch at different points. Adjust style for emotion and mood according to the program's genre.\nInstruction #22. If it is children’s content, tailor language and pace for children's TV, considering audience feedback\nInstruction #23. Do not alter, filter, or exclude content. You should describe what you see. Try to seek simplicity and succinctness in your description.\nInstruction #24. Prioritize what is relevant when describing action as to not affect user experience.\nInstruction #25. Include location, time, and weather conditions when relevant to the scene or plot.\nInstruction #26. Focus on key content for learning and enjoyment when creating audio descriptions. This is so that the intention of the program is conveyed.\nInstruction #27. When describing an instructional video/content, describe the sequence of activities first.\nInstruction #28. For a dramatic production, include elements such as style, setting, focus, period, dress, facial features, objects, and aesthetics.\nInstruction #29. Describe what is most essential for the viewer to know in order to follow, understand, and appreciate the intended learning outcomes of the video/content.\nInstruction #30. The description should describe characters, locations, on-screen action, and on-screen information.\nInstruction #31. Describe only what a sighted viewer can see.\nInstruction #32. Describe main and key supporting characters' visual aspects relevant to identity and personality. Prioritize factual descriptions of traits like hair, skin, eyes, build, height, age, and visible disabilities. Ensure consistency and avoid singling out characters for specific traits. Use person-first language.\nInstruction #33. If unable to confirm or if not established in the plot, do not guess or assume racial, ethnic or gender identity.\nInstruction #34. When naming characters for the first time, aim to include a descriptor before the name (e.g., \"a bearded man, Jack\").\nInstruction #35. Description should convey facial expressions, body language and reactions.\nInstruction #36. When important to the meaning / intent of content, describe race using currently-accepted terminology.\nInstruction #37. Avoid identifying characters solely by gender expression unless it offers unique insights not apparent otherwise to low vision viewers.\nInstruction #38. Describe character clothing if it enhances characterization, plot, setting, or genre enjoyment.\nInstruction #39. If text on the screen is central to understanding, establish a pattern of on-screen words being read. This may include making an announcement, such as \"Words appear\".\nInstruction #40. In the case of subtitles, the describer should read the translation after stating that a subtitle appears.\nInstruction #41. When shot changes are critical to the understanding of the scene, indicate them by describing where the action is or where characters are present in the new shot.\nInstruction #42. Provide description before the content rather than after."
                    },
                    *map(lambda x: {"image": x, "resize": 768}, base64Frames)
                ],
            },
        ]
        params = {
            "model": "gpt-4-vision-preview",
            "messages": PROMPT_MESSAGES,
            "max_tokens": 1500,
            "temperature": 0.01,
            "top_p": 1.0,
            "n": 1
        }

        result = client.chat.completions.create(**params)
        result_dict = json.loads(result.choices[0].message.content)
        full_dict[video_id] = result_dict
        print(result.choices[0].message.content)
    elif method == "GPT4VADHA":

        PROMPT_MESSAGES = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Imagine your role is to generate descriptions for videos to make them accessible to blind and low vision individuals. You will watch a sequence of keyframes from a video and read the current description of this video. Your task is to revise the current description. You must follow all the given instructions. Output your result in a dictionary format: {\"Video_Category\": A string representing the category of video you believe it to be, \"Revised_Desc\": A string of revised description.}",
                    },
                    {
                        "type": "text",
                        "text": "Current Description:\n\"{desc}\"\n\n".format(desc=desc)
                    },
                    {
                        "type": "text",
                        "text": "Instructions:\nInstruction #1. Avoid over-describing — do not include visual images that are not vital to the understanding or enjoyment of the scene.\nInstruction #2. Description should not be opinionated unless content demands it.\nInstruction #3. Choose level of detail based on plot relevance when describing scenes.\nInstruction #4. Description should be informative and conversational, in present tense and third-person omniscient.\nInstruction #5. The vocabulary should reflect the predominant language/accent of the program and should be consistent with the genre and tone of the content while also mindful of the target audience. Vocabulary used should ensure accuracy, clarity, and conciseness.\nInstruction #6. Consider historical context and avoid words with negative connotations or bias.\nInstruction #7. Pay attention to verbs — Choose vivid verbs over bland ones with adverbs.\nInstruction #8. Use pronouns only when clear whom they refer to.\nInstruction #9. Use comparisons for shapes and sizes with familiar and globally relevant objects.\nInstruction #10. Maintain consistency in word choice, character qualities, and visual elements for all audio descriptions.\nInstruction #11. Tone and vocabulary should match the target audience's age range.\nInstruction #12. Ensure no errors in word selection, pronunciation, diction, or enunciation.\nInstruction #13. Start with general context, then add details.\nInstruction #14. Describe shape, size, texture, or color as appropriate to the content.\nInstruction #15. Use first-person narrative for engagement if required to engage the audience.\nInstruction #16. Use articles appropriately to introduce or refer to subjects.\nInstruction #17. Prefer formal speech over colloquialisms, except where appropriate.\nInstruction #18. When introducing new terms, objects, or actions, label them first, and then follow with the definitions.\nInstruction #19. Describe objectively without personal interpretation or comment. Also, do not censor content.\nInstruction #20. Deliver narration steadily and impersonally (but not monotonously), matching the program's tone.\nInstruction #21. It can be important to add emotion, excitement, lightness of touch at different points. Adjust style for emotion and mood according to the program's genre.\nInstruction #22. If it is children’s content, tailor language and pace for children's TV, considering audience feedback\nInstruction #23. Do not alter, filter, or exclude content. You should describe what you see. Try to seek simplicity and succinctness in your description.\nInstruction #24. Prioritize what is relevant when describing action as to not affect user experience.\nInstruction #25. Include location, time, and weather conditions when relevant to the scene or plot.\nInstruction #26. Focus on key content for learning and enjoyment when creating audio descriptions. This is so that the intention of the program is conveyed.\nInstruction #27. When describing an instructional video/content, describe the sequence of activities first.\nInstruction #28. For a dramatic production, include elements such as style, setting, focus, period, dress, facial features, objects, and aesthetics.\nInstruction #29. Describe what is most essential for the viewer to know in order to follow, understand, and appreciate the intended learning outcomes of the video/content.\nInstruction #30. The description should describe characters, locations, on-screen action, and on-screen information.\nInstruction #31. Describe only what a sighted viewer can see.\nInstruction #32. Describe main and key supporting characters' visual aspects relevant to identity and personality. Prioritize factual descriptions of traits like hair, skin, eyes, build, height, age, and visible disabilities. Ensure consistency and avoid singling out characters for specific traits.\nInstruction #33. If unable to confirm or if not established in the plot, do not guess or assume racial, ethnic or gender identity.\nInstruction #34. When naming characters for the first time, aim to include a descriptor before the name (e.g., \"a bearded man, Jack\").\nInstruction #35. Description should convey facial expressions, body language and reactions.\nInstruction #36. When important to the meaning / intent of content, describe race using currently-accepted terminology.\nInstruction #37. Avoid identifying characters solely by gender expression unless it offers unique insights not apparent otherwise to low vision viewers.\nInstruction #38. Describe character clothing if it enhances characterization, plot, setting, or genre enjoyment.\nInstruction #39. If text on the screen is central to understanding, establish a pattern of on-screen words being read. This may include making an announcement, such as \"Words appear\".\nInstruction #40. In the case of subtitles, the describer should read the translation after stating that a subtitle appears.\nInstruction #41. When shot changes are critical to the understanding of the scene, indicate them by describing where the action is or where characters are present in the new shot.\nInstruction #42. Provide description before the content rather than after."
                    },
                    *map(lambda x: {"image": x, "resize": 768}, base64Frames)
                ],
            },
        ]
        params = {
            "model": "gpt-4-vision-preview",
            "messages": PROMPT_MESSAGES,
            "max_tokens": 1500,
            "temperature": 0.01,
            "top_p": 1.0,
            "n": 1
        }

        result = client.chat.completions.create(**params)
        result_dict = json.loads(result.choices[0].message.content)
        full_dict[video_id] = result_dict
        print(result.choices[0].message.content)
    else:
        print("Invalid method name.")

def walk_and_process_videos(client, desc_file, video_folder, target_file, method):
    with open(desc_file, 'r') as file:
        videos = json.load(file)
    for root, dirs, files in os.walk(video_folder):
        for file in files:
            if file.endswith((".mp4")):
                #print(file)

                # Check if the revised description exist
                #if os.path.splitext(file)[0] in descriptions.keys():
                #    continue

                video_path = os.path.join(root, file)
                t = 0

                # Check if the original description exist
                try:
                    desc = videos[os.path.splitext(file)[0]]
                except:
                    continue

                print(os.path.splitext(file)[0], video_path, videos[os.path.splitext(file)[0]])
                #main(os.path.splitext(file)[0], video_path, desc)

                # Try three times in case the API is unstable
                while t < 3:
                    try:
                        # The default maximum number of frames is setting as 80.
                        generate(client, method, os.path.splitext(file)[0], video_path, 80, desc)
                        time.sleep(5)
                        break
                    except:
                        time.sleep(10)
                    t += 1
                with open(target_file, 'w') as file:
                    json.dump(full_dict, file, indent=4)

def main(video_folder, api_key, method, desc_file, target_file):
    client = OpenAI(api_key=api_key)
    walk_and_process_videos(client, desc_file, video_folder, target_file, method)

full_dict = {} # Target dictionary

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some parameters.")
    parser.add_argument("--video_folder", type=str, help="Path to the folder containing videos.")
    parser.add_argument("--desc_file", type=str, help="Path to the file with original human annotation.")
    parser.add_argument("--target_file", type=str, help="Path to the file to store the revised descriptions.")
    parser.add_argument("--api_key", type=str, help="API key for OpenAI")
    parser.add_argument("--method", type=str, choices=["GPT4V", "GPT4VHA", "GPT4VAD", "GPT4VADHA"], default="GPT4VADHA", help="Method to use for processing. GPT4VHA = GPT-4V + Human Annotation; GPT4AD = GPT-4V + AD Guidelines; GPT4VADHA = GPT4-V + AD Guidelines + Human Annotation."
    )

    args = parser.parse_args()
    main(args.video_folder, args.api_key, args.method, args.desc_file, args.target_file)
