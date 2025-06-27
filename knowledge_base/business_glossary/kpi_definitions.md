# Business Glossary and KPI Definitions

This document provides definitions for key business terms and performance indicators used in our sales analysis.

---

## Key Performance Indicators (KPIs)

### Average Sales
**Definition:** The average monetary value of a single sales transaction. It is calculated by dividing the total sales amount by the total number of sales transactions over a given period.
**Calculation:** `SUM(amount) / COUNT(sale_id)` from the `sales` table.

### Sales Volume
**Definition:** The total number of products sold over a specified period. This indicates the quantity of goods moved.
**Calculation:** `SUM(quantity)` from the `sales` table.

### Revenue by Region
**Definition:** The total monetary value of sales attributed to a specific geographical region over a given period.
**Calculation:** `SUM(amount)` grouped by `region_name` from `sales` and `regions` tables.

---

## Business Terms

### Customer Segment
**Definition:** A group of customers sharing similar characteristics, often based on demographics, purchasing behavior, or psychographics. (Note: We don't have explicit segments in the current DB, but this is an example of what you'd define).

### Last Quarter
**Definition:** Refers to the most recently completed three-month period. For example, if the current month is June, the last quarter would typically be January-March. If it's July, the last quarter would be April-June.

---