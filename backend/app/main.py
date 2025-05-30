from fastapi import FastAPI
from app.database import Base, engine, SessionLocal
from app.news_fetcher import fetch_and_store_news
from app.models import Article  # Explicit import needed here
from sqlalchemy.orm import Session
from sqlalchemy import text
import os
print(f"Current working directory: {os.getcwd()}")
print(f"Files in current directory: {os.listdir('.')}")
print(f"Files in app directory: {os.listdir('./app')}")

# Log + create tables after importing model
print("Running create_all to initialize tables if they don't exist...")
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def root():
    return {"message": "News Sentiment API is running"}

@app.get("/db-status")
def db_status():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            data = [row[0] for row in result]
            return {"database": "connected", "result": data}
    except Exception as e:
        return {"database": "error", "details": str(e)}

@app.get("/fetch-news")
def fetch_news():
    fetch_and_store_news("AI", "AI")
    return {"message": "News fetched and stored."}

@app.get("/articles")
def get_articles():
    session: Session = SessionLocal()
    articles = session.query(Article).order_by(Article.published_at.desc()).limit(20).all()
    session.close()
    return articles
