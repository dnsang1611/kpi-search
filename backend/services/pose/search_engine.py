import numpy as np
from typing import List, Dict

from .indexer import PoseIndexer

class PoseSearchEngine:
    def __init__(self, indexer: PoseIndexer):
        self.indexer = indexer

    def search(self, query_arr: np.array, topk: int) -> List[dict]:
        pass