CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL
);

INSERT INTO users (username, password)
VALUES ('admin', 'admin123')
ON CONFLICT (username) DO NOTHING;

GRANT ALL PRIVILEGES ON TABLE users TO midterm_user;
GRANT USAGE, SELECT ON SEQUENCE users_id_seq TO midterm_user;
