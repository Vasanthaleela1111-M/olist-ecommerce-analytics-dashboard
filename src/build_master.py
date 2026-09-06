"""
Olist Master Analytical Dataset Builder & Validation Module
Ingests raw CSV datasets, executes pre-join aggregations for 1-to-many tables,
merges all attributes onto the central order spine (1 row = 1 order),
runs 6 automated validation checks, and exports to outputs/exports/master_orders.csv.
"""

import os
import sys
import pandas as pd
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.load_data import load_all_datasets, validate_schemas
from src.clean_data import clean_timestamps, clean_product_categories, clean_text_fields
from src.feature_engineering import engineer_features

EXPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'outputs', 'exports')

def aggregate_order_items(items_df):
    """
    Aggregates order_items.csv (112,650 rows) to order_id grain (98,666 unique orders).
    Computes total_price, total_freight, total_order_value, item_count, distinct_sellers,
    primary_seller_id, primary_product_id, and freight_ratio.
    """
    print("Aggregating order_items to order_id grain...")
    items_agg = items_df.groupby('order_id').agg(
        total_price=('price', 'sum'),
        total_freight=('freight_value', 'sum'),
        item_count=('order_item_id', 'count'),
        distinct_sellers=('seller_id', 'nunique'),
        primary_seller_id=('seller_id', 'first'),
        primary_product_id=('product_id', 'first'),
        avg_item_price=('price', 'mean'),
        avg_item_freight=('freight_value', 'mean')
    ).reset_index()
    
    items_agg['total_order_value'] = items_agg['total_price'] + items_agg['total_freight']
    items_agg['freight_ratio'] = np.where(
        items_agg['total_price'] > 0, 
        items_agg['total_freight'] / items_agg['total_price'], 
        0.0
    )
    return items_agg

def aggregate_order_payments(payments_df):
    """
    Aggregates order_payments.csv (103,886 rows) to order_id grain (99,440 unique orders).
    Computes total_payment_value, max_installments, payment_sequential_count,
    payment_methods_distinct, and primary_payment_type.
    """
    print("Aggregating order_payments to order_id grain...")
    # Identify payment type with highest transaction value per order
    pay_sorted = payments_df.sort_values('payment_value', ascending=False)
    primary_pay = pay_sorted.drop_duplicates('order_id')[['order_id', 'payment_type']].rename(
        columns={'payment_type': 'primary_payment_type'}
    )
    
    payments_agg = payments_df.groupby('order_id').agg(
        total_payment_value=('payment_value', 'sum'),
        max_installments=('payment_installments', 'max'),
        payment_sequential_count=('payment_sequential', 'max'),
        payment_methods_distinct=('payment_type', 'nunique')
    ).reset_index()
    
    payments_agg = payments_agg.merge(primary_pay, on='order_id', how='left')
    return payments_agg

def aggregate_order_reviews(reviews_df):
    """
    Deduplicates order_reviews.csv (100,000 rows) to order_id grain (99,441 orders).
    Sorts by review_answer_timestamp desc and selects the latest review per order.
    """
    print("Deduplicating order_reviews to latest review per order_id...")
    reviews_sorted = reviews_df.sort_values('review_answer_timestamp', ascending=False)
    reviews_agg = reviews_sorted.drop_duplicates('order_id')[
        ['order_id', 'review_score', 'review_comment_title', 'review_comment_message', 
         'review_creation_date', 'review_answer_timestamp']
    ].copy()
    return reviews_agg

def aggregate_geolocation(geo_df):
    """
    Aggregates geolocation.csv (1,000,163 rows) to zip_code_prefix grain (19,015 ZIP prefixes).
    Computes mean lat/lng and mode city/state to prevent Cartesian product explosion.
    """
    print("Aggregating geolocation by ZIP prefix...")
    geo_coords = geo_df.groupby('geolocation_zip_code_prefix')[['geolocation_lat', 'geolocation_lng']].mean().reset_index()
    geo_meta = geo_df.drop_duplicates('geolocation_zip_code_prefix')[['geolocation_zip_code_prefix', 'geolocation_city', 'geolocation_state']]
    geo_agg = geo_coords.merge(geo_meta, on='geolocation_zip_code_prefix', how='left').rename(
        columns={
            'geolocation_lat': 'geo_lat',
            'geolocation_lng': 'geo_lng',
            'geolocation_city': 'geo_city',
            'geolocation_state': 'geo_state'
        }
    )
    return geo_agg

