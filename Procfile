# backend/Procfile

web: cd backend && python -m nltk.downloader -d /app/nltk_data punkt stopwords vader_lexicon && uvicorn main:app --host=0.0.0.0 --port=$PORT

