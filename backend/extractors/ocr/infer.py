import sys
sys.path.extend(['DeepSolo', 'parseq']) # Add paths for SceneTextPipeline

import numpy as np
import pandas as pd
from PIL import Image
from models import SceneTextPipeline
import time
from utils import visualize
import os
from detectron2.data.detection_utils import read_image
from pathlib import Path
import glob
import json
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Color extractor args parser")

    # Add arguments to the parser
    parser.add_argument('--keyframe-dir', type=str, help='Directory to data')
    parser.add_argument('--json-path', type=str, help='Directory to features')
    parser.add_argument('--start-batch', type=int, help='Index of start batch')
    parser.add_argument('--end-batch', type=int, help='Index of end batch')
    parser.add_argument('--det-batch-size', type=int, help='Batch size of detection')
    parser.add_argument('--recog-batch-size', type=int, default=32, help='Batch size of recognition')

    # Parse the arguments
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()

    batch_dir = args.keyframe_dir
    json_path = args.json_path
    start_batch = args.start_batch
    end_batch = args.end_batch
    batch_size = args.det_batch_size
    recog_batch_size = args.recog_batch_size

    # Pipeline
    pipeline = SceneTextPipeline(
        'DeepSolo/configs/ViTAEv2_S/VinText/finetune_vintext.yaml',
        'pretrained/vintext_best_deepsolo_17999.pth',
        'pretrained/vintext_best_parseq.ckpt'
    )

    # Load checkpoint
    if os.path.exists(json_path):
        with open(json_path, 'r') as rf:
            features = json.load(rf)
            processed_frames = [feat["frame"] for feat in features]
    else:
        features = []
        processed_frames = []
    
    # Filter out frames
    frame_paths = sorted(glob.glob(f'{batch_dir}/*/*/*.jpg'))
    new_frame_paths = []

    rerun_csv = pd.read_csv("/mnt/mmlab2024nas/visedit/AIC2024/code/Script/filter_wrong_fps/error.csv")
    rerun_videos = list(rerun_csv["video_file"].map(lambda x: x.split(".")[0]))
    print(rerun_videos)

    for frame_path in frame_paths:
        # Fix wrong pfs
        _, video_name, frame_name = frame_path.rsplit("/", maxsplit=2)
        if video_name in rerun_videos:
            continue

        # Filter out frames which is not in desired batches
        batch_idx = int(frame_path.rsplit("/", maxsplit=2)[1][1:3])
        if not (start_batch <= batch_idx <= end_batch):
            continue
    
        # Filter out processed frames
        if os.path.join(f"Videos_L{batch_idx:02}", video_name, frame_name.split(".")[0]) in processed_frames:
            print(f"{video_name} {frame_name} found in checkpoint. Skip ...")
            continue

        new_frame_paths.append(frame_path)
        
    frame_paths = new_frame_paths

    # Process
    cnt = len(processed_frames)

    for i in range(0, len(frame_paths), batch_size):
        batch_frame_paths = frame_paths[i: i + batch_size]
        
        # Infer
        batch_rel_paths = [os.path.relpath(Path(frame_path), batch_dir) for frame_path in batch_frame_paths]
        frame_names = [os.path.splitext(rel_frame_path)[0] for rel_frame_path in batch_rel_paths]

        frames = [read_image(frame_path, format="BGR") for frame_path in batch_frame_paths]
        all_predictions = pipeline(frames, threshold=0.3, recog_batch_size=recog_batch_size)

        for j in range(len(all_predictions)):
            features.append({
                'id': cnt,
                'frame': frame_names[j],
                'ocr_text': ' '.join(all_predictions[j]['rec'])
            })

            # Save checkpoint
            if cnt % 10 == 0:
                with open(json_path, 'w', encoding='utf-8') as wf:
                    json.dump(features, wf, indent=4, ensure_ascii=False)

            cnt += 1

    with open(json_path, 'w', encoding='utf-8') as wf:
        json.dump(features, wf, indent=4, ensure_ascii=False)