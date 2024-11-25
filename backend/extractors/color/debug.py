import os
import shutil

FEATURES_DIR = "/mnt/mmlab2024nas/visedit/AIC2024/code/Features/clip2video"
NEW_DIR = "/mnt/mmlab2024nas/visedit/AIC2024/code/Features/clip2video_new"

for feat_file in sorted(os.listdir(FEATURES_DIR)):
    print(feat_file)
    if feat_file.endswith(".npy"):
        video_name = feat_file.split("-", maxsplit=1)[0]
        batch_name = "Videos_" + video_name[:3]
        new_dir = os.path.join(NEW_DIR, batch_name, video_name)
        os.makedirs(new_dir, exist_ok=True)

        old_path = os.path.join(FEATURES_DIR, feat_file)
        new_path = os.path.join(new_dir, feat_file)

        shutil.copy(old_path, new_path)
        