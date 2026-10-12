CREATE DATABASE midterm_db;

CREATE USER 'midterm_user'@'localhost' IDENTIFIED BY 'midterm_pass';

GRANT ALL PRIVILEGES ON midterm_db.* TO 'midterm_user'@'localhost';

USE midterm_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    password VARCHAR(50)
);

INSERT INTO users (username, password)
VALUES ('admin', 'admin123');
