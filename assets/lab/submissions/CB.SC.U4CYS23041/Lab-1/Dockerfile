# Base Image
FROM python:3.12-slim

# Maintainer
LABEL maintainer="<<Your Name>>"
LABEL email="<<Your Email>>"

# Install packages
RUN apt-get update && \
    apt-get install -y curl nano && \
    apt-get clean

# Environment Variable
APP_ENV=production
APP_PORT=8000
UPLOAD_DIR=/app/uploads


# Working Directory
WORKDIR /app

# Copy files
COPY app.py .
COPY requirements.txt .
COPY README.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose Port
EXPOSE 5000

# Run application
CMD ["python", "app.py"]
