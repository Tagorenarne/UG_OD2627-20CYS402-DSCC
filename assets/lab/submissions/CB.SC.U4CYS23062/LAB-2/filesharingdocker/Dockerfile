# Base Image
FROM python:3.12-slim

# Maintainer Information
LABEL maintainer="Vibhika"
LABEL email="vibhika.appaka@gmail.com"

# Install required packages
RUN apt-get update && \
    apt-get install -y curl nano && \
    apt-get clean

# Environment Variables
ENV APP_ENV=production
ENV APP_PORT=8000
ENV UPLOAD_DIR=/app/uploads

# Working Directory
WORKDIR /app

# Copy files
COPY Server.py .
COPY requirements.txt .
COPY config.json .
COPY README.txt .
COPY uploads ./uploads

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose Port
EXPOSE 8000

# Run Application
CMD ["python", "server.py"]