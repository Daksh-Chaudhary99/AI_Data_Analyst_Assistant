# Data Dictionary for Sales Database

This document describes the tables and columns within the sales database.

---

## Table: `regions`
**Purpose:** Stores information about geographical sales regions.

| Column      | Type    | Description                                   |
| :---------- | :------ | :-------------------------------------------- |
| `region_id` | INTEGER | Unique identifier for each sales region.      |
| `region_name`| TEXT    | Name of the sales region (e.g., 'North', 'South'). |

---

## Table: `products`
**Purpose:** Contains details about products sold.

| Column        | Type    | Description                                     |
| :------------ | :------ | :---------------------------------------------- |
| `product_id`  | INTEGER | Unique identifier for each product.             |
| `product_name`| TEXT    | Name of the product (e.g., 'Laptop', 'Pen Set').|
| `category`    | TEXT    | Product category (e.g., 'Electronics', 'Furniture').|
| `price`       | REAL    | Standard price of the product.                  |

---

## Table: `customers`
**Purpose:** Stores customer information.

| Column        | Type    | Description                                     |
| :------------ | :------ | :---------------------------------------------- |
| `customer_id` | INTEGER | Unique identifier for each customer.            |
| `customer_name`| TEXT    | Full name of the customer.                      |
| `email`       | TEXT    | Customer's email address, unique per customer.  |
| `region_id`   | INTEGER | ID of the region the customer belongs to. Links to `regions.region_id`. |

---

## Table: `sales`
**Purpose:** Records individual sales transactions.

| Column        | Type    | Description                                     |
| :------------ | :------ | :---------------------------------------------- |
| `sale_id`     | INTEGER | Unique identifier for each sale transaction.    |
| `product_id`  | INTEGER | ID of the product sold. Links to `products.product_id`. |
| `customer_id` | INTEGER | ID of the customer involved in the sale. Links to `customers.customer_id`. |
| `region_id`   | INTEGER | ID of the region where the sale occurred. This can also be derived from the customer's region. Links to `regions.region_id`. |
| `sale_date`   | TEXT    | Date of the sale in 'YYYY-MM-DD' format.        |
| `quantity`    | INTEGER | Number of units sold in this transaction.       |
| `amount`      | REAL    | Total monetary value of the sale (quantity * price, potentially with variations). |

---

## Relationships:
* `customers.region_id` links to `regions.region_id`
* `sales.product_id` links to `products.product_id`
* `sales.customer_id` links to `customers.customer_id`
* `sales.region_id` links to `regions.region_id`