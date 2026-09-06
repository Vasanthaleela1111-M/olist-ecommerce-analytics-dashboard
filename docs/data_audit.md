# Olist E-Commerce Data Discovery and Quality Audit

## Executive Overview
This document provides the formal data discovery, schema analysis, and quality audit across all **9 CSV datasets** in the `/data` directory of the Olist Brazilian E-Commerce project. The dataset encompasses **99,441 orders** placed between September 2016 and October 2018 across 27 Brazilian states.

---

## 1. Complete Dataset Audit Matrix

| Dataset File Name | Row Count | Column Count | Primary Key (PK) | Foreign Keys (FK) | Unique PK Count | Null Count (Total) | Duplicate Rows | Candidate Analytical Grain |
| :--- | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| `orders.csv` | 99,441 | 8 | `order_id` | `customer_id` | 99,441 | 4,908 | 0 | Order Grain (Primary) |
| `customers.csv` | 99,441 | 5 | `customer_id` | `customer_zip_code_prefix` | 99,441 | 0 | 0 | Customer Order Endpoint |
| `order_items.csv` | 112,650 | 6 | (`order_id`, `order_item_id`) | `order_id`, `product_id`, `seller_id` | 112,650 | 0 | 0 | Item Line Grain |
| `order_payments.csv` | 103,886 | 5 | (`order_id`, `payment_sequential`)| `order_id` | 103,886 | 0 | 0 | Payment Sequence Grain |
| `order_reviews.csv` | 100,000 | 7 | `review_id` | `order_id` | 99,173 | 146,532 | 0 | Customer Review Grain |
| `products.csv` | 32,951 | 9 | `product_id` | `product_category_name` | 32,951 | 2,448 | 0 | Product Catalog Grain |
| `sellers.csv` | 3,095 | 4 | `seller_id` | `seller_zip_code_prefix` | 3,095 | 0 | 0 | Seller Merchant Grain |
| `geolocation.csv` | 1,000,163 | 5 | Non-unique (`zip_prefix` + lat/lng) | `geolocation_zip_code_prefix` | 19,015 (ZIPs) | 0 | 261,836 | Geographic Coordinates |
| `category_translation.csv` | 71 | 2 | `product_category_name` | None | 71 | 0 | 0 | Translation Lookup |

---

## 2. File-by-File Detailed Audit

### 2.1 Orders Dataset (`orders.csv`)
- **Row Count**: 99,441 | **Column Count**: 8 | **Duplicate Full Rows**: 0
- **Primary Key**: `order_id` (99,441 unique values - 100% unique)
- **Foreign Key**: `customer_id` (99,441 unique values - 1:1 relationship with orders)
- **Column Data Types & Missing Values**:
  - `order_id`: string (0 nulls, 0.0%)
  - `customer_id`: string (0 nulls, 0.0%)
  - `order_status`: string (0 nulls, 0.0% | 8 distinct statuses: `delivered`: 96,478, `shipped`: 1,107, `canceled`: 625, `unavailable`: 609, `invoiced`: 314, `processing`: 301, `created`: 5, `approved`: 2)
  - `order_purchase_timestamp`: datetime (0 nulls, 0.0%)
  - `order_approved_at`: datetime (160 nulls, 0.16%)
  - `order_delivered_carrier_date`: datetime (1,783 nulls, 1.79%)
  - `order_delivered_customer_date`: datetime (2,965 nulls, 2.98%)
  - `order_estimated_delivery_date`: datetime (0 nulls, 0.0%)
- **Date Ranges**:
  - `order_purchase_timestamp`: **2016-09-04 21:15:19** to **2018-10-17 17:30:18**
  - `order_approved_at`: **2016-09-15 12:16:38** to **2018-09-03 17:40:06**
  - `order_delivered_carrier_date`: **2016-10-08 10:34:01** to **2018-09-11 19:48:28**
  - `order_delivered_customer_date`: **2016-10-11 13:46:32** to **2018-10-17 13:22:46**
  - `order_estimated_delivery_date`: **2016-09-30 00:00:00** to **2018-11-12 00:00:00**

---

### 2.2 Customers Dataset (`customers.csv`)
- **Row Count**: 99,441 | **Column Count**: 5 | **Duplicate Full Rows**: 0
- **Primary Key**: `customer_id` (99,441 unique values)
- **Foreign Key**: `customer_zip_code_prefix` (14,994 unique ZIP prefixes)
- **Important Key Cardinality**:
  - `customer_unique_id`: **96,096 unique buyers**. 
  - **Repeat Customer Rate**: 2,997 customers (**3.12%**) placed $>1$ order (Maximum orders by a single customer: 17 orders).
