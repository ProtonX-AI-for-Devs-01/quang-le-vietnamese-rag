from .mongo_client import MongoClient

# default number of top matches to retrieve from vector search
DEFAULT_SEARCH_LIMIT = 4

class RAG():
    def __init__(self, 
            mongodb_uri: str,
            db_name: str,
            db_collection: str,
            index_name: str
        ):
        self.client = MongoClient().get_mongo_client(mongodb_uri)
        self.db = self.client[db_name] 
        self.collection = self.db[db_collection]
        self.index_name = index_name
   
    def vector_search(
        self, 
        query_embedding: list, 
        limit=DEFAULT_SEARCH_LIMIT):

        if query_embedding is None:
            return "Invalid query or embedding generation failed."

        # Define the vector search pipeline
        vector_search_stage = {
            "$vectorSearch": {
                "index": self.index_name,
                "queryVector": query_embedding,
                "path": "embedding",
                "numCandidates": 150,  # Number of candidate matches to consider
                "limit": limit  # Return top matches
            }
        }

        unset_stage = {
            "$unset": "embedding" 
        }

        project_stage = {
            "$project": {
                "_id": 0,  # Exclude the _id field
                "fullplot": 1,  # Include the plot field
                "title": 1,  # Include the title field
                "genres": 1, # Include the genres field
                "score": {
                    "$meta": "vectorSearchScore"  # Include the search score
                }
            }
        }

        pipeline = [vector_search_stage, unset_stage, project_stage]

        # Execute the search
        results = self.collection.aggregate(pipeline)
        return list(results)

    def enhance_prompt(self, query_embedding: list):
        get_knowledge = self.vector_search(query_embedding, 10)
        print('vector_search_result:', get_knowledge)
        enhanced_prompt = ""
        for result in get_knowledge:
            enhanced_prompt += f"Title: {result.get('title', 'N/A')}, Plot: {result.get('fullplot', 'N/A')}\n"
        return enhanced_prompt
