FROM python:3.11-slim

WORKDIR /app

COPY client.py .

ENV PYTHONUNBUFFERED=1

EXPOSE 5001

CMD ["python", "client.py"]