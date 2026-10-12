FROM python:3.12-slim

LABEL maintainer="Hiba Leeyakath S"
LABEL email="hibaleeyakath@email.com"

RUN apt-get update && \
    apt-get install -y curl nano && \
    apt-get clean

ENV APP_NAME="DSCC-Lab2-flaskappdockerimage"

WORKDIR /app

COPY app.py .
COPY requirements.txt .
COPY README.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]
