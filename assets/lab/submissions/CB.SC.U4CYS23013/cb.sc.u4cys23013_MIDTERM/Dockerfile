FROM ubuntu:22.04

ENV ROLLNUMBER="CB.SC.U4CYS23013"
ENV NAME="Gautham"

LABEL EMAIL="cb.sc.u4cys23013@cb.students.amrita.edu"
LABEL "PRODUCTION VERSION"="1.0"

WORKDIR /midterm-exam

RUN apt-get update && \
    apt-get install -y python3 python3-pip mysql-server && \
    pip3 install flask mysql-connector-python && \
    apt-get clean

COPY database/init.sql .
COPY web/app.py .

RUN service mysql start && \
    mysql < init.sql

EXPOSE 5000

CMD ["sh", "-c", "service mysql start && python3 app.py"]