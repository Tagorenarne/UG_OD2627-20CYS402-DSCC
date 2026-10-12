FROM python:3.11-slim

ENV ROLLNUMBER=CB.SC.U4CYS23015
ENV NAME="Haemanth VJ"

LABEL EMAIL="cb.sc.u4cys23015@cb.students.amrita.edu"
LABEL PRODUCTION_VERSION="1.0"

WORKDIR /midterm-exam

# install database and dependencies
RUN apt-get update && apt-get install -y mariadb-server mariadb-client && rm -rf /var/lib/apt/lists/*

COPY web/requirements.txt /midterm-exam/web/requirements.txt
RUN pip install -r /midterm-exam/web/requirements.txt

COPY database/ /midterm-exam/database/
COPY web/ /midterm-exam/web/

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 5000

CMD ["/entrypoint.sh"]
