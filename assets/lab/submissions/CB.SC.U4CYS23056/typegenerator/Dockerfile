# Use a lightweight official Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the Python script into the container
COPY app.py .

# Unbuffer Python output so logs print to console correctly
ENV PYTHONUNBUFFERED=1

# Run the script when the container starts
CMD ["python", "app.py"]