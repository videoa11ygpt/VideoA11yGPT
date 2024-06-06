# VideoA11yGPT

## Files
```shell
.
├── assets
│   ├── VALOR32K
│   │   └──desc_test.json
│   │   └──desc_train.json
│   │   └──desc_val.json
│   ├── YouCook2
│   │   └──desc_train_pair_yc2.json
│   │   └──desc_val_pair_yc2.json
├── utils
│   ├── cut_video.py
│   └── download_video.py
└── main.py

```

## Getting Started

### Installation

- Clone this repo:
```bash
git clone https://github.com/videoa11ygpt/VideoA11yGPT.git
cd VideoA11yGPT
```

- Dependencies
```
pip install -r requirements.txt
```

## Prepare Data from Original Datasets

- We provided the original metadata files from VALOR32K and YouCook2 datasets, they are in .json format.

### Download Videos from YouTube

- Prepare your list of YouTube video IDs in a text file (e.g., `video_ids.txt`) from the dataset files.
- Run the script below:
  
```
python ./utils/download_video.py --max_workers <max_workers> --target_folder <Your folder to store videos> --video_ids_file <video_ids_file (e.g., `video_ids.txt`)>
```

### Cut the Videos as Clips (Only for VALOR32K)

- The video IDs in VALOR32K are shown like `YouTubeID_StartTime_EndTime`.
- Run the script below:
  
```
python ./utils/cut_video.py --json_file <Path to the JSON file containing the video IDs.> --original_path <Directory path where the original videos are stored.> --new_path <Directory path where the processed videos will be saved.>
```

## Generate Video Descriptions

- Run the script below with the necessary arguments: 

```
python main.py --video_folder <path/to/videos> --desc_file <path/to/original_descriptions.json> --target_file <path/to/target_descriptions.json> --api_key <your_OPENAI_api_key> --method <one from the four provided>
```
- --video_folder: Directory containing video files.
- --desc_file: File containing original video descriptions.
- --target_file: File where the generated video descriptions will be saved.
- --api_key: API key for accessing the AI processing features.
- --method: The processing method to use. Each of them represents a prompt. Options are:
    - GPT4V: Use only GPT-4V for video description (_GPT-4V_).
    - GPT4VHA: Combine GPT-4V with Human Annotation (_GPT-4V + Human Annotation_).
    - GPT4AD: GPT-4V with our AD Guidelines (_VideoA11yGPT w/o HA_).
    - GPT4VADHA: Combination of GPT-4V, our AD Guidelines, and Human Annotation (**_VideoA11yGPT_**).


## License

This project is licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) License.
