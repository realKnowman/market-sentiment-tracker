from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(text: str):
    score = analyzer.polarity_scores(text)
    compound = score['compound']
    sentiment = (
        'positive' if compound >= 0.05
        else 'negative' if compound <= -0.05
        else 'neutral'
    )
    return sentiment, compound