# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY scraper.py .

# Set environment variable
ENV TARGET_URL=https://news.ycombinator.com

# Expose port 8080
EXPOSE 8080

# Run the scraper
CMD ["python", "scraper.py"]