# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-ben \
    poppler-utils \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Download Bengali language data
RUN wget -O /usr/share/tesseract-ocr/4.00/tessdata/ben.traineddata \
    https://github.com/tesseract-ocr/tessdata/raw/main/ben.traineddata

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p data cache

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the application
CMD ["streamlit", "run", "app_deploy.py", "--server.port=8501", "--server.address=0.0.0.0"]
