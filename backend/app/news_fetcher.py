import requests
from app.models import Article
from app.database import SessionLocal
from app.sentiment import analyze_sentiment
import os
import time
import json
import logging
# Load sectors and keywords from JSON
with open('app/sectors_keywords.json') as f:
    sectors_keywords = json.load(f)

API_KEY = os.getenv("NEWS_API_KEY")
BASE_URL = "https://newsapi.org/v2/everything"

def fetch_and_store_news():
    session = SessionLocal()
    
    # Loop through each sector and its associated keywords
    for sector, keywords in sectors_keywords.items():
        for keyword in keywords:
            logging.info(f"Fetching news for sector: {sector} with keyword: {keyword}")  # Debug print

            # Construct URL with query parameters (keywords)
            url = f"{BASE_URL}?q={keyword}&language=en&sortBy=publishedAt&apiKey={API_KEY}"
            try:
                response = requests.get(url)
                response.raise_for_status()  # Will raise an exception for HTTP errors
                data = response.json()
                
                articles = data.get("articles", [])
                
                if not articles:
                    logging.info(f"No articles found for keyword: {keyword} under sector: {sector}")  # Debug print
                    continue  # If no articles, skip to the next keyword/sector

                logging.info(f"Received {len(articles)} articles from NewsAPI for keyword: {keyword}")  # Debug print

                # Store articles in the database
                for item in articles:
                    title = item["title"]
                    description = item.get("description") or ""
                    text = f"{title}. {description}"
                    sentiment, score = analyze_sentiment(title)

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

                session.commit()  # Commit to insert into DB after processing all articles for the keyword
                logging.info(f"Stored {len(articles)} articles in the database under sector: {sector}")  # Debug print
                
            except requests.exceptions.RequestException as e:
                logging.error(f"Error fetching data for keyword '{keyword}' in sector '{sector}': {e}")
                continue  # Skip to the next keyword/sector
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
                continue  # Skip to the next keyword/sector

            # Optionally, you can add a small delay to avoid hitting API rate limits
            time.sleep(1)

    session.close()
