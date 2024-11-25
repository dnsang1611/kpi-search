# %%
from pathlib import Path
from scenedetect import detect, AdaptiveDetector, split_video_ffmpeg
import os

data_path = Path("/opt/Video_a")
# data_path = Path("/mmlabworkspace/Datasets/AIC2024/Video")

BATCH_ID = os.environ.get("BATCH_ID", default="null")
assert BATCH_ID != "null", "Please provide BATCH_ID environment variable"
BATCH_ID = int(BATCH_ID)

sub_folders = [x for x in data_path.iterdir() if x.is_dir()]
# %%
sub_folders.sort()

if BATCH_ID == 1:
    sub_folders = [sub_folders[24]] # Videos_L25
elif BATCH_ID == 2:
    sub_folders = [sub_folders[25]] # Videos_L26
elif BATCH_ID == 3:
    sub_folders = sub_folders[26:29] # Videos_L27,28,29
elif BATCH_ID == 4:
    sub_folders = [sub_folders[29]] # Videos_L30

print(f"Processing subfolders: {[x.name for x in sub_folders]}")
# %%
for sub_folder in sub_folders:
    # create new subfolder named 'segmented' in each subfolder
    segmented_folder = sub_folder / "segmented"
    segmented_folder.mkdir(exist_ok=True)

    video_names = (sub_folder / "video").glob("*.mp4")
    print(f"___Processing {sub_folder.name}___")
    for video_name in video_names:
        print(f"Processing {video_name.name}...")
        # create new subfolder named by video name in segmented folder
        video_path = video_name
        video_name = video_name.stem
        video_folder = segmented_folder / video_name
        video_folder.mkdir(exist_ok=True)

        # split video into scenes
        scene_list = detect(str(video_path), AdaptiveDetector())
        split_video_ffmpeg(
            str(video_path),
            scene_list,
            output_dir=str(video_folder),
            # output file template is scene-<scene number>-<start time>-<end time>.mp4
            output_file_template="scene-$SCENE_NUMBER-$START_TIME-$END_TIME.mp4",
        )
        print(f"{video_name} done!")
