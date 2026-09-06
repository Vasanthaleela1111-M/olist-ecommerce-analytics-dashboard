# Formal Data Model - Olist E-Commerce Analytics

## Executive Overview
This document defines the formal relational data model and aggregation architecture for the Olist Brazilian E-Commerce dataset. The core architectural constraint of this data model is **Analytical Grain Preservation**: 

> **Central Analytical Grain**: **1 Row = 1 Unique Order (`order_id`)**  
> Total Order Backbone: **99,441 records**

To prevent Cartesian explosion, revenue double-counting, and fan-out join anomalies, raw tables with 1-to-Many cardinality (`order_items`, `order_payments`, `order_reviews`, `geolocation`) must undergo strict pre-join aggregation before merging into the master analytical table.

---

## 1. Table-by-Table Purpose & Schema Definition

| Table Name | Primary Purpose & Role | Primary Key (PK) | Foreign Keys (FK) | Target Grain |
| :--- | :--- | :--- | :--- | :--- |
| `orders` | Central transaction backbone detailing order lifecycle, timestamps, and customer key. | `order_id` | `customer_id` | 1 Row = 1 Order (99,441 rows) |
| `customers` | Buyer demographics, residential location, and unique customer identification (`customer_unique_id`). | `customer_id` | `customer_zip_code_prefix` | 1 Row = 1 Order Customer Key |
| `order_items` | Line-item details detailing item selling price, freight cost, product SKU, and seller ID. | (`order_id`, `order_item_id`) | `order_id`, `product_id`, `seller_id` | 1 Row = 1 Item Line |
| `order_payments` | Financial settlement sequence detailing payment method, installment count, and transaction value. | (`order_id`, `payment_sequential`) | `order_id` | 1 Row = 1 Payment Sequence |
| `order_reviews` | Customer satisfaction feedback detailing review scores, survey timestamps, and text messages. | `review_id` | `order_id` | 1 Row = 1 Review Survey |
| `products` | Product catalog attributes detailing category name, physical dimensions, weight, and photos. | `product_id` | `product_category_name` | 1 Row = 1 Product SKU |
| `sellers` | Merchant registration metadata detailing seller city, state, and location ZIP prefix. | `seller_id` | `seller_zip_code_prefix` | 1 Row = 1 Merchant Seller |
| `geolocation` | Spatial coordinate lookup mapping 5-digit ZIP prefixes to latitude and longitude. | Non-unique (`zip_prefix` + lat/lng) | `geolocation_zip_code_prefix` | 1 Row = 1 Coordinate Log |
| `category_translation` | Bilingual translation dictionary mapping Portuguese category names to English. | `product_category_name` | None | 1 Row = 1 Category Lookup |

---

## 2. Relationship Cardinality Matrix

| Parent Table | Child Table | Relationship Type | Cardinality | Join Key | Handling Strategy |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `orders` | `customers` | One-to-One | 1 : 1 | `customer_id` | Direct 1:1 `LEFT JOIN` |
| `customers` | `orders` | One-to-Many | 1 : $N$ | `customer_unique_id` | Group by `customer_unique_id` for repeat buyer analytics |
| `orders` | `order_items` | One-to-Many | 1 : $N$ | `order_id` | **Pre-aggregate** `order_items` to `order_id` grain before join |
| `orders` | `order_payments` | One-to-Many | 1 : $N$ | `order_id` | **Pre-aggregate** `order_payments` to `order_id` grain before join |
| `orders` | `order_reviews` | One-to-Many | 1 : $N$ | `order_id` | **Deduplicate** `order_reviews` to latest review per `order_id` |
| `order_items` | `products` | Many-to-One | $N$ : 1 | `product_id` | `LEFT JOIN` on primary product ID |
| `order_items` | `sellers` | Many-to-One | $N$ : 1 | `seller_id` | `LEFT JOIN` on primary seller ID |
| `products` | `category_translation` | Many-to-One | $N$ : 1 | `product_category_name` | `LEFT JOIN` with fallback for unmapped categories |
| `customers` | `geolocation` | Many-to-Many | $N$ : $M$ | `zip_code_prefix` | **Pre-aggregate** `geolocation` by ZIP prefix (mean lat/lng) |
| `sellers` | `geolocation` | Many-to-Many | $N$ : $M$ | `zip_code_prefix` | **Pre-aggregate** `geolocation` by ZIP prefix (mean lat/lng) |

---

## 3. Mandatory Pre-Join Aggregation Requirements

To maintain the **1 Row = 1 Order** grain without creating duplicate records or artificial inflation, the following transformations must be executed prior to table merging:

### 3.1 Order Items Aggregation (`order_items_agg`)
Group `order_items.csv` by `order_id` to create a 1:1 order summary:
$$\text{total\_price} = \sum(\text{price})$$
$$\text{total\_freight} = \sum(\text{freight\_value})$$
$$\text{total\_order\_value} = \text{total\_price} + \text{total\_freight}$$
$$\text{item\_count} = \text{count}(\text{order\_item\_id})$$
$$\text{distinct\_sellers} = \text{nunique}(\text{seller\_id})$$
$$\text{primary\_seller\_id} = \text{first}(\text{seller\_id})$$
$$\text{primary\_product\_id} = \text{first}(\text{product\_id})$$
$$\text{freight\_ratio} = \frac{\text{total\_freight}}{\text{total\_price}}$$

### 3.2 Order Payments Aggregation (`order_payments_agg`)
Group `order_payments.csv` by `order_id` to create a 1:1 financial summary:
$$\text{total\_payment\_value} = \sum(\text{payment\_value})$$
$$\text{max\_installments} = \max(\text{payment\_installments})$$
$$\text{payment\_sequential\_count} = \max(\text{payment\_sequential})$$
$$\text{payment\_methods\_distinct} = \text{nunique}(\text{payment\_type})$$
$$\text{primary\_payment\_type} = \text{payment\_type with maximum payment\_value}$$

