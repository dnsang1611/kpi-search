import os
import cv2
from natsort import natsorted
import sys
import pandas as pd

# Params
batch_start = int(sys.argv[1])
batch_end = int(sys.argv[2])
error_id = int(sys.argv[3])

# Paths
video_root_dir = '/mnt/mmlab2024nas/visedit/AIC2024/data/Video_a'
frame_root_dir = '/mnt/mmlab2024nas/visedit/AIC2024/code/Data/FixError'
checkpoint_path = f'/mnt/mmlabworkspace_new/Students/visedit/AIC2024/Script/cut_frame/errors/error_{error_id}.txt'
os.makedirs(frame_root_dir, exist_ok=True)
wrong_fps_dir = '/mnt/mmlab2024nas/visedit/AIC2024/code/Script/filter_wrong_fps/error.csv'

def get_video_fps(video_path):
    """Trả về số FPS của video."""
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    return fps

# Main
if __name__ == '__main__':
    wrong_df = pd.read_csv(wrong_fps_dir)
    wrong_csvs = wrong_df['video_file']
    sorted_files = natsorted(wrong_csvs)

    for file in sorted_files:
        file = file.replace('.csv', '.mp4')
        batch_name = f'Videos_L{file[1:3]}'
        video_path = os.path.join(video_root_dir, batch_name, 'video', file)
        
        video_name = os.path.basename(video_path).split('.')[0]
        frame_dir = os.path.join(frame_root_dir, batch_name, video_name)
        
        os.makedirs(frame_dir, exist_ok=True)
        
        # Process video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Cannot open video {video_path}")
            with open(checkpoint_path, 'a') as wf:
                wf.write(f"{video_path}\n")
            continue

        # Lấy FPS của video
        fps = get_video_fps(video_path)
        print(f"Processing video: {video_name}, FPS: {fps}")

        frame_index = 0
        next_save_frame = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Nếu frame hiện tại nằm trong khoảng thời gian cần lưu
            if frame_index >= next_save_frame:
                frame_name = f'{int(frame_index):06d}.jpg'
                frame_path = os.path.join(frame_dir, frame_name)
                cv2.imwrite(frame_path, frame)
                # Tính frame tiếp theo cần lưu
                next_save_frame = next_save_frame + fps

            frame_index += 1

        cap.release()
        print(f'Scene frames saved in {frame_dir}')
    # for root, dirs, files in os.walk(video_root_dir):
    #     if 'segmented' in dirs:
    #         dirs.remove('segmented')
    #     if 'segmented_3' in dirs:
    #         dirs.remove('segmented_3')

    #     sorted_files = natsorted(files)
    #     for file in sorted_files:
    #         if file.endswith('.mp4'):
    #             batch_name = os.path.basename(os.path.dirname(root))
    #             print(file)
    #             batch_index = int(batch_name[-2:])

    #             if batch_start > batch_index or batch_index > batch_end:
    #                 continue

    #             video_path = os.path.join(root, file)
    #             video_name = os.path.basename(video_path).split('.')[0]
    #             frame_dir = os.path.join(frame_root_dir, batch_name, video_name)
    #             os.makedirs(frame_dir, exist_ok=True)
                
    #             # Process video
    #             cap = cv2.VideoCapture(video_path)
    #             if not cap.isOpened():
    #                 print(f"Cannot open video {video_path}")
    #                 with open(checkpoint_path, 'a') as wf:
    #                     wf.write(f"{video_path}\n")
    #                 continue

    #             # Lấy FPS của video
    #             fps = get_video_fps(video_path)
    #             print(f"Processing video: {video_name}, FPS: {fps}")

    #             frame_index = 0
    #             next_save_frame = 0
    #             while cap.isOpened():
    #                 ret, frame = cap.read()
    #                 if not ret:
    #                     break

    #                 # Nếu frame hiện tại nằm trong khoảng thời gian cần lưu
    #                 if frame_index >= next_save_frame:
    #                     frame_name = f'{int(frame_index):06d}.jpg'
    #                     frame_path = os.path.join(frame_dir, frame_name)
    #                     cv2.imwrite(frame_path, frame)
    #                     # Tính frame tiếp theo cần lưu
    #                     next_save_frame = next_save_frame + fps

    #                 frame_index += 1

    #             cap.release()
    #             print(f'Scene frames saved in {frame_dir}')