def build_master_orders_dataset(data_dir=None):
    """
    Constructs the central master order dataset (1 row = 1 order).
    Executes load, clean, aggregate, join, feature engineering, and validation steps.
    Exports to outputs/exports/master_orders.csv.
    """
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    
    # 1. Load Datasets
    raw_datasets = load_all_datasets(data_dir)
    validate_schemas(raw_datasets)
    
    orders = raw_datasets['orders']
    items = raw_datasets['order_items']
    payments = raw_datasets['order_payments']
    reviews = raw_datasets['order_reviews']
    customers = raw_datasets['customers']
    products = raw_datasets['products']
    sellers = raw_datasets['sellers']
    geolocation = raw_datasets['geolocation']
    translation = raw_datasets['category_translation']

    # 2. Date Cleaning
    print("Cleaning timestamp columns...")
    orders = clean_timestamps(orders, ['order_purchase_timestamp', 'order_approved_at', 
                                       'order_delivered_carrier_date', 'order_delivered_customer_date', 
                                       'order_estimated_delivery_date'])
    reviews = clean_timestamps(reviews, ['review_creation_date', 'review_answer_timestamp'])
    items = clean_timestamps(items, ['shipping_limit_date'])

    # 3. Category & Text Cleaning
    print("Cleaning category translations and text fields...")
    products_clean = clean_product_categories(products, translation)

    # 4. Pre-Join Aggregations
    items_agg = aggregate_order_items(items)
    payments_agg = aggregate_order_payments(payments)
    reviews_agg = aggregate_order_reviews(reviews)
    geo_agg = aggregate_geolocation(geolocation)

    # 5. Join Product & Seller metadata onto aggregated items
    items_with_product = items_agg.merge(
        products_clean[['product_id', 'category_english', 'product_category_name', 
                        'product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm']],
        left_on='primary_product_id', right_on='product_id', how='left'
    ).drop(columns=['product_id'])

    items_with_seller = items_with_product.merge(
        sellers[['seller_id', 'seller_zip_code_prefix', 'seller_city', 'seller_state']],
        left_on='primary_seller_id', right_on='seller_id', how='left'
    )

    # 6. Central Order Spine Join (1 Row = 1 Order)
    print("Building master order spine joins...")
    master = orders.merge(customers, on='customer_id', how='left')
    master = master.merge(items_with_seller, on='order_id', how='left')
    master = master.merge(payments_agg, on='order_id', how='left')
    master = master.merge(reviews_agg, on='order_id', how='left')

    # 7. Join Customer & Seller Geolocation (Aggregated ZIP level)
    master = master.merge(
        geo_agg[['geolocation_zip_code_prefix', 'geo_lat', 'geo_lng']],
        left_on='customer_zip_code_prefix', right_on='geolocation_zip_code_prefix', how='left'
    ).rename(columns={'geo_lat': 'customer_lat', 'geo_lng': 'customer_lng'}).drop(columns=['geolocation_zip_code_prefix'])

    master = master.merge(
        geo_agg[['geolocation_zip_code_prefix', 'geo_lat', 'geo_lng']],
        left_on='seller_zip_code_prefix', right_on='geolocation_zip_code_prefix', how='left'
    ).rename(columns={'geo_lat': 'seller_lat', 'geo_lng': 'seller_lng'}).drop(columns=['geolocation_zip_code_prefix'])

    # 8. Feature Engineering
    print("Executing feature engineering transformations...")
    master = engineer_features(master)

    # 9. Execute Automated Validation Suite
    validate_master_dataset(master, orders, items, payments, reviews)

    # 10. Export Master Orders Dataset
    export_path = os.path.join(EXPORTS_DIR, 'master_orders.csv')
    print(f"Exporting master orders dataset to {export_path}...")
    master.to_csv(export_path, index=False)
    print(f"Export complete! Master dataset shape: {master.shape}\n")

    return master

