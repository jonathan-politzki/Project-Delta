import re
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
import nltk

nltk.download('punkt')
nltk.download('stopwords')

def process_text(text: str) -> str:
    # Remove special characters and digits
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # Convert to lowercase
    text = text.lower()
    
    # Tokenize into sentences
    sentences = sent_tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    processed_sentences = [
        ' '.join([word for word in sentence.split() if word not in stop_words])
        for sentence in sentences
    ]
    
    return ' '.join(processed_sentences)
