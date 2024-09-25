import numpy as np
from sentence_transformers import SentenceTransformer

class SemanticRouter():
    def __init__(self, routes):
        self.routes = routes
        self.embedding_model = SentenceTransformer("keepitreal/vietnamese-sbert")
        self.routesEmbedding = {}
        self.routesEmbeddingCal = {}

        for route in self.routes:
            self.routesEmbedding[
                route.name
            ] = self.embedding_model.encode(route.samples)

        for route in self.routes:
            self.routesEmbeddingCal[
                route.name
            ] = self.routesEmbedding[route.name] / np.linalg.norm(self.routesEmbedding[route.name])

    def get_routes(self):
        return self.routes

    def guide(self, query):
        queryEmbedding = self.embedding_model.encode([query]) 
        queryEmbedding = queryEmbedding / np.linalg.norm(queryEmbedding)
        scores = []

        # Calculate the cosine similarity of the query embedding with the sample embeddings of the router.

        for route in self.routes:
            routeEmbeddingCal = self.routesEmbeddingCal[route.name]
            score = np.mean(np.dot(routeEmbeddingCal, queryEmbedding.T).flatten())
            scores.append((score, route.name))

        scores.sort(reverse=True)
        return scores[0]
