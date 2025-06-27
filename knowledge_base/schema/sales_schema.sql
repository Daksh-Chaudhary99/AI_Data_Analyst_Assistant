CREATE TABLE regions (
    region_id INTEGER PRIMARY KEY,
    region_name TEXT NOT NULL UNIQUE
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL
);

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name TEXT NOT NULL,
    email TEXT UNIQUE,
    region_id INTEGER,
    FOREIGN KEY (region_id) REFERENCES regions(region_id)
);

CREATE TABLE sales (
    sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    region_id INTEGER NOT NULL,
    sale_date TEXT NOT NULL, -- Stored as YYYY-MM-DD
    quantity INTEGER NOT NULL,
    amount REAL NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (region_id) REFERENCES regions(region_id)
);