- **Column Data Types & Missing Values**:
  - `customer_id`: string (0 nulls)
  - `customer_unique_id`: string (0 nulls)
  - `customer_zip_code_prefix`: integer (0 nulls)
  - `customer_city`: string (0 nulls, 4,119 unique cities)
  - `customer_state`: string (0 nulls, 27 unique states)

---

### 2.3 Order Items Dataset (`order_items.csv`)
- **Row Count**: 112,650 | **Column Count**: 6 | **Duplicate Full Rows**: 0
- **Composite Primary Key**: (`order_id`, `order_item_id`)
- **Foreign Keys**: 
  - `order_id`: 98,666 unique orders (Note: 775 orders in `orders.csv` have no items recorded, e.g. early cancellations)
  - `product_id`: 32,951 unique products
  - `seller_id`: 3,095 unique sellers
- **Column Data Types & Missing Values**:
  - `order_id`: string (0 nulls)
  - `order_item_id`: integer (0 nulls, range: 1 to 21 items per order)
  - `product_id`: string (0 nulls)
  - `seller_id`: string (0 nulls)
  - `shipping_limit_date`: datetime (0 nulls, range: 2016-09-19 to 2020-04-09)
  - `price`: float (0 nulls, range: R$ 0.85 to R$ 6,735.00)
  - `freight_value`: float (0 nulls, range: R$ 0.00 to R$ 409.68)

---

### 2.4 Order Payments Dataset (`order_payments.csv`)
- **Row Count**: 103,886 | **Column Count**: 5 | **Duplicate Full Rows**: 0
- **Composite Primary Key**: (`order_id`, `payment_sequential`)
- **Foreign Key**: `order_id` (99,440 unique orders - 1 order has no payment row)
- **Column Data Types & Missing Values**:
  - `order_id`: string (0 nulls)
  - `payment_sequential`: integer (0 nulls, range: 1 to 29 sequential payments)
  - `payment_type`: string (0 nulls, 5 distinct types: `credit_card`: 76,784, `boleto`: 19,784, `voucher`: 5,775, `debit_card`: 1,529, `not_defined`: 3)
  - `payment_installments`: integer (0 nulls, range: 0 to 24 installments)
  - `payment_value`: float (0 nulls, range: R$ 0.00 to R$ 13,664.08)

---

### 2.5 Order Reviews Dataset (`order_reviews.csv`)
- **Row Count**: 100,000 | **Column Count**: 7 | **Duplicate Full Rows**: 0
- **Primary Key**: `review_id` (99,173 unique values - 827 duplicate `review_id` instances exist where a review was updated or re-submitted)
- **Foreign Key**: `order_id` (99,441 unique orders covered)
- **Column Data Types & Missing Values**:
  - `review_id`: string (0 nulls)
  - `order_id`: string (0 nulls)
  - `review_score`: integer (0 nulls, 1 to 5 scale: 5-star: 57,320, 4-star: 19,142, 3-star: 8,179, 2-star: 3,157, 1-star: 11,424)
  - `review_comment_title`: string (88,285 nulls, 88.29% missing)
  - `review_comment_message`: string (58,247 nulls, 58.25% missing)
  - `review_creation_date`: datetime (0 nulls, min: 2016-10-02, max: 2018-08-31)
  - `review_answer_timestamp`: datetime (0 nulls, min: 2016-10-07, max: 2018-10-29)

---

### 2.6 Products Dataset (`products.csv`)
- **Row Count**: 32,951 | **Column Count**: 9 | **Duplicate Full Rows**: 0
- **Primary Key**: `product_id` (32,951 unique values - 100% unique)
- **Foreign Key**: `product_category_name` (73 unique category names)
- **Column Data Types & Missing Values**:
  - `product_id`: string (0 nulls)
  - `product_category_name`: string (610 nulls, 1.85% missing)
  - `product_name_lenght`: float (610 nulls, 1.85% missing)
  - `product_description_lenght`: float (610 nulls, 1.85% missing)
  - `product_photos_qty`: float (610 nulls, 1.85% missing)
  - `product_weight_g`: float (2 nulls, 0.01% missing)
  - `product_length_cm`: float (2 nulls, 0.01% missing)
  - `product_height_cm`: float (2 nulls, 0.01% missing)
  - `product_width_cm`: float (2 nulls, 0.01% missing)

---

### 2.7 Sellers Dataset (`sellers.csv`)
- **Row Count**: 3,095 | **Column Count**: 4 | **Duplicate Full Rows**: 0
- **Primary Key**: `seller_id` (3,095 unique values - 100% unique)
- **Foreign Key**: `seller_zip_code_prefix` (2,246 unique ZIP prefixes)
- **Column Data Types & Missing Values**:
  - `seller_id`: string (0 nulls)
  - `seller_zip_code_prefix`: integer (0 nulls)
  - `seller_city`: string (0 nulls, 611 unique cities)
  - `seller_state`: string (0 nulls, 23 unique states)

