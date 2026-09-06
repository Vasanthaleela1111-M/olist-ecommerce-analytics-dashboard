# Olist E-Commerce Data Dictionary

This document serves as the authoritative data dictionary for all **9 CSV datasets** in the Olist Brazilian E-Commerce analytics project.

---

## 1. Orders Table (`orders.csv`)
- **Primary Grain**: `order_id` (1 row per order transaction)
- **Total Rows**: 99,441

| Column Name | Data Type | Key Type | Nullable | Description / Business Meaning | Sample / Allowed Values |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `order_id` | string | PK | No | Unique identifier of the order transaction | `e481f51cbdc54678b7cc49136f2d6af7` |
| `customer_id` | string | FK | No | Foreign key linking to `customers.csv` (unique per order) | `9ef432eb6251297304e76186b10a928d` |
| `order_status` | string | Attribute | No | Order lifecycle status | `delivered`, `shipped`, `canceled`, `unavailable`, `invoiced`, `processing`, `created`, `approved` |
| `order_purchase_timestamp` | datetime | Attribute | No | Timestamp when customer placed the order | `2017-10-02 10:56:33` |
| `order_approved_at` | datetime | Attribute | Yes | Timestamp when payment approval was confirmed | `2017-10-02 11:07:15` |
| `order_delivered_carrier_date` | datetime | Attribute | Yes | Timestamp when order was handed to logistics carrier | `2017-10-04 19:55:00` |
| `order_delivered_customer_date`| datetime | Attribute | Yes | Actual timestamp when customer received the order | `2017-10-10 21:25:13` |
| `order_estimated_delivery_date`| datetime | Attribute | No | Estimated delivery date promised to customer at purchase | `2017-10-18 00:00:00` |

---

## 2. Customers Table (`customers.csv`)
- **Primary Grain**: `customer_id` (1 row per customer order key)
- **Total Rows**: 99,441

| Column Name | Data Type | Key Type | Nullable | Description / Business Meaning | Sample / Allowed Values |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `customer_id` | string | PK | No | Key linked to orders (unique per order) | `9ef432eb6251297304e76186b10a928d` |
| `customer_unique_id` | string | Identifier | No | Unique identifier of the actual human buyer (used to track repeat orders) | `7c396fdbe695d5426c39f3d5106756c7` |
| `customer_zip_code_prefix` | integer | FK | No | First 5 digits of customer ZIP code | `01151`, `13023` |
| `customer_city` | string | Attribute | No | Customer residential city | `sao paulo`, `rio de janeiro` |
| `customer_state` | string | Attribute | No | Customer 2-letter state code | `SP`, `RJ`, `MG`, `RS`, `PR` (27 states) |

---

## 3. Order Items Table (`order_items.csv`)
- **Primary Grain**: Composite (`order_id`, `order_item_id`)
- **Total Rows**: 112,650

| Column Name | Data Type | Key Type | Nullable | Description / Business Meaning | Sample / Allowed Values |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `order_id` | string | FK | No | Foreign key linking to `orders.csv` | `e481f51cbdc54678b7cc49136f2d6af7` |
| `order_item_id` | integer | PK | No | Sequential number identifying item within an order | `1`, `2`, `3` (Range: 1 to 21) |
| `product_id` | string | FK | No | Foreign key linking to `products.csv` | `87285b2e9cb76b728053f11819e3d194` |
| `seller_id` | string | FK | No | Foreign key linking to `sellers.csv` | `350400472dbd9329a0e7040b528e3568` |
| `shipping_limit_date` | datetime | Attribute | No | Seller deadline to ship order to logistics carrier | `2017-10-06 11:07:15` |
| `price` | float | Metric | No | Item selling price in Brazilian Reais (R$) | `29.99`, `120.00` |
| `freight_value` | float | Metric | No | Freight cost charged for this item in R$ | `8.72`, `15.10` |

---

## 4. Order Payments Table (`order_payments.csv`)
- **Primary Grain**: Composite (`order_id`, `payment_sequential`)
- **Total Rows**: 103,886

| Column Name | Data Type | Key Type | Nullable | Description / Business Meaning | Sample / Allowed Values |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `order_id` | string | FK | No | Foreign key linking to `orders.csv` | `e481f51cbdc54678b7cc49136f2d6af7` |
| `payment_sequential` | integer | PK | No | Sequence number for multiple payment methods per order | `1`, `2`, `3` (Range: 1 to 29) |
| `payment_type` | string | Attribute | No | Payment method chosen by customer | `credit_card`, `boleto`, `voucher`, `debit_card`, `not_defined` |
| `payment_installments` | integer | Attribute | No | Number of installment payments selected | `1` to `24` installments |
| `payment_value` | float | Metric | No | Total transaction value paid in R$ | `18.12`, `384.27` |

