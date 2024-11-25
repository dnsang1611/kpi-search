import numpy as np
from typing import List, Dict

from .indexer import ImageSemanticIndexer, VideoSemanticIndexer

class ImageSemanticSearchEngine:
    def __init__(self, indexer: ImageSemanticIndexer):
        self.indexer = indexer

    def search(self, query_arr: np.array, topk: int) -> List[dict]:
        index, video_frame_mapping = self.indexer.index, self.indexer.mapping
        query_arr /= np.linalg.norm(query_arr)
        scores, indices = index.search(np.expand_dims(query_arr, axis=0), topk)
        
        return [
            {
                "frame": video_frame_mapping[index],
                "score": float(scores[0][i])
            }
            for i, index in enumerate(indices[0])
        ]
    
class VideoSemanticSearchEngine:
    def __init__(self, indexer: VideoSemanticIndexer):
        self.indexer = indexer

    def search(self, query_arr: np.array, topk: int) -> List[dict]:
        index, video_frame_mapping = self.indexer.index, self.indexer.mapping
        query_arr /= np.linalg.norm(query_arr)
        print(query_arr.shape)
        scores, indices = index.search(query_arr.reshape(1, -1), topk)
        
        return [
            {
                "frame": frame_name,
                "score": float(scores[0][i])
            }
            for i, index in enumerate(indices[0])
            for frame_name in video_frame_mapping[index]
        ][:topk]