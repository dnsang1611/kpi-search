from typing import List, Dict
import numpy as np

from .indexer import ColorIndexer

class ColorSearchEngine:
    def __init__(self, indexer: ColorIndexer):
        self.indexer = indexer
        self.colors = [
            "black", "blue", "brown", "grey", "green", 
            "orange", "pink", "purple", "red", "white", "yellow"
        ]

        self.color2id = {color: i for i, color in enumerate(self.colors)}

    def ohe_color(self, feature):
        ohe_feature = []
        for color in feature:
            ohe = np.zeros((len(self.colors)))
            if color != -1:
                ohe[color] = 1
            ohe_feature.append(ohe)
        
        return np.hstack(ohe_feature).astype(np.float32)
    
    def process_query(self, query):
        color_ids = []
        for color in query:
            color_ids.append(self.color2id.get(color, -1))

        return self.ohe_color(color_ids)

    def search(self, query: List[str], topk: int) -> List[Dict]:
        processed_query = self.process_query(query).reshape(1, -1)
        index, video_frame_mapping = self.indexer.index, self.indexer.mapping
        scores, indices = index.search(processed_query, topk)

        results = [
            {
                "frame": video_frame_mapping[index],
                "score": float(scores[0][i])
            }
            for i, index in enumerate(indices[0])
        ]

        return results