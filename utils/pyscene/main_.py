# %%
from pathlib import Path
from scenedetect import detect, AdaptiveDetector, split_video_ffmpeg, FrameTimecode

video_path = Path("/opt/Video_a/Videos_L01/video/L01_V001.mp4")

START_TIME = "00:01:02"
END_TIME = "00:01:09"
# %%
start_frame = FrameTimecode(timecode=START_TIME, fps=30)
end_frame = FrameTimecode(timecode=END_TIME, fps=30)
print(start_frame)
print(end_frame)
split_video_ffmpeg(
    str(video_path),
    [(start_frame, end_frame)],
    output_dir=str(video_path.parent),
    output_file_template="scene-$SCENE_NUMBER-$START_TIME-$END_TIME.mp4",
)
