import ollama
from objectbox_store import ObjectBoxStore

class HistoryAgent:
    def __init__(self, 
                 embedding_model_name='all-MiniLM-L6-v2', 
                 gemma_model='gemma3n', 
                 embedding_dim=384):
        self.db = ObjectBoxStore(embedding_model_name, embedding_dim)
        self.gemma_model = gemma_model
        self.client = ollama.Client()

    def index_documents(self, texts):
        self.db.build_store(texts)

    def query(self, user_query, context_k=3):
        context_docs = self.db.similarity_search(user_query, k=context_k)
        context_str = "\n".join([doc.page_content for doc in context_docs])
        prompt = f"Context: {context_str}\n\nQuestion: {user_query}"
        response = self.client.chat(model=self.gemma_model, prompt=prompt)
        return response['message']
