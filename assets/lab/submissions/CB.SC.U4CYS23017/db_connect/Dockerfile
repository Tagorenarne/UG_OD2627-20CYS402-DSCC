# Use official Python image
FROM python:3.12-slim

# Working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install packages
RUN pip install --no-cache-dir -r requirements.txt

# Database environment variables
ENV DB_HOST=localhost
ENV DB_PORT=5432
ENV DB_USER=postgres
ENV DB_PASSWORD=password
ENV DB_NAME=testdb

# Copy application
COPY app.py .

# Expose application port
EXPOSE 8080

# Run application
CMD ["python", "app.py"]
