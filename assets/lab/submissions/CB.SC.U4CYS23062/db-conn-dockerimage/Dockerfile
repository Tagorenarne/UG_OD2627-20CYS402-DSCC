
FROM python:3.10-slim


WORKDIR /app


COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt


COPY app.py .


ENV DB_HOST=localhost
ENV DB_PORT=3306
ENV DB_USER=root
ENV DB_PASSWORD=
ENV DB_NAME=testdb


ENV HOST=0.0.0.0
ENV PORT=8080


EXPOSE 8080


CMD ["python", "app.py"]