FROM python:3.11-slim

WORKDIR /app

RUN pip install python-dateutil

COPY server.py .
COPY client.py .

CMD ["python", "server.py"]