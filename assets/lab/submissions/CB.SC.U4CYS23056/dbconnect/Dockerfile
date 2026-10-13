FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

ENV DB_HOST=host.docker.internal
ENV DB_PORT=3306
ENV DB_USER=root
ENV DB_PASSWORD=
ENV DB_NAME=sample

EXPOSE 8080

CMD ["python", "app.py"]