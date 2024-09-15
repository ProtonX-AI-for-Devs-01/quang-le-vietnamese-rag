## Vietnames RAG for an online flower shop ##

### Running in local ###
- Create an `.env` file and populate these ENV variables needed as required in  `.env.example`
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

- Run streamlit app to access chatbot:
```
streamlit run Hello.py
```
