
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(250) NOT NULL UNIQUE,
    password VARCHAR(250) NOT NULL
);


CREATE TABLE IF NOT EXISTS bucher (
    id INT AUTO_INCREMENT PRIMARY KEY,
    buchtitel VARCHAR(100) NOT NULL,
    autor VARCHAR(100) NOT NULL,
    verlag VARCHAR(100) NOT NULL,
    sprache VARCHAR(100),
    originalpreis DECIMAL(10, 2)
);

CREATE TABLE IF NOT EXISTS angebot (
    user_id INT NOT NULL,
    buch_id INT NOT NULL,
    qualitat ENUM('wie neu', 'gut', 'mittel', 'schlecht'),
    verkauft BOOLEAN,
    CONSTRAINT fk1 FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT fk2 FOREIGN KEY (buch_id) REFERENCES bucher(id)
);
