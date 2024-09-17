from rag.mongo_client import MongoClient

# default number of top matches to retrieve from vector search
DEFAULT_SEARCH_LIMIT = 4
CACHE_HIT_THRESHOLD = 0.85

class SemanticCache():
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

    """
    Perform a vector search in the MongoDB collection based on the user query

    Args:
    user_query (str): The user's query string

    Returns:
    list: A list of matching documents
    """
    def vector_search(self, query_embedding: list):
        # Define the vector search pipeline
        vector_search_stage = {
            "$vectorSearch": {
                "index": self.index_name,
                "queryVector": query_embedding,
                "path": "embedding",
                "numCandidates": 150,  # Number of candidate matches to consider
                "limit": DEFAULT_SEARCH_LIMIT  # Return top matches
            }
        }

        unset_stage = {
            "$unset": "embedding" 
        }

        project_stage = {
            "$project": {
                "_id": 0,  # Exclude the _id field
                "text": 1,  # Include the text field
                "return_val": 1,  # Include the return_val field
                "score": {
                    "$meta": "vectorSearchScore"  # Include the search score
                }
            }
        }
        pipeline = [vector_search_stage, unset_stage, project_stage]

        # Execute the cache search
        results = self.collection.aggregate(pipeline)
        return list(results)

    def retrieve_cached_result(self, query_embedding):
        cache_results = self.vector_search(query_embedding)
        print('cache_results:', list(map(lambda x: { "content": x['text'][0]['content'], "score": x['score'] }, cache_results)))
        if len(cache_results) > 0 and cache_results[0]['score'] > CACHE_HIT_THRESHOLD:
            return cache_results[0]['return_val'][0]['content']
        else:
            return None        
