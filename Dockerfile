FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (required for some NLP and database libs)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download default spaCy model during build
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY src/ ./src/

ENV PYTHONPATH=/app
