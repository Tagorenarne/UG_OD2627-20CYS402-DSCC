FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir python-dateutil

COPY server.py .
COPY client.py .

EXPOSE 8000
