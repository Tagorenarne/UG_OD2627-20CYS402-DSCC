# Use Python image
FROM python:3.10-slim

# Working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install MySQL connector
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Database environment variables
ENV DB_HOST=host.docker.internal
ENV DB_PORT=3306
ENV DB_USER=root
ENV DB_PASSWORD=
ENV DB_NAME=college

# Expose port
EXPOSE 8080

# Run application
CMD ["python","app.py"]