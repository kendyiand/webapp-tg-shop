CREATE TABLE IF NOT EXISTS product  (
    id BIGINT,
    first_name VARCHAR(64),
    last_name VARCHAR(64),
    username VARCHAR(32),
    role ENUM('user', 'admin') DEFAULT 'user'
);