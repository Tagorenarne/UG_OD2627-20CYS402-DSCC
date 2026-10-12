FROM python:3.11-slim

WORKDIR /app

COPY client.py .

ENV CLIENT_ID=client
ENV CLOCK_OFFSET=0

CMD ["python", "client.py"]