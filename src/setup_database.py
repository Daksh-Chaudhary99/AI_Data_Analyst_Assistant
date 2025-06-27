import sqlite3
import os
import pandas as pd
from datetime import datetime, timedelta
import random
from tqdm import tqdm

DATABASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
DATABASE_PATH = os.path.join(DATABASE_DIR, 'sales_database.db')

def create_database():
    """Creates the SQLite database file if it doesn't exist."""
    os.makedirs(DATABASE_DIR, exist_ok=True)
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        print(f"Database created successfully at {DATABASE_PATH}")
    except sqlite3.Error as e:
        print(f"Error creating database: {e}")
    finally:
        if conn:
            conn.close()

def create_tables(conn):
    """Creates necessary tables in the database."""
    cursor = conn.cursor()

    # Regions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS regions (
            region_id INTEGER PRIMARY KEY,
            region_name TEXT NOT NULL UNIQUE
        );
    ''')

    # Products Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL
        );
    ''')

    # Customers Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            customer_name TEXT NOT NULL,
            email TEXT UNIQUE,
            region_id INTEGER,
            FOREIGN KEY (region_id) REFERENCES regions(region_id)
        );
    ''')

    # Sales Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
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
    ''')
    conn.commit()
    print("Tables created successfully.")

def insert_dummy_data(conn):
    """Inserts sample data into the tables."""
    cursor = conn.cursor()

    # Clear existing data before inserting new, to ensure fresh start
    print("Clearing existing data...")
    cursor.execute("DELETE FROM sales")
    cursor.execute("DELETE FROM customers")
    cursor.execute("DELETE FROM products")
    cursor.execute("DELETE FROM regions")
    conn.commit()
    print("Existing data cleared.")


    # Insert Regions
    regions_data = [
        (1, 'North'),
        (2, 'South'),
        (3, 'East'),
        (4, 'West'),
        (5, 'Central') # Added a new region
    ]
    cursor.executemany("INSERT OR IGNORE INTO regions (region_id, region_name) VALUES (?, ?)", regions_data)
    print(f"Inserted {len(regions_data)} regions.")

    # Insert Products (More variety, including sub-categories implicitly via name)
    products_data = [
        (101, 'Laptop Basic', 'Electronics', 800.00),
        (102, 'Laptop Pro', 'Electronics', 1500.00),
        (103, 'Smartphone X', 'Electronics', 700.00),
        (104, 'Smartwatch', 'Electronics', 250.00),
        (105, 'Headphones Noise-Cancelling', 'Electronics', 180.00),
        (201, 'Office Desk Standard', 'Furniture', 200.00),
        (202, 'Ergonomic Chair', 'Furniture', 350.00),
        (203, 'Bookshelf Small', 'Furniture', 80.00),
        (301, 'Notebook A4', 'Stationery', 12.00),
        (302, 'Premium Pen Set', 'Stationery', 30.00),
        (303, 'Art Supplies Kit', 'Stationery', 45.00),
        (401, 'Running Shoes', 'Apparel', 110.00), # New Category
        (402, 'T-Shirt Cotton', 'Apparel', 25.00),
    ]
    cursor.executemany("INSERT OR IGNORE INTO products (product_id, product_name, category, price) VALUES (?, ?, ?, ?)", products_data)
    print(f"Inserted {len(products_data)} products.")

    # Insert Customers (More customers)
    customer_names = [
        'Alice Smith', 'Bob Johnson', 'Charlie Brown', 'Diana Prince', 'Eve Adams', 
        'Frank White', 'Grace Lee', 'Henry Green', 'Ivy Chen', 'Jack Taylor',
        'Karen Black', 'Liam Davis', 'Mia Wilson', 'Noah Martinez', 'Olivia Garcia',
        'Peter Rodriguez', 'Quinn Miller', 'Rachel Jones', 'Sam Hernandez', 'Tina Clark'
    ] # 20 customers
    customers_data = []
    for i, name in enumerate(customer_names):
        # Assign customers to regions, trying to balance or bias
        region_id = random.choice([1, 1, 2, 3, 4, 5]) # North region (ID 1) slightly more customers
        customers_data.append((i + 1, name, f"{name.replace(' ', '').lower()}@example.com", region_id))
    cursor.executemany("INSERT OR IGNORE INTO customers (customer_id, customer_name, email, region_id) VALUES (?, ?, ?, ?)", customers_data)
    print(f"Inserted {len(customers_data)} customers.")


    # --- Sales Data Generation Configuration (MOVED TO HERE) ---
    NUM_SALES_RECORDS = 15000 
    
    end_date = datetime.now()
    
    # Ensure a good chunk of sales are recent
    recent_sales_period_days = 60 # Sales within last 2 months
    long_term_sales_period_days = 730 # Sales within last 2 years

    # Define how many sales should be recent vs. long-term
    recent_sales_proportion = 0.3 # 30% of sales in the last 2 months
    num_recent_sales = int(NUM_SALES_RECORDS * recent_sales_proportion)
    num_long_term_sales = NUM_SALES_RECORDS - num_recent_sales

    products_df = pd.DataFrame(products_data, columns=['product_id', 'product_name', 'category', 'price'])
    customers_df = pd.DataFrame(customers_data, columns=['customer_id', 'customer_name', 'email', 'region_id'])
    regions_df = pd.DataFrame(regions_data, columns=['region_id', 'region_name'])

    sales_records = []

    # Define some regional biases (e.g., North sells more)
    region_weights = {1: 0.30, 2: 0.25, 3: 0.20, 4: 0.15, 5: 0.10}
    weighted_regions = [r for r, weight in region_weights.items() for _ in range(int(weight * 100))]

    # Define some category biases (e.g., Electronics sells more)
    category_weights = {'Electronics': 0.40, 'Furniture': 0.30, 'Stationery': 0.20, 'Apparel': 0.10}
    all_weighted_products = []
    for cat, weight in category_weights.items():
        cat_products = products_df[products_df['category'] == cat]['product_id'].tolist()
        all_weighted_products.extend(cat_products * int(weight * 100 / (len(cat_products) if cat_products else 1)))
    
    # Simulate some seasonality (e.g., more sales towards end of year)
    def get_seasonal_factor(date):
        month = date.month
        if month in [11, 12]: return random.uniform(1.1, 1.3) 
        elif month in [1, 2]: return random.uniform(0.8, 1.0) 
        else: return random.uniform(0.9, 1.1) 

    # --- End Sales Data Generation Configuration ---


    # Generate recent sales
    for _ in tqdm(range(num_recent_sales), desc="Generating Recent Sales Data"):
        current_date = end_date - timedelta(days=random.randint(0, recent_sales_period_days - 1))
        
        chosen_region_id = random.choice(weighted_regions)
        region_customers = customers_df[customers_df['region_id'] == chosen_region_id]
        customer = region_customers.sample(1).iloc[0] if not region_customers.empty else customers_df.sample(1).iloc[0]

        product = products_df[products_df['product_id'] == random.choice(all_weighted_products)].iloc[0]

        quantity = random.randint(1, 5)
        seasonal_factor = get_seasonal_factor(current_date)
        amount = round(quantity * product['price'] * (1 + random.uniform(-0.1, 0.1)) * seasonal_factor, 2)

        sales_records.append((
            int(product['product_id']),    # Explicitly cast to int
            int(customer['customer_id']),   # Explicitly cast to int
            int(customer['region_id']),    # Explicitly cast to int
            current_date.strftime('%Y-%m-%d'),
            quantity,
            amount
        ))
    
    # Generate long-term sales (apply the same fix here)
    for _ in tqdm(range(num_long_term_sales), desc="Generating Long-Term Sales Data"):
        current_date = end_date - timedelta(days=random.randint(recent_sales_period_days, long_term_sales_period_days - 1))
        
        chosen_region_id = random.choice(weighted_regions)
        region_customers = customers_df[customers_df['region_id'] == chosen_region_id]
        customer = region_customers.sample(1).iloc[0] if not region_customers.empty else customers_df.sample(1).iloc[0]

        product = products_df[products_df['product_id'] == random.choice(all_weighted_products)].iloc[0]

        quantity = random.randint(1, 5)
        seasonal_factor = get_seasonal_factor(current_date)
        amount = round(quantity * product['price'] * (1 + random.uniform(-0.1, 0.1)) * seasonal_factor, 2)

        sales_records.append((
            int(product['product_id']),    # Explicitly cast to int
            int(customer['customer_id']),   # Explicitly cast to int
            int(customer['region_id']),    # Explicitly cast to int
            current_date.strftime('%Y-%m-%d'),
            quantity,
            amount
        ))

    cursor.executemany("INSERT INTO sales (product_id, customer_id, region_id, sale_date, quantity, amount) VALUES (?, ?, ?, ?, ?, ?)", sales_records)
    conn.commit()
    print(f"Inserted {len(sales_records)} dummy sales records.")
    print("Dummy data inserted successfully.")

def main():
    create_database()
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        create_tables(conn)
        insert_dummy_data(conn)
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    main()