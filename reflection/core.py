from rag.mongo_client import MongoClient

OPEN_AI_ROLE_MAPPING = {
    "human": "user",
    "ai": "assistant"
}

class Reflection():
    def __init__(self,
        llm,
        mongodbUri: str,
        dbName: str,
        dbChatHistoryCollection: str,
        semanticCacheCollection: str,
    ):
        self.client = MongoClient().get_mongo_client(mongodbUri)
        self.db = self.client[dbName] 
        self.collection = self.db[dbChatHistoryCollection]
        self.semantic_cache_collection = self.db[semanticCacheCollection]
        self.llm = llm

    def chat(self, session_id: str, enhanced_message: str, original_message: str = '', cache_response: bool = False, query_embedding: list = []):
        system_prompt_content = """Bạn là một chatbot của cửa hàng hoa. Vai trò của bạn là hỗ trợ khách hàng trong việc tìm hiểu về các sản phẩm và dịch vụ của cửa hàng, cũng như tạo một trải nghiệm mua sắm dễ chịu và thân thiện. Bạn có thể trả lời các câu hỏi về loại hoa, dịch vụ giao hàng, và hướng dẫn chăm sóc hoa. Bạn cũng có thể trò chuyện với khách hàng về các chủ đề không liên quan đến sản phẩm như thời tiết, sở thích cá nhân, và những câu chuyện thú vị để tạo sự gắn kết. 
Hãy luôn giữ thái độ lịch sự và chuyên nghiệp. Nếu khách hàng hỏi về sản phẩm cụ thể, hãy cung cấp thông tin chi tiết và gợi ý các lựa chọn phù hợp. Nếu khách hàng trò chuyện về các chủ đề không liên quan đến sản phẩm, hãy tham gia vào cuộc trò chuyện một cách vui vẻ và thân thiện.
một số điểm chính bạn cần lưu ý:
1. Đáp ứng nhanh chóng và chính xác.
2. Giữ cho cuộc trò chuyện vui vẻ và thân thiện.
3. Cung cấp thông tin hữu ích về hoa và dịch vụ của cửa hàng.
4. Giữ cho cuộc trò chuyện mang tính chất hỗ trợ và giúp đỡ.
Hãy làm cho khách hàng cảm thấy được chào đón và quan tâm!"""
        system_prompt = [
            {
                "role": "system", 
                "content": system_prompt_content
            },
        ]
        human_prompt = [
            {
                "role": "user", 
                "content": enhanced_message
            },
        ]
        chat_session_query = { "SessionId": session_id }
        session_messages = self.collection.find(chat_session_query)
        formatted_session_messages = self.__construct_session_messages__(session_messages)
        messages = system_prompt + formatted_session_messages + human_prompt
        print(f"final messages: {messages}")
        response = self.llm.chat(messages)
        self.__record_human_prompt__(session_id, enhanced_message, original_message)
        self.__record_ai_response__(session_id, response)
        if cache_response:
            self.__cache_ai_response__(enhanced_message, original_message, response, query_embedding)

        return response.choices[0].message.content

    def __construct_session_messages__(self, session_messages: list):
        result = []
        for session_message in session_messages:
            print(f"session_message: {session_message}")
            print(f"session_message: {session_message['History']}")
            result.append({
                "role": OPEN_AI_ROLE_MAPPING[session_message['History']['type']],
                "content": session_message['History']['data']['content']
            })
        return result

    def __record_human_prompt__(self, session_id: str, enhanced_message: str, original_message: str):
        self.collection.insert_one({
            "SessionId": session_id,
            "History": {
                "type": "human",
                "data":  {
                    "type": "human",
                    "content": original_message,
                    "enhanced_content": enhanced_message,
                    "additional_kwargs": {},
                    "response_metadata": {},
                    "name": None,
                    "id": None,
                }
            }
        })
    
    def __record_ai_response__(self, session_id: str, response: dict):
        self.collection.insert_one({
            "SessionId": session_id,
            "History": {
                "type": "ai",
                "data":  {
                    "type": "ai",
                    "content": response.choices[0].message.content,
                    "enhanced_content": None,
                    "additional_kwargs": {},
                    "name": None,
                    "id": response.id,
                    "usage_metadata": {
                        "input_tokens": response.usage.prompt_tokens,
                        "output_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    },
                    "response_metadata": {
                        "usage": response.usage.to_json(),
	                    "model_name": response.model,
	                    "finish_reason": response.choices[0].finish_reason,
                        "logprobs": response.choices[0].logprobs
                    },
                }
            }
        })

    def __cache_ai_response__(self, enhanced_message: str, original_message: str, response: dict, query_embedding: list):
        # try a different embedding model for semantic cache, do we even need embedding? fuzzy search
        # try a different vector search algorithm
        # cache expiration based on TTL (1 week)
        # invalidate cache if the data source changes
        # invalidate cache if the embedding model changes
        embedding = query_embedding
        self.semantic_cache_collection.insert_one({
            "embedding": embedding,
            "text": [
                {
                    "type": "human",
                    "content": original_message,
                    "enhanced_content": enhanced_message,
                    "additional_kwargs": {},
                    "response_metadata": {},
                    "name": None,
                    "id": None,
                }
            ],
            "llm_string": {
                "model_name": response.model,
                "name": "ChatOpenAI"
            },
            "return_val": [
                {
                    "type": "ai",
                    "content": response.choices[0].message.content,
                    "enhanced_content": None,
                    "additional_kwargs": {},
                    "name": None,
                    "id": response.id,
                    "usage_metadata": {
                        "input_tokens": response.usage.prompt_tokens,
                        "output_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    },
                    "response_metadata": {
                        "usage": response.usage.to_json(),
                        "model_name": response.model,
                        "finish_reason": response.choices[0].finish_reason,
                        "logprobs": response.choices[0].logprobs
                    },
                }
            ]
        })



