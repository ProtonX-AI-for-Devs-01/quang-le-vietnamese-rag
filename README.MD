## Vietnames RAG powered AI chatbot for an online flower shop ##

<img width="717" alt="Screen Shot 2024-09-26 at 12 50 05 AM" src="https://github.com/user-attachments/assets/cfb152d4-38a8-4c15-95b1-90ce6e6ab70d">

### Running in local ###
- Create an `.env` file and populate these ENV variables needed as required in  `.env.example`
- for `VECTOR_INDEX_NAME`, create a MongoDB Atlas vectorSearch index for the `DB_COLLECTION` collection:
```
{
  "fields": [
    {
      "numDimensions": 768,
      "path": "embedding",
      "similarity": "cosine",
      "type": "vector"
    }
  ]
}
```
- for `KEYWORD_INDEX_NAME`, create a MongoDB Atlas search index for the `DB_COLLECTION` collection:
```
{
  "mappings": {
    "dynamic": false,
    "fields": {
      "title": [
        {
          "type": "string"
        }
      ]
    }
  }
}
```

- for `SEMANTIC_CACHE_INDEX_NAME`, create a MongoDB Atlas vectorSearch index for the `SEMANTIC_CACHE_COLLECTION` collection:
```
{
  "fields": [
    {
      "numDimensions": 768,
      "path": "embedding",
      "similarity": "euclidean",
      "type": "vector"
    },
    {
      "path": "llm_string",
      "type": "filter"
    }
  ]
}
```

- Install dependencies:
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

- Run web scraper, `all_urls.json` and  `output.json` files will be generated:
```
python web_scraper.py
```

- Load documents and their embeddings into MongoDB:
```
python load_document.py
```

- Start the server, the server will run from http://localhost:5000 by default:
```
python serve.py
```

- Run streamlit app to access chatbot:
```
streamlit run Hello.py
```

- To run test suite:
```
python -m unittest
```
