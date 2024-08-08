# text_processor.py

import re
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
from textstat import flesch_reading_ease

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('vader_lexicon')

def process_text(text: str) -> dict:
    # Remove special characters and digits
    clean_text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # Convert to lowercase
    clean_text = clean_text.lower()
    
    # Tokenize into sentences and words
    sentences = sent_tokenize(text)
    words = word_tokenize(clean_text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word not in stop_words]
    
    # Calculate readability score
    readability_score = flesch_reading_ease(text)
    
    # Perform sentiment analysis
    sia = SentimentIntensityAnalyzer()
    sentiment_scores = sia.polarity_scores(text)
    sentiment = 'positive' if sentiment_scores['compound'] > 0 else 'negative' if sentiment_scores['compound'] < 0 else 'neutral'
    
    return {
        'processed_text': ' '.join(filtered_words),
        'sentence_count': len(sentences),
        'word_count': len(words),
        'readability_score': readability_score,
        'sentiment': sentiment
    }