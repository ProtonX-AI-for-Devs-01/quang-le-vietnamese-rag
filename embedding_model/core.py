from sentence_transformers import SentenceTransformer

class EmbeddingModel():
    def __init__(self):
        self.embedding_model = SentenceTransformer("keepitreal/vietnamese-sbert")
        
    def get_embedding(self, text: str):
        if not text.strip():
            return []

        embedding = self.embedding_model.encode(text)
        return embedding.tolist()
