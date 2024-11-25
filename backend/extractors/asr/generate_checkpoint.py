import os

CHECKPOINT_PATH = '/mnt/mmlab2024nas/visedit/AIC2024/code/Backend/ASR/checkpoints/batch3.txt'
VIDEO_SEGMENTS_PATH = '/mnt/mmlab2024nas/visedit/AIC2024/data/Audio_batch3'

# Make sure to open the checkpoint file in append mode ('a') so that existing content is not overwritten.
with open(CHECKPOINT_PATH, 'a') as checkpoint_file:
    for video in sorted(os.listdir(VIDEO_SEGMENTS_PATH)):
        video_path = os.path.join(VIDEO_SEGMENTS_PATH, video)

        for audio in sorted(os.listdir(video_path)):
            audio_path = os.path.join(video_path, audio)
            print(audio_path)
            # Write the audio path to the checkpoint file
            checkpoint_file.write(audio_path + '\n')

# The checkpoint file will be automatically closed when the 'with' block exits.


