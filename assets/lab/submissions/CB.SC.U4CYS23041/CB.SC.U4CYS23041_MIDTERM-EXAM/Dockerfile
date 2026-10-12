FROM ubuntu:24.04

LABEL maintainer="SANTHOSH THARUN S"
LABEL EMAIL="cb.sc.u4cys23041@cb.students.amrita.edu"
LABEL "PRODUCTION VERSION"="1.0"

ENV ROLLNUMBER="CB.SC.U4CYS23041"
ENV NAME="SANTHOSH THARUN S"

WORKDIR /midterm-exam

RUN apt-get update
RUN apt-get install -y apache2 php libapache2-mod-php php-mysql mariadb-server

RUN rm /var/www/html/index.html

RUN service mariadb start && mysql -e "CREATE DATABASE midterm_db;"
RUN service mariadb start && mysql -e "CREATE USER 'midterm_user'@'localhost' IDENTIFIED BY 'midterm_pass';"
RUN service mariadb start && mysql -e "GRANT ALL PRIVILEGES ON midterm_db.* TO 'midterm_user'@'localhost';"
RUN service mariadb start && mysql -e "USE midterm_db; CREATE TABLE users (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(50), password VARCHAR(50));"
RUN service mariadb start && mysql -e "USE midterm_db; INSERT INTO users (username,password) VALUES ('admin','admin123');"

COPY web/ /var/www/html/

EXPOSE 80

CMD ["bash", "-c", "service mariadb start && apachectl -D FOREGROUND"]
