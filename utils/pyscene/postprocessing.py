from pathlib import Path

data_path = Path("/mmlabworkspace/Datasets/AIC2024/Video_a")

# get all segments folders
segments = [x / "segmented" for x in data_path.iterdir() if x.is_dir()]

files = []

for segment in segments:
    for file in segment.iterdir():
        for video_path in file.iterdir():
            files.append(video_path)
print(len(files), files[:3])