---

### 2.8 Geolocation Dataset (`geolocation.csv`)
- **Row Count**: 1,000,163 | **Column Count**: 5 | **Duplicate Full Rows**: 261,836
- **Grain**: Non-unique location observations per ZIP prefix (19,015 unique ZIP prefixes)
- **Column Data Types & Missing Values**:
  - `geolocation_zip_code_prefix`: integer (0 nulls, 19,015 unique)
  - `geolocation_lat`: float (0 nulls, range: -36.60 to 45.41)
  - `geolocation_lng`: float (0 nulls, range: -101.42 to 121.15)
  - `geolocation_city`: string (0 nulls, 8,011 unique cities)
  - `geolocation_state`: string (0 nulls, 27 unique states)

---

### 2.9 Category Translation Dataset (`category_translation.csv`)
- **Row Count**: 71 | **Column Count**: 2 | **Duplicate Full Rows**: 0
- **Primary Key**: `product_category_name` (71 unique values)
- **Column Data Types & Missing Values**:
  - `product_category_name`: string (0 nulls)
  - `product_category_name_english`: string (0 nulls)
- **Note**: 2 Portuguese categories in `products.csv` (`pc_gamer` and `portateis_cozinha_e_preparadores_de_alimentos`) lack direct entries in `category_translation.csv` and require fallback handling.

---

## 3. Relationships & Entity Topology

```
                   +---------------------+
                   |   customers.csv     |
                   | PK: customer_id     |
                   +----------+----------+
                              | (1:1)
                              v
+------------------+  (1:N) +---------------------+  (1:N) +---------------------+
| order_reviews.csv| <------+     orders.csv      +------> | order_payments.csv  |
| PK: review_id    |        | PK: order_id        |        | Composite PK        |
+------------------+        +----------+----------+        +---------------------+
                                       | (1:N)
                                       v
                            +---------------------+
                            |  order_items.csv    |
                            | Composite PK        |
                            +----+-----------+----+
                          (N:1)  |           | (N:1)
                                 v           v
            +--------------------+---+   +---+------------------+
            |    products.csv        |   |   sellers.csv        |
            | PK: product_id         |   | PK: seller_id        |
            +------------+-----------+   +---------+------------+
                         | (N:1)                   | (N:1)
                         v                         v
            +------------+-----------+   +---------+------------+
            |category_translation.csv|   |   geolocation.csv    |
            | PK: product_cat_name   |   | Non-unique ZIP Prefix|
            +------------------------+   +----------------------+
```

---

## 4. Join Risks & Mitigation Controls

### Risk 1: Cartesian Explosion on Direct Geolocation Join (CRITICAL)
- **Issue**: `geolocation.csv` contains 1,000,163 rows for only 19,015 ZIP code prefixes. Joining `customers` or `sellers` directly on `zip_code_prefix` creates a Cartesian product of millions of duplicate rows.
- **Mitigation**: Aggregating `geolocation.csv` by `geolocation_zip_code_prefix` to compute mean latitude and mean longitude before performing any join.

### Risk 2: Revenue Duplication on Item-Level Joins
- **Issue**: Joining `order_items` directly to `orders` duplicates order status, review scores, and customer metadata across multiple item rows (up to 21 items per order).
- **Mitigation**: Aggregate `order_items` to the `order_id` grain (`sum(price)`, `sum(freight_value)`, `count(order_item_id)`) prior to merging with `orders`.

### Risk 3: Payment Multiplicity Distortion
- **Issue**: 103,886 payment records exist for 99,440 orders because customers can pay with multiple vouchers or credit cards.
- **Mitigation**: Aggregate `order_payments` to the `order_id` grain (`sum(payment_value)`, `max(payment_installments)`, primary payment type) prior to order-level analysis.

### Risk 4: Duplicate Review IDs & Multiple Reviews
- **Issue**: 559 orders have multiple review entries in `order_reviews.csv`.
- **Mitigation**: Sort reviews by `review_answer_timestamp` and take the latest review per order, or calculate average review score per order.

---

## 5. Recommended Analytical Grains

1. **Primary Analytical Grain**: `order_id` (99,441 records). Every row represents a single customer order transaction.
2. **Customer Analysis Grain**: `customer_unique_id` (96,096 records) for analyzing repeat purchase frequency and customer lifetime value.
3. **Seller Performance Grain**: `seller_id` (3,095 records) for evaluating seller revenue concentration (Pareto curve) and fulfillment speed.
4. **Category Performance Grain**: `category_english` (73 categories) with minimum sample threshold $N \ge 50$ orders.
