CREATE DATABASE IF NOT EXISTS midterm_db;

USE midterm_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    password VARCHAR(50)
);

INSERT INTO users(username,password)
VALUES('jaiaditya','jai2005');
