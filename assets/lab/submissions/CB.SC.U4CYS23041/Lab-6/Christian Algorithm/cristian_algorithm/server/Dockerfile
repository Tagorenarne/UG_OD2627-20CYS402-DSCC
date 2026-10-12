FROM python:3.11-alpine

WORKDIR /app

COPY server.py .

ENV PYTHONUNBUFFERED=1

EXPOSE 8888

CMD ["python", "server.py"]
