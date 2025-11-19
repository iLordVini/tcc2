-- Extensões necessárias
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabelas
CREATE TABLE user_account (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE sellers (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES user_account(id),
    store_name VARCHAR(255) NOT NULL,
    rating DECIMAL(3,2) DEFAULT 5.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES user_account(id),
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'Brasil',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    seller_id INTEGER REFERENCES sellers(id),
    category_id INTEGER REFERENCES categories(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    sku VARCHAR(100) UNIQUE,
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    stock_quantity INTEGER DEFAULT 0 CHECK (stock_quantity >= 0),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id),
    order_number VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    subtotal DECIMAL(10,2) DEFAULT 0,
    shipping_amount DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(10,2) NOT NULL CHECK (total_amount >= 0),
    payment_status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL CHECK (unit_price >= 0),
    total_price DECIMAL(10,2) NOT NULL CHECK (total_price >= 0)
);

CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    payment_method VARCHAR(50),
    amount DECIMAL(10,2) NOT NULL,
    paid_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'pending'
);

CREATE TABLE shipments (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    tracking_code VARCHAR(100),
    carrier VARCHAR(100),
    shipped_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'pending'
);

-- Dados iniciais
INSERT INTO categories (id, name) VALUES
(1, 'Eletrônicos'),
(2, 'Smartphones'),
(3, 'Computadores'),
(4, 'Roupas'),
(5, 'Masculino'),
(6, 'Feminino'),
(7, 'Casa'),
(8, 'Móveis'),
(9, 'Decoração'),
(10, 'Esportes');

INSERT INTO user_account (id, email, name, password_hash, role)
SELECT i, 'seller_'||i||'@marketplace.com', 'Vendedor '||i, crypt('seller'||i, gen_salt('bf')), 'seller'
FROM generate_series(1,100) i;

INSERT INTO sellers (id, user_id, store_name, rating)
SELECT i, i, 'Loja '||i, 4.0 + (i % 10) * 0.1
FROM generate_series(1,100) i;

INSERT INTO user_account (id, email, name, password_hash, role)
SELECT 100 + i, 'client_'||i||'@marketplace.com', 'Cliente '||i, crypt('client'||i, gen_salt('bf')), 'client'
FROM generate_series(1,1000) i;

INSERT INTO clients (id, user_id, name, phone, city, state)
SELECT i, 100 + i, 'Cliente '||i, '1199'||LPAD(i::text,6,'0'),
CASE WHEN i%5=0 THEN 'São Paulo' WHEN i%5=1 THEN 'Rio de Janeiro' WHEN i%5=2 THEN 'Belo Horizonte' WHEN i%5=3 THEN 'Salvador' ELSE 'Curitiba' END,
CASE WHEN i%5=0 THEN 'SP' WHEN i%5=1 THEN 'RJ' WHEN i%5=2 THEN 'MG' WHEN i%5=3 THEN 'BA' ELSE 'PR' END
FROM generate_series(1,1000) i;

INSERT INTO products (id, seller_id, category_id, name, description, sku, price, stock_quantity)
SELECT i, ((i-1)%100)+1, ((i-1)%10)+1,
'Produto '||i, 'Descrição do produto '||i, 'SKU'||LPAD(i::text,8,'0'),
50.00 + (i%1000), (i%500)+1
FROM generate_series(1,1000000) i;

INSERT INTO orders (id, client_id, order_number, status, subtotal, shipping_amount, total_amount)
SELECT i, ((i-1)%1000)+1, 'ORD'||LPAD(i::text,8,'0'), 'pending',
100 + (i%500), 10, 110 + (i%500)
FROM generate_series(1,10000) i;

INSERT INTO order_items (id, order_id, product_id, quantity, unit_price, total_price)
SELECT i, ((i-1)%10000)+1, ((i-1)%1000000)+1, 1 + ((i-1)%3), 100 + (i%200), (1 + ((i-1)%3)) * (100 + (i%200))
FROM generate_series(1,20000) i;

INSERT INTO payments (order_id, payment_method, amount, status)
SELECT id, 'credit_card', total_amount, 'paid'
FROM orders;

INSERT INTO shipments (order_id, tracking_code, carrier, status)
SELECT id, 'TRK'||LPAD(id::text,8,'0'), 'Correios', 'shipped'
FROM orders;

-- Atualizar sequences
SELECT setval('user_account_id_seq', (SELECT MAX(id) FROM user_account));
SELECT setval('sellers_id_seq', (SELECT MAX(id) FROM sellers));
SELECT setval('clients_id_seq', (SELECT MAX(id) FROM clients));
SELECT setval('categories_id_seq', (SELECT MAX(id) FROM categories));
SELECT setval('products_id_seq', (SELECT MAX(id) FROM products));
SELECT setval('orders_id_seq', (SELECT MAX(id) FROM orders));
SELECT setval('order_items_id_seq', (SELECT MAX(id) FROM order_items));
SELECT setval('payments_id_seq', (SELECT MAX(id) FROM payments));
SELECT setval('shipments_id_seq', (SELECT MAX(id) FROM shipments));

ANALYZE user_account;
ANALYZE sellers;
ANALYZE clients;
ANALYZE categories;
ANALYZE products;
ANALYZE orders;
ANALYZE order_items;
ANALYZE payments;
ANALYZE shipments;
