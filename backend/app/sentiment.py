from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re

def preprocess_text(text):
    # Remove URLs, numbers, and extra spaces
    text = re.sub(r'http\S+', '', text)  # Remove URLs
    text = re.sub(r'\d+', '', text)      # Remove numbers
    text = re.sub(r'\s+', ' ', text)     # Remove extra spaces
    text = text.strip()
    return text
analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(text: str):
    # Preprocess the input text
    text = preprocess_text(text)
    
    # Perform sentiment analysis using VADER
    score = analyzer.polarity_scores(text)
    compound = score['compound']
    
    # Determine sentiment based on the compound score
    sentiment = (
        'positive' if compound >= 0.05
        else 'negative' if compound <= -0.05
        else 'neutral'
    )
    
    return sentiment, compound