#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  CREATE TABLE IF NOT EXISTS articles (
      id SERIAL PRIMARY KEY,
      title VARCHAR,
      description VARCHAR,
      published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      sentiment VARCHAR,
      sentiment_score FLOAT,
      source VARCHAR,
      url VARCHAR,
      sector VARCHAR
  );
EOSQL
