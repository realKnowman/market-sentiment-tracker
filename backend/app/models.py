from sqlalchemy import Column, Integer, String, DateTime, Float
from app.database import Base
from datetime import datetime

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    published_at = Column(DateTime, default=datetime.utcnow)
    sentiment = Column(String)
    sentiment_score = Column(Float)
    source = Column(String)
    url = Column(String)
    sector = Column(String)