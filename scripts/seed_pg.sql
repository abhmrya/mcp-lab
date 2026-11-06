
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    category VARCHAR(100) NOT NULL
);

INSERT INTO products (name, price, category)
VALUES
    ('Laptop', 50000, 'Electronics'),
    ('Mouse', 500, 'Accessories'),
    ('Keyboard', 1200, 'Accessories')
ON CONFLICT DO NOTHING;
