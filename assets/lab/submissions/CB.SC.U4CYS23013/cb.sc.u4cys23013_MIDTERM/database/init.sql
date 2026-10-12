CREATE DATABASE IF NOT EXISTS midterm_db;

CREATE USER IF NOT EXISTS 'midterm_user'@'localhost'
IDENTIFIED BY 'midterm_pass';

GRANT ALL PRIVILEGES ON midterm_db.* TO 'midterm_user'@'localhost';

USE midterm_db;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    password VARCHAR(100)
);

INSERT INTO users (username, password)
VALUES ('gt', 'dog@123');