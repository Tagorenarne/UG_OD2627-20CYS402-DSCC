# 1. Use an appropriate official Python base image
FROM python:3.12-slim

# 2. Maintainer
LABEL maintainer="Karun A.T."
LABEL email="cb.sc.u4cys23023@cb.students.amrita.edu"

# 3. Configure the required environment variables
ENV APP_ENV="production" \
    APP_PORT="8000" \
    UPLOAD_DIR="/app/uploads"

# 4. Set the working directory
WORKDIR /app

# 5. Copy required files and the uploads directory
COPY server.py .
COPY requirements.txt .
COPY config.json .
COPY README.md .
COPY uploads/ ./uploads/

# 6. Install all Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 7. Expose the application on port 8000
EXPOSE 8000

# 8. Start automatically when the container is executed
CMD ["python", "server.py"]