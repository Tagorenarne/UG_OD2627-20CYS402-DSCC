
FROM python:3.12-slim


ENV APP_ENV="production" \
    APP_PORT="8000" \
    UPLOAD_DIR="/app/uploads"


WORKDIR /app


COPY server.py .
COPY requirements.txt .
COPY config.json .
COPY README.md .
COPY uploads/ ./uploads/


RUN pip install --no-cache-dir -r requirements.txt


EXPOSE 8000


CMD ["python", "server.py"]
