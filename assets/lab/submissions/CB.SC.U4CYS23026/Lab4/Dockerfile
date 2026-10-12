# Use official Python image
FROM python:3.12-slim

# Author information
LABEL author="Mithunn"

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install database connector package
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Database environment variables
ENV DB_HOST=localhost
ENV DB_PORT=5432
ENV DB_USER=admin
ENV DB_PASSWORD=password
ENV DB_NAME=testdb

# Expose application port
EXPOSE 8080

# Run the application
CMD ["python", "app.py"]