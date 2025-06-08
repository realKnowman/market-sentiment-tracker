AI-Powered Market Sentiment Tracker

A modular, scalable backend and dashboard application to track, analyze, and visualize real-time sentiment from news articles across multiple niche sectors like AI, Electric Vehicles, FinTech, and more.

 Features

    � Ingests real-time news articles using NewsAPI with dynamic multi-sector keyword tracking via JSON config.
      
    � Applies NLP sentiment analysis (VADER and BERT) to classify news as positive, neutral, or negative.
      
    � Stores processed articles with sentiment scores in PostgreSQL.
      
    � Interactive Streamlit dashboard for multi-sector sentiment visualization, trends, and top headlines.
      
    � PDF report generation with embedded charts for offline review.
      
    � Containerized with Docker and orchestrated via Docker Compose for consistent multi-service deployment.
      
    � Robust handling of empty or missing data scenarios.

 Tech Stack

    � Backend: Python, FastAPI, SQLAlchemy
      
    � Database: PostgreSQL
      
    � NLP: VADER, HuggingFace BERT
      
    � Dashboard: Streamlit, Plotly
      
    � Containerization: Docker, Docker Compose
      
    � APIs: NewsAPI

Getting Started

    � Prerequisites

Python 3.11+

Docker and Docker Compose installed

NewsAPI key (get from newsapi.org)

    � Installation

Clone the repository:

git clone https://github.com/yourusername/market-sentiment-tracker.git
cd market-sentiment-tracker
Create .env file and add your NewsAPI key:

NEWSAPI_KEY=your_api_key_here - users must provide their own API keys as environment variables.
DATABASE_URL=postgresql://postgres:postgres@sentiment-postgres:5432/newsdb

Build and start the Docker containers:

docker-compose up -�build

Access the API and dashboard:

API: http://localhost:8000
Dashboard: http://localhost:8501

    � Usage

Use the /fetch-news endpoint to fetch and store latest news articles for all configured sectors.

Explore the Streamlit dashboard to filter sectors, view sentiment distributions, trends, and download PDF reports.

    � Configuration

The sectors and keywords for news tracking are defined in sectors_keywords.json. You can add/remove sectors or keywords to customize the tracking.

Example:

json
Copy
{
  "AI": ["AI", "artificial intelligence", "ChatGPT"],
  "EV": ["electric vehicles", "Tesla", "battery"]
}

    � Demo Video



    � Contributing

Contributions welcome! Please open issues or pull requests to improve features, fix bugs, or add new sectors.

    � Contact
Nouman Rasool � rasoolnouman10@gmail.com � https://www.linkedin.com/in/noumanrasool/
