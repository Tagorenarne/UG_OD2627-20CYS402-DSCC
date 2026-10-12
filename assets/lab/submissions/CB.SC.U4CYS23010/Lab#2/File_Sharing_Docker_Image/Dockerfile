# 1. Use an official Python base image
FROM python:3.12-slim

# 2. Configure environment variables
ENV APP_ENV="production" \
    APP_PORT="8000" \
    UPLOAD_DIR="/app/uploads"

# 3. Set the working directory
WORKDIR /app

# 4. Copy files and directories from the host to the image
COPY server.py .
COPY requirements.txt .
COPY config.json .
COPY README.md .
COPY uploads/ ./uploads/

# 5. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6. Expose the application port
EXPOSE 8000

# 7. Start the application automatically
CMD ["python", "server.py"]
