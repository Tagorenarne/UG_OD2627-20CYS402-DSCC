FROM python:3.12-slim

ENV ROLLNUMBER=CB.SC.U4CYS23014
ENV NAME=Gouthaman

LABEL EMAIL="cb.sc.u4cys23014@cb.students.amrita.edu"
LABEL PRODUCTION_VERSION="1.0"

WORKDIR /midterm-exam

RUN apt-get update && \
    apt-get install -y mariadb-server mariadb-client && \
    pip install flask mysql-connector-python && \
    rm -rf /var/lib/apt/lists/*

COPY web /midterm-exam/web
COPY database /midterm-exam/database

RUN chmod +x /midterm-exam/database/abc.sh

EXPOSE 5000

CMD ["/midterm-exam/database/abc.sh"]
