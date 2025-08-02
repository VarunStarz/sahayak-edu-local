from langchain_objectbox.vectorstores import ObjectBox
from sentence_transformers import SentenceTransformer

class ObjectBoxStore:
    def __init__(self, embedding_model_name='all-MiniLM-L6-v2', embedding_dim=384):
        self.embedder = SentenceTransformer(embedding_model_name)
        self.embedding_dim = embedding_dim
        self.store = None

    def build_store(self, texts):
        embeddings = self.embedder.encode(texts)
        self.store = ObjectBox.from_texts(
            texts=texts,
            embeddings=embeddings,
            embedding_dimensions=self.embedding_dim
        )

    def similarity_search(self, query, k=3):
        query_embedding = self.embedder.encode([query])
        return self.store.similarity_search_by_vector(query_embedding[0], k=k)
