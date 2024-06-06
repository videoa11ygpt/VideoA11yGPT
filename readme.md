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

- Generated attacked videos in object only mode. IMG_SAVE_FOLDER is where to save generated videos.
```
python adv_train_PSP_S1.py --task generate --attack_name advtexture --data_split dev --image_save_root IMG_SAVE_FOLDER
```

- Generated attacked images in BPDA mode (for inference/visualization)
```
python adv_train_PSP_S1.py --task generate --psp_mode BPDA --psp_load_dir PSP_CKPT_PATH --attack_name robustDpatch --data_split dev --image_save_root IMG_SAVE_FOLDER
```

### Train PSP model

- Train S1 PSP downstream only, using imgs generated in "image_save_root" and "image_save_root_adv"
```
python adv_train_PSP_S1.py --task train --model_save_root MODEL_SAVE_ROOT --data_split train --image_save_root RODPatch_ROOT --image_save_root_adv AdvPatch_ROOT --max_iter_d 2000 --learning_rate_d 0.01 --max_iter_adv 1000 --learning_rate_adv 0.003 --batch_size 8 --val_batch_size 32 --num_epoch 15 --with_psp --wandb_usr USER_NAME --wandb_proj PROJECT_NAME
```

- Train S2 PSP adaptive attack, new attack images are generated for each iteration, do not use pregenerated imgs
- Tracking
```
python adv_train_PSP_S2.py  --model_save_root MODEL_SAVE_ROOT --output_dir LOG_OUTPUT_ROOT --attack_name BPDA --num_epoch 20 --batch_size 44 --for_video
```

### Test defense results
- Set "max_iter_test" and "learning_rate_test" to be the same number of the attack parameters you need to test.
```
python adv_train_PSP_S1.py --task test --attack_name robustDpatch --max_iter_test 2000 --learning_rate_test 0.01 --data_split dev --image_save_root IMG_SAVE_FOLDER
```
