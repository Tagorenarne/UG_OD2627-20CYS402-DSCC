# Base Image
FROM python:3.12-slim

# Maintainer
LABEL maintainer="Your Name"
LABEL email="your_email@example.com"

# Install packages
RUN apt-get update && \
    apt-get install -y curl nano && \
    apt-get clean

# Environment Variables
ENV APP_ENV=production
ENV APP_PORT=8000
ENV UPLOAD_DIR=/app/uploads

# Working Directory
WORKDIR /app

# Copy application files
COPY server.py .
COPY requirements.txt .
COPY config.json .
COPY README.md .
COPY uploads ./uploads

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose application port
EXPOSE 8000

# Start application
CMD ["python", "server.py"]