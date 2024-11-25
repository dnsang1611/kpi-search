import pandas as pd
import os
import numpy as np


data_dir = "/mnt/mmlab2024nas/visedit/AIC2024/data/Video_a"
output_path = "post_processed_scenes.csv"
max_length = 10 # in seconds

def seconds_to_timecode(seconds):
    """ Convert seconds to timecode string (HH:MM:SS.MS) """
    seconds = np.round(seconds, 3)
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    milliseconds = int((seconds % 1) * 1000)
    seconds = int(seconds % 60)
    return f"{hours:02d};{minutes:02d};{seconds:02d}.{milliseconds:03d}"

def timecode_to_seconds(timecode):
    h, m, s = map(float, timecode.split(";"))
    return h * 3600 + m * 60 + s

if __name__ == "__main__":
    splitted_scenes = []

    for batch_folder in sorted(os.listdir(data_dir)):
        batch_dir = os.path.join(data_dir, batch_folder, "segmented")
        print(batch_folder)
        for video_folder in sorted(os.listdir(batch_dir)):
            video_dir = os.path.join(batch_dir, video_folder)

            for scene_file in sorted(os.listdir(video_dir)):
                if not scene_file.endswith(".mp4"):
                    continue

                batch_id = int(video_folder[1:3])
                video_path = os.path.join(data_dir, "Videos_" + video_folder[:3], "video", video_folder + ".mp4")
                
                _, _, start_timecode, end_timecode = scene_file.rsplit(".", maxsplit=1)[0].split("-")
                
                start_time = timecode_to_seconds(start_timecode)
                end_time = timecode_to_seconds(end_timecode)
                duration = end_time - start_time

                if duration <= max_length:
                    splitted_scenes.append({
                        "batch_id": batch_id,
                        "video_name": video_folder,
                        "video_path": video_path,
                        "start_time": start_time,
                        "end_time": end_time,
                        "start_timecode": start_timecode,
                        "end_timecode": end_timecode,
                        "duration": duration
                    })

                    continue

                # Split scene
                n_splits = np.ceil(duration / max_length).astype(int)
                duration = duration / n_splits

                for i in range(n_splits):
                    new_start_time = start_time + i * duration
                    new_end_time = start_time + (i + 1) * duration
                    splitted_scenes.append({
                        "batch_id": batch_id,
                        "video_name": video_folder,
                        "video_path": video_path,
                        "start_time": new_start_time,
                        "end_time": new_end_time,
                        "start_timecode": seconds_to_timecode(new_start_time),
                        "end_timecode": seconds_to_timecode(new_end_time),
                        "duration": duration
                    })

    df = pd.DataFrame(splitted_scenes)
    n_low = (df["duration"] < 5).sum()
    n_high = (df["duration"] > 10).sum()
    n_middle = df.shape[0] - n_low - n_high

    print("# of scenes < 5:", n_low)
    print("# of scenes 5 <= seconds <= 10:", n_middle)
    print("# of scenes with seconds > 10:", n_high)

    df.to_csv(output_path, index=False)