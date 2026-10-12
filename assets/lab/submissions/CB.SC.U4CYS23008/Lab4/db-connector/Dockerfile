# ---- Base image: official slim Python image ----
FROM python:3.11-slim

# ---- Set working directory inside container ----
WORKDIR /app

# ---- Copy and install the MySQL connector library ----
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Copy the application source code ----
COPY app.py .

# ---- Database connection environment variables (XAMPP MySQL) ----
ENV DB_HOST=host.docker.internal
ENV DB_PORT=3306
ENV DB_USER=root
ENV DB_PASSWORD=
ENV DB_NAME=testdb

# ---- Application host/port ----
ENV APP_HOST=0.0.0.0
ENV APP_PORT=8080

# ---- Expose the app port ----
EXPOSE 8080

# ---- Run the connector script ----
CMD ["python", "app.py"]