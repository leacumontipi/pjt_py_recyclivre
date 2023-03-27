CREATE DATABASE recyclivre

CREATE TABLE user
(
    id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    username VARCHAR(20),
    password VARCHAR(255),
);

CREATE TABLE book
(
    id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    title VARCHAR(255),
    author VARCHAR(255),
    edition VARCHAR(255),
    summary TEXT(255),
    price DECIMAL(4,2),
    FOREIGN KEY (id) REFERENCES user(id),
);

INSERT INTO user VALUES ('Jean', 'Livre', 'admin', 'admin')
INSERT INTO book VALUES ('Alice au pays des merveilles', 'Lewis Carroll', 'Soleil', 'Un matin, Alice décide de suivre un mystérieux Lapin Blanc jusque dans son terrier. Chemin faisant, elle fait des rencontres surprenantes : une Reine de Coeur qui veut couper la tête de tout le monde, un Chapelier fou avec lequel elle prend le thé, ou encore un Chat qui arbore un sourire jusqu\'aux oreilles', 29.90, 1);
INSERT INTO book VALUES ('Salem', 'Stephen King', 'Le livre de Poche', 'Le Maine, 1970. Ben Mears revient à Salem et s\'installe à Marsten House, inhabitée depuis la mort tragique de ses propriétaires, vingt-cinq ans auparavant.', 9.90, 1);



