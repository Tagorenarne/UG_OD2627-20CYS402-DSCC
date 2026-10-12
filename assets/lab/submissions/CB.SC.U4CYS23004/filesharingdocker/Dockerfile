# Base Image
FROM python:3.12-slim

# Install packages
RUN apt-get update && \
    apt-get install -y curl nano && \
    apt-get clean

# Environment Variable
ENV APP_ENV=production
ENV APP_PORT=8000
ENV UPLOAD_DIR=/app/uploads

# Working Directory
WORKDIR /app

# Copy files
COPY server.py .
COPY requirements.txt .
COPY config.json .
COPY README.md .
COPY uploads/ ./uploads/

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose Port
EXPOSE 8000

# Run application
CMD ["python", "server.py"]