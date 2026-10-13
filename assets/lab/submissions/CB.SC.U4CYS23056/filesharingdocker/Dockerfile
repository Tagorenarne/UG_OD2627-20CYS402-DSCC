# Base Image
FROM python:3.12-slim

# Environment Variables
ENV APP_ENV=production
ENV APP_PORT=8000
ENV UPLOAD_DIR=/app/uploads

# Working Directory
WORKDIR /app

# Copy dependency file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY server.py .
COPY config.json .
COPY README.md .
COPY uploads/ ./uploads/

# Expose application port
EXPOSE 8000

# Start the application
CMD ["python", "server.py"]