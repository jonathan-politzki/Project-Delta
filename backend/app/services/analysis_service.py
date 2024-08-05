from collections import Counter
from nltk import pos_tag, word_tokenize
import nltk

nltk.download('averaged_perceptron_tagger')

def generate_analysis(insights: str, processed_text: dict) -> dict:
    # Extract key themes (most common nouns)
    words = word_tokenize(processed_text['processed_text'])
    tagged_words = pos_tag(words)
    nouns = [word.lower() for word, pos in tagged_words if pos.startswith('NN')]
    key_themes = [theme for theme, _ in Counter(nouns).most_common(5)]
    
    # Determine writing style based on sentence length and word choice
    avg_sentence_length = processed_text['word_count'] / processed_text['sentence_count']
    if avg_sentence_length > 20:
        writing_style = "Complex and detailed"
    elif avg_sentence_length < 10:
        writing_style = "Concise and to-the-point"
    else:
        writing_style = "Balanced and clear"
    
    return {
        "insights": insights,
        "writing_style": writing_style,
        "key_themes": key_themes,
        "readability_score": processed_text['readability_score'],
        "sentiment": processed_text['sentiment']
    }
