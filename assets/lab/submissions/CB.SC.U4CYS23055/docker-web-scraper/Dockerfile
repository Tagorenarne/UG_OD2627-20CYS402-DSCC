# Base Image
FROM python:3.10-slim

# Metadata
LABEL maintainer="Madhumitha"

# Environment Variable
ENV TARGET_URL=https://news.ycombinator.com

# Working Directory
WORKDIR /app

# Copy Files
COPY scraper.py .
COPY requirements.txt .
COPY README.md .

# Install Packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose Port
EXPOSE 8080

# Run Application
CMD ["python", "scraper.py"]