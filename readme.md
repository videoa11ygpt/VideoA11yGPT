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

- 
```
python adv_train_PSP_S1.py --task train --model_save_root MODEL_SAVE_ROOT --data_split train --image_save_root RODPatch_ROOT --image_save_root_adv AdvPatch_ROOT --max_iter_d 2000 --learning_rate_d 0.01 --max_iter_adv 1000 --learning_rate_adv 0.003 --batch_size 8 --val_batch_size 32 --num_epoch 15 --with_psp --wandb_usr USER_NAME --wandb_proj PROJECT_NAME
```

## License

This project is licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) License.
