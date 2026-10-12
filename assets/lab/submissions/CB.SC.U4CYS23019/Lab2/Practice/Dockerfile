FROM python:3.12-slim

LABEL maintainer="Jai Aditya"

RUN apt-get update && \
    apt-get install -y curl nano && \
    apt-get clean

ENV APP_ENV=production
ENV APP_PORT=8000
ENV UPLOAD_DIR=/app/uploads

WORKDIR /app

COPY server.py .
COPY requirements.txt .
COPY config.json .
COPY README.md .
COPY uploads/ uploads/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "server.py"]