# Base Image
FROM python:3.12-slim

# Maintainer Information
LABEL maintainer="Madhumitha"

# Environment Variables
ENV APP_ENV=production
ENV APP_PORT=8000
ENV UPLOAD_DIR=/app/uploads

# Working Directory
WORKDIR /app

# Copy Files
COPY server.py .
COPY requirements.txt .
COPY config.json .
COPY README.md .
COPY uploads/ ./uploads/

# Install Python Packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose Port
EXPOSE 8000

# Start Application
CMD ["python", "server.py"]