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

import logging
import requests
import time
from app.database import SessionLocal
from app.models import Article
from app.sentiment import analyze_sentiment

logging.basicConfig(level=logging.INFO)

def fetch_and_store_news():
    session = SessionLocal()

    # Loop through each sector and its associated keywords
    for sector, keywords in sectors_keywords.items():
        # Dynamically create the query with 'AND' for each sector's keywords
        query = " AND ".join(keywords)  # Join all keywords with 'AND'
        logging.info(f"Fetching news for sector: {sector} with query: {query}")

        # Construct URL with query parameters (keywords joined with 'AND')
        url = f"{BASE_URL}?q={query}&language=en&sortBy=publishedAt&apiKey={API_KEY}"

        try:
            response = requests.get(url)
            response.raise_for_status()  # Will raise an exception for HTTP errors
            data = response.json()

            articles = data.get("articles", [])

            if not articles:
                logging.info(f"No articles found for sector: {sector} with query: {query}")
                continue  # If no articles, skip to the next sector

            logging.info(f"Received {len(articles)} articles for sector: {sector} with query: {query}")

            # Filter articles by sector relevance
            filtered_articles = []
            for item in articles:
                if any(kw.lower() in item["title"].lower() or kw.lower() in item["description"].lower() for kw in keywords):
                    filtered_articles.append(item)

            # Store articles in the database
            for item in filtered_articles:
                logging.info(f"Processing article: {item['title']}")  # Debug print
                title = item["title"]
                description = item.get("description", "")
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

            session.commit()  # Commit to insert into DB after processing all articles for the sector
            logging.info(f"Stored {len(articles)} articles in the database under sector: {sector}")

        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching data for sector '{sector}' with query '{query}': {e}")
            continue  # Skip to the next sector
        except Exception as e:
            logging.error(f"Unexpected error for sector '{sector}' with query '{query}': {e}")
            continue  # Skip to the next sector

        # Optionally, you can add a small delay to avoid hitting API rate limits
        time.sleep(1)

    session.close()
    logging.info("Finished fetching and storing news articles.")