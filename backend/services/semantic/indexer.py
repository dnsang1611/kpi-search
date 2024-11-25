import os
import json
import numpy
from typing import Dict, List
import faiss
from natsort import natsorted
from tqdm import tqdm
import numpy as np
import sys
import cv2

from ..base_indexer import BaseIndexer

class ImageSemanticIndexer(BaseIndexer):
    def __init__(self, features_dir: str = None, indexer_dir: str = None, 
                 sel_keyframe_dir: str = None, keyframe_dir: str = None):
        # Special arguments
        self.keyframe_dir = keyframe_dir

        # End of special arguments

        super().__init__(features_dir, indexer_dir, sel_keyframe_dir)

    def indexing_methods(self) -> faiss.Index:
        npy_files = natsorted([file for file in os.listdir(self.features_dir) if file.endswith(".npy")])
        features_list = []
        video_frame_mapping = []

        for feat_npy in tqdm(npy_files):
            feats_arr = np.load(os.path.join(self.features_dir, feat_npy))
            video_name = os.path.splitext(feat_npy)[0]
            prefix = "Videos_" + video_name.split('_')[0]
            mapping = sorted(os.listdir(os.path.join(self.keyframe_dir, prefix, video_name)))

            assert len(feats_arr) == len(mapping), f"len(feats) != len(mapping) in {feat_npy}"

            # Get selected frames
            if self.sel_keyframe_dir:
                sel_keyframe_path = os.path.join(self.sel_keyframe_dir, feat_npy.split(".")[0] + ".json")

                with open(sel_keyframe_path, "r") as rf:
                    sel_frames = [frame_item["kept"] for group in json.load(rf) for frame_item in group]

                assert len(sel_frames) == len(mapping), f"len(sel_frames) != len(mapping) in {feat_npy}"

            for id, feat in enumerate(feats_arr):
                if self.sel_keyframe_dir and (not sel_frames[id]):
                    continue

                feat /= np.linalg.norm(feat)
                features_list.append(feat)
                video_frame_mapping.append(os.path.join(prefix, video_name, mapping[id]))

        photo_features = np.vstack(features_list).astype('float32')
        features_list = None
        n, d = photo_features.shape
        index = faiss.IndexFlatIP(d)
        index.add(photo_features)
        photo_features = None
        return index, video_frame_mapping

def timecode_to_seconds(timecode):
    h, m, s = map(float, timecode.split(";"))
    return h * 3600 + m * 60 + s

class VideoSemanticIndexer(BaseIndexer):
    def __init__(self, 
        features_dir: str = None, indexer_dir: str = None, sel_keyframe_dir: str = None,
        keyframe_dir: str = None, video_root: str = None
    ):
        # Special arguments
        self.keyframe_dir = keyframe_dir
        self.video_root = video_root

        # End of special arguments

        super().__init__(features_dir, indexer_dir, sel_keyframe_dir)

    def indexing_methods(self) -> faiss.Index:
        features = []
        mapping = []

        for batch_folder in tqdm(sorted(os.listdir(self.features_dir))):
            batch_dir = os.path.join(self.features_dir, batch_folder)

            for video_folder in sorted(os.listdir(batch_dir)):
                video_dir = os.path.join(batch_dir, video_folder)
                fps = self.get_video_fps(os.path.join(self.video_root, batch_folder, "video", video_folder + ".mp4"))
                
                for scene_file in sorted(os.listdir(video_dir)):
                    # Process mapping
                    _, _, _, start_timecode, end_timecode = scene_file.split(".npy")[0].split("-")

                    if self.sel_keyframe_dir:
                        sel_keyframe_path = os.path.join(self.sel_keyframe_dir, video_folder + ".json")

                        with open(sel_keyframe_path, "r") as rf:
                            sel_frames = [
                                group[-1]["frame"].rsplit("/", maxsplit=1)[-1]
                                for group in json.load(rf)
                            ]
                    else:
                        sel_frames = sorted(os.path.join(self.keyframe_dir, batch_folder, video_folder))

                    frames = self.get_valid_frames(sel_frames, fps, start_timecode, end_timecode)
                    
                    # Skip if there are no valid frames
                    if frames is None:
                        continue

                    frames = [os.path.join(batch_folder, video_folder, frame) for frame in frames]
                    mapping.append(frames)

                    # Normalize features
                    scene_path = os.path.join(video_dir, scene_file)
                    feature = np.load(scene_path)
                    feature = feature / np.linalg.norm(feature)
                    features.append(feature)

        features = np.vstack(features).astype('float32')
        n, d = features.shape
        index = faiss.IndexFlatIP(d)
        index.add(features)

        return index, mapping
    
    def get_video_fps(self, video_path):
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        return fps
    
    def get_valid_frames(self, frames, fps, start_timecode, end_timecode):        
        # Convert timecode to frame id
        start_frame = int(timecode_to_seconds(start_timecode) * fps)
        end_frame = np.floor(timecode_to_seconds(end_timecode) * fps)
        
        # Select valid start
        start_id = 0
        while start_id < len(frames):
            frame_id = int(frames[start_id].split(".")[0])

            if frame_id > start_frame:
                break

            start_id += 1

        # Check if there is valid start frame or not
        if start_id == 0:
            return None
        
        start_id -= 1

        # Select valid end frame
        end_id = start_id
        while end_id < len(frames):
            frame_id = int(frames[end_id].split(".")[0])
            if frame_id >= end_frame:
                break

            end_id += 1
        
        end_id = min(end_id, len(frames) - 1)

        # print(frames[0], fps)
        # print(start_timecode, start_frame, frames[start_id])
        # print(end_timecode, end_frame, frames[end_id])
        # print("============")

        return frames[start_id: end_id + 1]
