import faiss
import numpy as np

class Retriever:
    def __init__(self, documents):
        self.documents = documents
        self.index = self._build_index(documents)

    def _build_index(self, documents):
        dimension = 768  # Assume 768-dim embeddings
        index = faiss.IndexFlatL2(dimension)
        embeddings = [self._embed(doc) for doc in documents]
        index.add(np.array(embeddings).astype('float32'))
        return index

    def _embed(self, document):
        # Mock embedding function
        return np.random.rand(768)

    def retrieve(self, query, k=5):
        query_embedding = self._embed(query)
        distances, indices = self.index.search(np.array([query_embedding]).astype('float32'), k)
        return [self.documents[idx] for idx in indices[0]]
