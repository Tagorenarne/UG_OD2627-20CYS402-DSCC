FROM python:3.12-slim

ENV ROLLNUMBER="CB.SC.U4CYS23056"
ENV NAME="SAIRAGHUNANDHAN"

LABEL EMAIL="CB.SC.U4CYS23056@CB.STUDENTS.AMRITA.EDU"
LABEL "PRODUCTION VERSION"="1.0"

WORKDIR /midterm-exam

RUN apt-get update && \
    apt-get install -y mariadb-server && \
    rm -rf /var/lib/apt/lists/*

COPY web/requirements.txt .
RUN pip install -r requirements.txt

COPY web/app.py .
COPY database/init.sql .

EXPOSE 5000

CMD ["python", "app.py"]