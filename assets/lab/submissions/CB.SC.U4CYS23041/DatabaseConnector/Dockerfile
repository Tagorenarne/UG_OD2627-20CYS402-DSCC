# Use official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy dependency file
COPY requirements.txt .

# Install required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY app.py .

# Database environment variables
# If MySQL is running on your host machine (Docker Desktop):
ENV DB_HOST=host.docker.internal
ENV DB_PORT=3306
ENV DB_USER=dockeruser
ENV DB_PASSWORD=password123
ENV DB_NAME=company
# Expose application port
EXPOSE 8080

# Run the application
CMD ["python", "app.py"]