---

## 5. Order Reviews Table (`order_reviews.csv`)
- **Primary Grain**: `review_id` (1 row per review entry)
- **Total Rows**: 100,000

| Column Name | Data Type | Key Type | Nullable | Description / Business Meaning | Sample / Allowed Values |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `review_id` | string | PK | No | Unique identifier of the review survey | `a470795fe869ea03dd7088a5c9401b5c` |
| `order_id` | string | FK | No | Foreign key linking to `orders.csv` | `e481f51cbdc54678b7cc49136f2d6af7` |
| `review_score` | integer | Metric | No | Customer satisfaction score from 1 (lowest) to 5 (highest) | `1`, `2`, `3`, `4`, `5` |
| `review_comment_title` | string | Attribute | Yes | Short title of review message submitted by buyer | `recomendo`, `super recomendo` |
| `review_comment_message` | string | Attribute | Yes | Detailed free-form feedback text submitted by buyer | `Não recebi o produto...` |
| `review_creation_date` | datetime | Attribute | No | Date when review survey was sent to customer | `2017-10-11 00:00:00` |
| `review_answer_timestamp` | datetime | Attribute | No | Timestamp when customer completed review survey | `2017-10-12 03:43:48` |

---

## 6. Products Table (`products.csv`)
- **Primary Grain**: `product_id` (1 row per product SKU)
- **Total Rows**: 32,951

| Column Name | Data Type | Key Type | Nullable | Description / Business Meaning | Sample / Allowed Values |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `product_id` | string | PK | No | Unique identifier of the product item | `1e9e8ef04dbcff4541ed26657ea517e5` |
| `product_category_name` | string | FK | Yes | Category name in Portuguese | `perfumaria`, `esporte_lazer` |
| `product_name_lenght` | float | Attribute | Yes | Character length of product title | `40.0`, `58.0` |
| `product_description_lenght`| float | Attribute | Yes | Character length of product description text | `287.0`, `1250.0` |
| `product_photos_qty` | float | Attribute | Yes | Number of product listing photos | `1.0`, `4.0` |
| `product_weight_g` | float | Attribute | Yes | Product weight in grams | `225.0`, `1500.0` |
| `product_length_cm` | float | Attribute | Yes | Product package length in centimeters | `16.0`, `30.0` |
| `product_height_cm` | float | Attribute | Yes | Product package height in centimeters | `10.0`, `25.0` |
| `product_width_cm` | float | Attribute | Yes | Product package width in centimeters | `14.0`, `20.0` |

---

## 7. Sellers Table (`sellers.csv`)
- **Primary Grain**: `seller_id` (1 row per registered merchant)
- **Total Rows**: 3,095

| Column Name | Data Type | Key Type | Nullable | Description / Business Meaning | Sample / Allowed Values |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `seller_id` | string | PK | No | Unique identifier of seller merchant | `3442f8959a84dea7ee197c632cb2df15` |
| `seller_zip_code_prefix` | integer | FK | No | First 5 digits of seller ZIP code | `13023`, `20031` |
| `seller_city` | string | Attribute | No | Seller location city | `campinas`, `rio de janeiro` |
| `seller_state` | string | Attribute | No | Seller 2-letter state code | `SP`, `RJ`, `PR`, `MG`, `SC` |

---

## 8. Geolocation Table (`geolocation.csv`)
- **Primary Grain**: Non-unique location coordinate log
- **Total Rows**: 1,000,163

| Column Name | Data Type | Key Type | Nullable | Description / Business Meaning | Sample / Allowed Values |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `geolocation_zip_code_prefix`| integer | FK | No | First 5 digits of ZIP code (19,015 unique) | `01001`, `99990` |
| `geolocation_lat` | float | Attribute | No | Latitude geographic coordinate | `-23.548`, `-22.906` |
| `geolocation_lng` | float | Attribute | No | Longitude geographic coordinate | `-46.636`, `-43.172` |
| `geolocation_city` | string | Attribute | No | City name associated with ZIP prefix | `sao paulo`, `rio de janeiro` |
| `geolocation_state` | string | Attribute | No | 2-letter state code | `SP`, `RJ`, `MG` |

---

## 9. Category Translation Table (`category_translation.csv`)
- **Primary Grain**: `product_category_name` (1 row per category mapping)
- **Total Rows**: 71

| Column Name | Data Type | Key Type | Nullable | Description / Business Meaning | Sample / Allowed Values |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `product_category_name` | string | PK | No | Product category name in Portuguese | `perfumaria`, `artes` |
| `product_category_name_english`| string | Attribute | No | Product category name translated to English | `perfumery`, `art` |
