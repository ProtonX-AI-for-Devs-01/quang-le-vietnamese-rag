from .mongo_client import MongoClient

# default number of top matches to retrieve from vector search
DEFAULT_SEARCH_LIMIT = 2

class RAG():
    def __init__(self, 
            mongodb_uri: str,
            db_name: str,
            db_collection: str,
            vector_index_name: str,
            keyword_index_name: str
        ):
        self.client = MongoClient().get_mongo_client(mongodb_uri)
        self.db = self.client[db_name] 
        self.collection = self.db[db_collection]
        self.vector_index_name = vector_index_name
        self.keyword_index_name = keyword_index_name

    def weighted_reciprocal_rank(self, doc_lists):
        """
        This is a modified version of the fuction in the langchain repo
        https://github.com/langchain-ai/langchain/blob/master/libs/langchain/langchain/retrievers/ensemble.py
        
        Perform weighted Reciprocal Rank Fusion on multiple rank lists.
        You can find more details about RRF here:
        https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf

        Args:
            doc_lists: A list of rank lists, where each rank list contains unique items.

        Returns:
            list: The final aggregated list of items sorted by their weighted RRF
                    scores in descending order.
        """
        c=60 #c comes from the paper
        weights=[1]*len(doc_lists) #you can apply weights if you like, here they are all the same, ie 1
        
        if len(doc_lists) != len(weights):
            raise ValueError(
                "Number of rank lists must be equal to the number of weights."
            )

        # Create a union of all unique documents in the input doc_lists
        all_documents = set()
        for doc_list in doc_lists:
            for doc in doc_list:
                all_documents.add(doc["content"])

        # Initialize the RRF score dictionary for each document
        rrf_score_dic = {doc: 0.0 for doc in all_documents}

        # Calculate RRF scores for each document
        for doc_list, weight in zip(doc_lists, weights):
            for rank, doc in enumerate(doc_list, start=1):
                rrf_score = weight * (1 / (rank + c))
                rrf_score_dic[doc["content"]] += rrf_score

        # Sort documents by their RRF scores in descending order
        sorted_documents = sorted(
            rrf_score_dic.keys(), key=lambda x: rrf_score_dic[x], reverse=True
        )

        # Map the sorted page_content back to the original document objects
        page_content_to_doc_map = {
            doc["content"]: doc for doc_list in doc_lists for doc in doc_list
        }
        sorted_docs = [
            page_content_to_doc_map[page_content] for page_content in sorted_documents
        ]

        return sorted_docs
   
    def hybrid_search(
        self,
        query: str, 
        query_embedding: list, 
        limit=DEFAULT_SEARCH_LIMIT):

        if query_embedding is None:
            return "Invalid query or embedding generation failed."

        # Define the vector search pipeline
        vector_search_stage = {
            "$vectorSearch": {
                "index": self.vector_index_name,
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
                "_id": 1,
                "title": 1,
                "content": 1,
                "price": 1,
                "image_urls": 1,
                "score": {
                    "$meta": "vectorSearchScore"  # Include the search score
                }
            }
        }

        pipeline = [vector_search_stage, unset_stage, project_stage]

        # Execute the search
        vector_results = self.collection.aggregate(pipeline)
        vector_results = list(vector_results) 
        
        #keyword search    
        keyword_results = self.collection.aggregate([{
                "$search": {
                    "index": self.keyword_index_name,
                    "text": {
                        "query": query,
                        "path": "title"
                    }
                }
            },
            { "$addFields" : { "score": { "$meta": "searchScore" } } },
            { "$limit": limit }
        ])
        keyword_results = list(keyword_results) 
        doc_lists = [vector_results, keyword_results]
        # Enforce that retrieved docs are the same form for each list in retriever_docs
        for i in range(len(doc_lists)):
            doc_lists[i] = [
                {
                    "_id": str(doc["_id"]),
                    "title": doc["title"],
                    "content": doc["content"],
                    "price": doc["price"],
                    "image_urls": doc["image_urls"], 
                    "score": doc["score"],
                }
                for doc in doc_lists[i]
            ]
        
        # apply rank fusion
        fused_documents = self.weighted_reciprocal_rank(doc_lists)
        return fused_documents


    def enhance_prompt(self, query: str, query_embedding: list):
        get_knowledge = self.hybrid_search(query, query_embedding, 10)
        print('hybrid_search_result:', get_knowledge)
        enhanced_prompt = ""
        for result in get_knowledge:
            enhanced_prompt += f"Title: {result.get('title', 'N/A')}, Content: {result.get('content', 'N/A')}, Price: {result.get('price', 'N/A')}, Image URLs: #{result.get('image_urls', 'N/A')}\n"
        return enhanced_prompt
