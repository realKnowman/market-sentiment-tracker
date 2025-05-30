import requests
from app.sentiment import analyze_sentiment
from app.database import SessionLocal
from app.models import Article
import os
import json

API_KEY = os.getenv("NEWS_API_KEY")
BASE_URL = "https://newsapi.org/v2/everything"

# Load sectors and keywords from the JSON file
with open('app/sectors_keywords.json') as f:
    sectors_keywords = json.load(f)


def fetch_and_store_news():
    session = SessionLocal()
    
    # Loop through each sector and its associated keywords
    for sector, keywords in sectors_keywords.items():
        for keyword in keywords:
            print(f"Fetching news for sector: {sector} with keyword: {keyword}")  # Debug print

            # Construct URL with query parameters (keywords)
            url = f"{BASE_URL}?q={keyword}&language=en&sortBy=publishedAt&apiKey={API_KEY}"
            response = requests.get(url)
            data = response.json()
            
            articles = data.get("articles", [])
            
            if not articles:
                print(f"No articles found for keyword: {keyword} under sector: {sector}")  # Debug print
                continue  # If no articles, skip to the next keyword/sector

            print(f"Received {len(articles)} articles from NewsAPI for keyword: {keyword}")  # Debug print

            # Store articles in the database
            for item in articles:
                title = item["title"]
                description = item.get("description") or ""
                text = f"{title}. {description}"
                sentiment, score = analyze_sentiment(text)

                article = Article(
                    title=title,
                    description=description,
                    published_at=item["publishedAt"],
                    sentiment=sentiment,
                    sentiment_score=score,
                    source=item["source"]["name"],
                    url=item["url"],
                    sector=sector  # Store sector info per article
                )
                session.add(article)

            session.commit()  # Commit to insert into DB
            print(f"Stored {len(articles)} articles in the database under sector: {sector}")  # Debug print
    
    session.close()
