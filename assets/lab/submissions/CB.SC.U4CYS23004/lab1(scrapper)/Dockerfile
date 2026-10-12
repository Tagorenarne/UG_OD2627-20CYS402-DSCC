FROM python:3.10-slim

WORKDIR /app

RUN pip install --no-cache-dir requests beautifulsoup4

COPY scrapper.py .

ENV TARGET_URL=https://news.ycombinator.com

EXPOSE 8080

CMD ["python", "scrapper.py"]