FROM python:3.12-slim

LABEL EMAIL="CB.SC.U4CYS23017@cb.amrita.edu"
LABEL "PRODUCTION VERSION"="1.0"

ENV ROLLNUMBER="CB.SC.U4CYS23017"
ENV NAME="Hiba Leeyakath S"

WORKDIR /midterm-exam

RUN apt-get update && \
    apt-get install -y postgresql postgresql-contrib && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir flask psycopg2-binary

COPY database /midterm-exam/database
COPY web /midterm-exam/web
COPY start.sh /start.sh

RUN chmod +x /start.sh

EXPOSE 5000

CMD ["/start.sh"]
