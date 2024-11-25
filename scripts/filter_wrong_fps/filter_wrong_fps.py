"""Wrong assumptions:
- Batch 1: only 25 fps
- Batch 2: don't handle x.y fps
- Batch 3: handle wrong x.y fps
"""
import cv2
import os
import pandas as pd


DATA_DIR = "/mnt/mmlab2024nas/visedit/AIC2024/data/Video_a"

def get_video_fps(video_path):
    """Trả về số FPS của video."""
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    return fps

error_files = []

for batch_folder in sorted(os.listdir(DATA_DIR)):
    batch_dir = os.path.join(DATA_DIR, batch_folder, "video")
    batch_id = int(batch_folder[-2:])

    for video_file in sorted(os.listdir(batch_dir)):
        # print(video_file)
        video_path = os.path.join(batch_dir, video_file)
        fps = get_video_fps(video_path)

        if batch_id <= 12:
            if fps != 25:
                error_files.append({
                    "video_file": video_file,
                    "fps": fps,
                    "batch": 1,
                    "error": "only handle 25 fps"
                })
        elif batch_id <= 24:
            print(fps)
            if fps != int(fps):
                error_files.append({
                    "video_file": video_file,
                    "fps": fps,
                    "batch": 2,
                    "error": "handle wrongly x.y fps"
                })
        else:
            if fps != int(fps):
                error_files.append({
                    "video_file": video_file,
                    "fps": fps,
                    "batch": 3,
                    "error": "handle wrongly x.y fps"
                })

df = pd.DataFrame(error_files)
df.to_csv("error.csv", index=False)