import json
import os
import faiss

class BaseIndexer:
    def __init__(self, features_dir: str = None, indexer_dir: str = None, sel_keyframe_dir: str = None):
        self.features_dir = features_dir
        self.indexer_dir = indexer_dir
        self.sel_keyframe_dir = sel_keyframe_dir

        if self.features_dir is None or self.indexer_dir is None:
            self.log("You must specfiy both features_dir and indexer_dir")
        elif os.path.exists(self.indexer_dir):
            self.log("indexer_dir is found")
            self.log(f"Loading indexer from {self.indexer_dir}")
            self.index, self.mapping = self.load_indexer()
            self.log(f"Loading successfully")
        else:
            self.log("Because your indexer_dir is not found, we try to create new indexer.")
            self.log(f"Creating indexer from {self.features_dir}")
            self.index, self.mapping = self.indexing_methods()
            self.save_indexer()
            self.log(f"Create successfully! Indexer is saved at {self.indexer_dir}")

        self.log(f"Size of index: ({self.index.ntotal}, {self.index.d})")
        self.log(f"Length of mapping: {len(self.mapping)}")

        if isinstance(self.mapping[0], str):
            batch_set = set([int(frame[8:10]) for frame in self.mapping])
        elif isinstance(self.mapping[0], list):
            batch_set = set([int(frame[8:10]) for frames in self.mapping for frame in frames])

        self.log(f"Number of batches: {len(batch_set)}")

    def log(self, message):
        print(f"\033[1;32;40m {self.__class__.__name__}: \033[0m", message)

    def indexing_methods(self):
        pass

    def save_indexer(self):
        os.makedirs(self.indexer_dir, exist_ok=True)
        index_path = os.path.join(self.indexer_dir, 'index.index')
        mapping_path = os.path.join(self.indexer_dir, 'mapping.json')

        faiss.write_index(self.index, index_path)
        with open(mapping_path, 'w') as wf:
            json.dump(self.mapping, wf, indent=3)

    def load_indexer(self):
        index_path = os.path.join(self.indexer_dir, 'index.index')
        mapping_path = os.path.join(self.indexer_dir, 'mapping.json')

        index = faiss.read_index(index_path)
        with open(mapping_path, 'r') as rf:
            mapping = json.load(rf)

        return index, mapping
    
