"""FAISS-backed vector index, mapping SQLite photo ids to CLIP embeddings."""
import faiss
import numpy as np
from pathlib import Path


class VectorIndexStore:
    def __init__(self, index_path, dim=512):
        self.index_path = index_path
        self.dim = dim
        Path(index_path).parent.mkdir(parents=True, exist_ok=True)
        if Path(index_path).exists():
            self.index = faiss.read_index(index_path)
        else:
            self.index = faiss.IndexIDMap(faiss.IndexFlatIP(dim))

    def add(self, ids, vectors):
        ids = np.asarray(ids, dtype=np.int64)
        vectors = np.asarray(vectors, dtype=np.float32)
        self.index.remove_ids(ids)  # re-indexing a changed photo replaces its vector
        self.index.add_with_ids(vectors, ids)

    def search(self, query_vector, top_k=20):
        query_vector = np.asarray(query_vector, dtype=np.float32).reshape(1, -1)
        scores, ids = self.index.search(query_vector, top_k)
        return [(int(i), float(s)) for i, s in zip(ids[0], scores[0]) if i != -1]

    def save(self):
        faiss.write_index(self.index, self.index_path)

    def __len__(self):
        return self.index.ntotal
