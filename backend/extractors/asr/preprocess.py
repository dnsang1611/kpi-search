import os
import pandas as pd
import subprocess
import librosa
import soundfile as sf
import sys

# Params
batch_start = int(sys.argv[1])
batch_end = int(sys.argv[2])

# Paths
input_videos_dir = "/mnt/mmlab2024nas/visedit/AIC2024/data/Video_a"
input_meta_dir = "/mnt/mmlab2024nas/visedit/AIC2024/code/Data/batch3_Mapframe"
output_dir = "/mnt/mmlab2024nas/visedit/AIC2024/data/Audio_batch3"

# Convert to minute:second
def convert(seconds):
    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)
    return f"{minutes:02d}:{remaining_seconds:02d}"

# Resample to 16kHz
def resample_audio(input_file, output_file, target_sr=16000):
    audio, current_sr = librosa.load(input_file, sr=None)
    if current_sr != target_sr:
        audio_resampled = librosa.resample(audio, orig_sr=current_sr, target_sr=target_sr)
        sf.write(output_file, audio_resampled, target_sr)
    else:
        sf.write(output_file, audio, current_sr)

# Function to cut video
def cut_video(input_video, output_video, start_frame, end_frame, start_time, end_time):
    subprocess.run(["ffmpeg", "-i", input_video, "-ss", convert(start_time), "-to", convert(end_time), output_video])

# Iterate through each CSV file in the Meta directory
input_meta_files = os.listdir(input_meta_dir)

# Filter out files in selected batches
print(f"Filtering out files from batch {batch_start} to {batch_end}...")

input_meta_files = sorted([file for file in input_meta_files if batch_start <= int(file[1:3]) <= batch_end])

for file in input_meta_files:
    if file.endswith(".csv"):
        csv_path = os.path.join(input_meta_dir, file)
        video_name = os.path.splitext(file)[0]
        batch = video_name.split('_')[0]

        # Create output subfolder in the output directory
        output_subfolder = os.path.join(output_dir, video_name)
        print(output_subfolder)
        if not os.path.exists(output_subfolder):
            os.makedirs(output_subfolder)

        df = pd.read_csv(csv_path)
        segment_duration = 5  # độ dài segment 5s

        for i in range(len(df) - segment_duration):
            start_frame = df.loc[i, 'n']
            end_frame = df.loc[i + segment_duration, 'n']
            start_time = df.loc[i, 'pts_time']
            end_time = df.loc[i + segment_duration, 'pts_time']
            
            output_wav = os.path.join(output_subfolder, f"{start_frame:04d}_{end_frame:04d}.wav")
            video_file = os.path.join(input_videos_dir, f"Videos_{batch}", "video", f"{video_name}.mp4")

            # Check if the output_wav file already exists, if it does, skip processing
            if os.path.exists(output_wav):
                print(f"Skipping file {output_wav} because it already exists")
                continue

            # If the converted audio has length under 2s (e.g: from 13.4s to 13.8s), skip it
            if abs(float(end_time) - float(start_time)) <= 2.0:
                continue

            # Process
            cut_video(video_file, output_wav, start_frame, end_frame, start_time, end_time)
            # Resample the extracted audio segment to 16 kHz
            resample_audio(output_wav, output_wav)

print("Done")