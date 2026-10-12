FROM python:3.11-slim

WORKDIR /app

COPY master.py .

ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["python", "master.py"]