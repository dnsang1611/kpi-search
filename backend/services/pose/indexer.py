
from ..base_indexer import BaseIndexer

class PoseIndexer(BaseIndexer):
    def __init__(self, features_dir: str = None, indexer_dir: str = None):
        super().__init__(features_dir, indexer_dir)

    def indexing_methods(self):
        pass