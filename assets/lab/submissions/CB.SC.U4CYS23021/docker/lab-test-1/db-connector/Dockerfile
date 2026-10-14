# base image is this. its based on a stripped down version of debian 12
FROM python:3.12-slim 

# set the working directory 
WORKDIR /app

# copy the requrements and install them, which has psycopg2
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# copy the source code to the working directory 
COPY app.py .

# expose port 80
EXPOSE 8080

CMD ["python", "app.py"]
