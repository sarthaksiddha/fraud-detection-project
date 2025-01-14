# Use official Python runtime as base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ src/
COPY config/ config/
COPY models/ models/

# Set environment variables
ENV PYTHONPATH=/app
ENV KAFKA_BOOTSTRAP_SERVERS=kafka:9092
ENV MONGODB_HOST=mongodb
ENV MONGODB_PORT=27017

# Expose port for API
EXPOSE 8000

# Command to run the application
CMD ["python", "src/api/api_server.py"]