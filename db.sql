CREATE DATABASE recyclivre

CREATE TABLE user
(
    id INT PRIMARY KEY NOT NULL,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    username VARCHAR(20),
    password VARCHAR(255),
)

CREATE TABLE book
(
    id INT PRIMARY KEY NOT NULL,
    title VARCHAR(255),
    author VARCHAR(255),
    edition VARCHAR(255),
    summary TEXT(255),
    price DECIMAL(4,2),
    FOREIGN KEY (id) REFERENCES user(id),
    
)


