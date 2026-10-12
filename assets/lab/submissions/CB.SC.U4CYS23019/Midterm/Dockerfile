FROM python:3.11-slim

ENV ROLLNUMBER=CB.SC.U4CYS23019
ENV NAME="Jai Aditya"

LABEL EMAIL="cb.sc.u4cys23019@cb.students.amrita.edu"
LABEL PRODUCTION_VERSION="1.0"

WORKDIR /midterm-exam

RUN apt-get update && \
    apt-get install -y apache2

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY web/ ./web

EXPOSE 5000

CMD ["python","web/app.py"]
