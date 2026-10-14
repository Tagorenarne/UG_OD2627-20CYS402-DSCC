FROM python:3.11-slim

WORKDIR /app

RUN pip install flask

COPY master.py .

EXPOSE 5000

CMD ["python", "master.py"]
