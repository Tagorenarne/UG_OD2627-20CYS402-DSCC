FROM debian:bookworm-slim

LABEL EMAIL="rozariyomartin@gmail.com"
LABEL "PRODUCTION VERSION"="1.0"

ENV ROLLNUMBER="CB.SC.U4CYS23025"
ENV NAME="Martin Rozariyo I"

WORKDIR /midterm-exam

RUN apt-get update && apt-get install -y \
    apache2 \
    php \
    php-mysql \
    mariadb-server \
    mariadb-client \
    && a2dismod mpm_event \
    && a2enmod mpm_prefork \
    && a2enmod php8.2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY database/init.sql /midterm-exam/database/init.sql
COPY entrypoint.sh /midterm-exam/entrypoint.sh
RUN chmod +x /midterm-exam/entrypoint.sh

EXPOSE 80

CMD ["/midterm-exam/entrypoint.sh"]
