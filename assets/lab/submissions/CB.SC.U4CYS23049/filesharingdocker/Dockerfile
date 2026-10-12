# Base Image
FROM python:3.12-slim

# Maintainer
LABEL maintainer="<<Revanth>>"
LABEL email="<<revanthtalasila41@gmail.com>>"

# Install system packages
RUN apt-get update && \
    apt-get install -y curl nano && \
    apt-get clean

# Environment Variables
ENV APP_ENV=production
ENV APP_PORT=8000
ENV UPLOAD_DIR=/app/uploads

# Working Directory
WORKDIR /app

# Copy files and directories
COPY server.py .
COPY requirements.txt .
COPY config.json .
COPY README.md .
COPY uploads/ ./uploads/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Port
EXPOSE 8000

# Run application automatically
CMD ["python", "server.py"]