### 3.3 Order Reviews Deduplication (`order_reviews_agg`)
Group `order_reviews.csv` by `order_id`:
- Sort reviews by `review_answer_timestamp desc`.
- Select the latest review record per `order_id` to obtain:
  - `review_score`: rating from 1 to 5.
  - `review_comment_title`: customer comment title.
  - `review_comment_message`: customer feedback text.
  - `review_answer_timestamp`: survey submission timestamp.

### 3.4 Geolocation Coordinates Aggregation (`geolocation_agg`)
Group `geolocation.csv` by `geolocation_zip_code_prefix` (19,015 unique ZIP prefixes):
$$\text{customer\_lat} / \text{seller\_lat} = \text{mean}(\text{geolocation\_lat})$$
$$\text{customer\_lng} / \text{seller\_lng} = \text{mean}(\text{geolocation\_lng})$$

---

## 4. Dangerous Join Pitfalls & Anti-Patterns

> [!CAUTION]
> **Cartesian Explosion on Raw Geolocation Join**:
> Joining `customers` (99k rows) or `sellers` (3k rows) directly to raw `geolocation` (1.0M rows) creates millions of duplicate rows because ZIP prefixes are not unique.
> **Rule**: NEVER join `geolocation` without grouping by `geolocation_zip_code_prefix` first.

> [!WARNING]
> **GMV Duplication on Direct Items Join**:
> Joining raw `order_items` (112,650 rows) directly to `orders` (99,441 rows) inflates order counts by +13.3% and duplicates order payments, review scores, and delivery statuses.
> **Rule**: ALWAYS aggregate `order_items` to `order_id` before joining to `orders`.

> [!WARNING]
> **Financial Double-Counting on Direct Payments Join**:
> Joining raw `order_payments` (103,886 rows) directly to `orders` duplicates line items and freight values for multi-payment orders.
> **Rule**: ALWAYS aggregate `order_payments` to `order_id` before joining to `orders`.

---

## 5. Recommended Join Sequence Architecture

```
Step 1: Base Order Spine (orders.csv - 99,441 rows)
   │
   ├── Step 2: LEFT JOIN order_items_agg (aggregated on order_id)
   │
   ├── Step 3: LEFT JOIN order_payments_agg (aggregated on order_id)
   │
   ├── Step 4: LEFT JOIN order_reviews_agg (deduplicated on order_id)
   │
   ├── Step 5: LEFT JOIN customers.csv (on customer_id)
   │    │
   │    └── Step 6: LEFT JOIN geolocation_agg (on customer_zip_code_prefix)
   │
   ├── Step 7: LEFT JOIN products.csv (on primary_product_id)
   │    │
   │    └── Step 8: LEFT JOIN category_translation.csv (on product_category_name)
   │
   └── Step 9: LEFT JOIN sellers.csv (on primary_seller_id)
        │
        └── Step 10: LEFT JOIN geolocation_agg (on seller_zip_code_prefix)
```

---

## 6. Visual Entity-Relationship Diagram (Mermaid)

```mermaid
erDiagram
    ORDERS {
        string order_id PK
        string customer_id FK
        string order_status
        datetime order_purchase_timestamp
        datetime order_approved_at
        datetime order_delivered_carrier_date
        datetime order_delivered_customer_date
        datetime order_estimated_delivery_date
    }

    CUSTOMERS {
        string customer_id PK
        string customer_unique_id
        int customer_zip_code_prefix FK
        string customer_city
        string customer_state
    }

    ORDER_ITEMS_AGG {
        string order_id PK_FK
        float total_price
        float total_freight
        float total_order_value
        int item_count
        string primary_product_id FK
        string primary_seller_id FK
    }

    ORDER_PAYMENTS_AGG {
        string order_id PK_FK
        float total_payment_value
        int max_installments
        string primary_payment_type
        int payment_sequential_count
    }

    ORDER_REVIEWS_AGG {
        string order_id PK_FK
        float review_score
        string review_comment_title
        string review_comment_message
        datetime review_answer_timestamp
    }

    PRODUCTS {
        string product_id PK
        string product_category_name FK
        float product_weight_g
        float product_length_cm
        float product_height_cm
        float product_width_cm
    }

    SELLERS {
        string seller_id PK
        int seller_zip_code_prefix FK
        string seller_city
        string seller_state
    }

    CATEGORY_TRANSLATION {
        string product_category_name PK
        string product_category_name_english
    }

    GEOLOCATION_AGG {
        int geolocation_zip_code_prefix PK
        float geo_lat
        float geo_lng
    }

    ORDERS ||--|| CUSTOMERS : "1:1 via customer_id"
    ORDERS ||--o| ORDER_ITEMS_AGG : "1:1 via order_id (Aggregated)"
    ORDERS ||--o| ORDER_PAYMENTS_AGG : "1:1 via order_id (Aggregated)"
    ORDERS ||--o| ORDER_REVIEWS_AGG : "1:1 via order_id (Latest)"
    ORDER_ITEMS_AGG }|--|| PRODUCTS : "N:1 via primary_product_id"
    ORDER_ITEMS_AGG }|--|| SELLERS : "N:1 via primary_seller_id"
    PRODUCTS }|--o| CATEGORY_TRANSLATION : "N:1 via product_category_name"
    CUSTOMERS }|--o| GEOLOCATION_AGG : "N:1 via customer_zip_code_prefix"
    SELLERS }|--o| GEOLOCATION_AGG : "N:1 via seller_zip_code_prefix"
```
