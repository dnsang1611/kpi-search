import google.generativeai as genai
from api_keys import API_KEYS
from utils import timestamp_to_frame
import json
from pathlib import Path

data_path = Path("/mmlabworkspace/Datasets/AIC2024/Video_a")


class FrameCode:
    def __init__(self, min, sec):
        self.min = min
        self.sec = sec
        self.idx = None

    @staticmethod
    def parse_str(time_str: str, sep=";"):
        parts = time_str.split(sep)
        return FrameCode(int(parts[1]), int(parts[2]))

    def __str__(self):
        return f"{self.min:02d}:{self.sec:02d}"


def build_prompt(start: FrameCode, end: FrameCode):
    return f"""
    viết đoạn mô tả nội dung chính và từng chi tiết nhỏ nhất có trong các đoạn video được cung cấp trong đoạn từ phút {str(start)} đến phút {str(end)}.
    """


# get all segments folders
batchs = [x / "segmented" for x in data_path.iterdir() if x.is_dir()]

batchs.sort()

genai.configure(api_key=API_KEYS[0])

for f in genai.list_files():
    f.delete()
    print(f"Deleted {f.name}")

# exit(0)

model = genai.GenerativeModel(model_name="gemini-1.5-flash")
root = Path("/mmlabworkspace/Datasets/AIC2024/shot_summary")
for batch in batchs:
    videos = [x for x in batch.glob("L*") if x.is_dir()]
    videos.sort()

    # create a folder to store shot summary
    shot_summary_folder = root / batch.parent.name
    shot_summary_folder.mkdir(exist_ok=True)

    for video in videos:
        minute_threshold = 1
        shots = []
        acc_idx = 0
        shot_summary = []
        last_start_frame = None

        # upload the whole video
        video_path = video.parent.parent / "video" / f"{video.name}.mp4"
        video_file = genai.upload_file(path=str(video_path))
        print(f"Uploaded {video_file.name}")

        segment_paths = list(video.iterdir())
        segment_paths.sort()
        for idx, segment_path in enumerate(segment_paths):
            # print(idx, segment_path)

            # get end time of the video
            name_parts = segment_path.name.split("-")
            start_time = name_parts[-2][:-4]  # remove milliseconds
            end_time = name_parts[-1][:-8]  # remove milliseconds and extension
            start_frame_idx = timestamp_to_frame(start_time)
            end_frame_idx = timestamp_to_frame(end_time)
            # if number of frames is less than 25 * 2, skip less than 2 seconds
            if end_frame_idx - start_frame_idx < 50:
                continue

            start_moment = FrameCode.parse_str(start_time)
            start_moment.idx = start_frame_idx
            end_moment = FrameCode.parse_str(end_time)
            end_moment.idx = end_frame_idx

            if last_start_frame is None:
                last_start_frame = start_moment
            if int(end_moment.min) >= minute_threshold:
                print(
                    f"Summarize | start: {str(last_start_frame)} - end: {str(end_moment)}"
                )
                frame_end_id = f"{segment_path.parent.name}/{end_moment.idx}.mp4"
                frame_start_id = (
                    f"{segment_path.parent.name}/{last_start_frame.idx}.mp4"
                )

                prompt = build_prompt(last_start_frame, end_moment)
                # print(prompt)
                respond = model.generate_content([video_file, prompt])
                print(respond.text)

                result = {
                    "id": acc_idx,
                    "frame_start": frame_start_id,
                    "frame_end": frame_end_id,
                    "text": respond.text,
                }
                shot_summary.append(result)
                acc_idx += 1
                minute_threshold += 1
                last_start_frame = end_moment
                shots = []
                with open(
                    shot_summary_folder / f"{video.name}.json",
                    "w",
                ) as f:
                    # overwrite the file
                    json.dump(shot_summary, f, ensure_ascii=False, indent=4)
        print(f"Finished {video.name}")
        video_file.delete()
        exit(0)
