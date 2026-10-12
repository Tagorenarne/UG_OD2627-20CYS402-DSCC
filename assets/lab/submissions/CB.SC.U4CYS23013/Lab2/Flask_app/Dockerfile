# Base Image
FROM python:3.13-slim

# Maintainer
LABEL maintainer="Gautham"
LABEL email="gauthamram57@gmail.com"

# Install packages
RUN apt-get update && \
    apt-get install -y curl nano && \
    apt-get clean

# Environment Variable
ENV APP_NAME="DSCC-Lab2-flaskappdockerimage"

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
y"]