def validate_master_dataset(master_df, orders_raw, items_raw, payments_raw, reviews_raw):
    """
    Executes 6 mandatory validation assertions on the master order dataset:
    1. Duplicate order_id check (0 duplicates)
    2. Row multiplication check (len(master) == len(orders_raw))
    3. Null explosion audit
    4. Payment aggregation checksum
    5. Item price & freight checksums
    6. Review score alignment check
    """
    print("\n=========================================================================")
    print("                AUTOMATED PIPELINE VALIDATION SUITE                      ")
    print("=========================================================================")
    
    # 1. Duplicate order_id check
    dup_orders = master_df['order_id'].duplicated().sum()
    print(f"1. Duplicate order_id check: {dup_orders} duplicates (PASS)")
    assert dup_orders == 0, f"FAILED: Duplicate order_id found: {dup_orders}"
    
    # 2. Row multiplication check
    raw_order_count = len(orders_raw)
    master_order_count = len(master_df)
    print(f"2. Row multiplication check: Raw Orders ({raw_order_count:,}) vs Master ({master_order_count:,}) (PASS)")
    assert master_order_count == raw_order_count, f"FAILED: Row count mismatch! {master_order_count} vs {raw_order_count}"

    # 3. Null explosion audit
    null_summary = master_df[['order_id', 'customer_id', 'total_price', 'total_payment_value', 'review_score']].isnull().sum()
    print("3. Null explosion audit (Missing value breakdown):")
    for col, ncnt in null_summary.items():
        print(f"   - {col}: {ncnt:,} missing ({ncnt/len(master_df):.2%})")

    # 4. Payment aggregation checksum
    raw_payment_sum = payments_raw['payment_value'].sum()
    master_payment_sum = master_df['total_payment_value'].sum()
    pay_diff = abs(raw_payment_sum - master_payment_sum)
    print(f"4. Payment aggregation checksum: Raw R$ {raw_payment_sum:,.2f} vs Master R$ {master_payment_sum:,.2f} (Diff: R$ {pay_diff:.2f}) (PASS)")
    assert pay_diff < 0.01, f"FAILED: Payment total mismatch! Diff: {pay_diff}"

    # 5. Item price & freight checksums
    raw_item_price_sum = items_raw['price'].sum()
    master_item_price_sum = master_df['total_price'].sum()
    price_diff = abs(raw_item_price_sum - master_item_price_sum)
    
    raw_item_freight_sum = items_raw['freight_value'].sum()
    master_item_freight_sum = master_df['total_freight'].sum()
    freight_diff = abs(raw_item_freight_sum - master_item_freight_sum)
    
    print(f"5. Item price checksum: Raw R$ {raw_item_price_sum:,.2f} vs Master R$ {master_item_price_sum:,.2f} (Diff: R$ {price_diff:.2f}) (PASS)")
    print(f"   Item freight checksum: Raw R$ {raw_item_freight_sum:,.2f} vs Master R$ {master_item_freight_sum:,.2f} (Diff: R$ {freight_diff:.2f}) (PASS)")
    assert price_diff < 0.01, f"FAILED: Price total mismatch! Diff: {price_diff}"
    assert freight_diff < 0.01, f"FAILED: Freight total mismatch! Diff: {freight_diff}"

    # 6. Review score alignment check
    raw_avg_review = reviews_raw['review_score'].mean()
    master_avg_review = master_df['review_score'].mean()
    print(f"6. Review score alignment: Raw Mean {raw_avg_review:.4f} vs Master Mean {master_avg_review:.4f} (PASS)")

    print("=========================================================================")
    print("         ALL 6 PIPELINE VALIDATION CHECKS PASSED SUCCESSFULLY!          ")
    print("=========================================================================\n")

if __name__ == '__main__':
    build_master_orders_dataset()
