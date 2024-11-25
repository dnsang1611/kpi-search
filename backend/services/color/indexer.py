import faiss
from tqdm import tqdm
import os
import numpy as np
import json

from ..base_indexer import BaseIndexer

class ColorIndexer(BaseIndexer):
    def __init__(self, features_dir: str = None, indexer_dir: str = None, sel_keyframe_dir: str = None):
        super().__init__(features_dir, indexer_dir, sel_keyframe_dir)

    def indexing_methods(self) -> faiss.Index:
        features_list = []
        video_frame_mapping = []

        for batch_folder in tqdm(sorted(os.listdir(self.features_dir))):
            batch_path = os.path.join(self.features_dir, batch_folder)

            for video_folder in sorted(os.listdir(batch_path)):
                video_path = os.path.join(batch_path, video_folder)

                if self.sel_keyframe_dir:
                    sel_keyframe_path = os.path.join(self.sel_keyframe_dir, video_folder + ".json")

                    with open(sel_keyframe_path, "r") as rf:
                        sel_frames = [group[-1]["frame"] for group in json.load(rf)]

                for frame_npy in sorted(os.listdir(video_path)):
                    frame_path = os.path.join(video_path, frame_npy)
                    frame_name = os.path.join(batch_folder, video_folder, frame_npy.split(".")[0] + ".jpg")

                    # Check if npy file is found
                    if not (os.path.isfile(frame_path) and frame_path.endswith('.npy')):
                        continue

                    # Check if current frame is selected
                    if self.sel_keyframe_dir and (frame_name not in sel_frames):
                        continue

                    feature = np.load(frame_path)
                    features_list.append(feature)
                    frame_path_jpg = frame_path.replace('.npy', '.jpg').split('/')[-3:]
                    frame_path_jpg = "/".join(frame_path_jpg)
                    video_frame_mapping.append(frame_path_jpg)
                
        features = np.vstack(features_list).astype('float32')
        n, d = features.shape
        index = faiss.IndexFlatIP(d)
        index.add(features)
        return index, video_frame_mapping