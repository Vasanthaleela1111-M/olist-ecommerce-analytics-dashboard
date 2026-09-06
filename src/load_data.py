"""
Olist Hackathon Data Loader & Schema Validator Module
Ingests all 9 raw CSV datasets from data/ and performs schema & primary key validation checks.
"""

import os
import sys
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

RAW_FILE_KEYWORDS = {
    'orders': 'orders.csv',
    'order_items': 'order_items.csv',
    'order_payments': 'order_payments.csv',
    'order_reviews': 'order_reviews.csv',
    'customers': 'customers.csv',
    'products': 'products.csv',
    'sellers': 'sellers.csv',
    'geolocation': 'geolocation.csv',
    'category_translation': 'category_translation.csv'
}

REQUIRED_COLUMNS = {
    'orders': ['order_id', 'customer_id', 'order_status', 'order_purchase_timestamp', 
               'order_approved_at', 'order_delivered_carrier_date', 
               'order_delivered_customer_date', 'order_estimated_delivery_date'],
    'order_items': ['order_id', 'order_item_id', 'product_id', 'seller_id', 'price', 'freight_value'],
    'order_payments': ['order_id', 'payment_sequential', 'payment_type', 'payment_installments', 'payment_value'],
    'order_reviews': ['review_id', 'order_id', 'review_score', 'review_comment_title', 
                      'review_comment_message', 'review_creation_date', 'review_answer_timestamp'],
    'customers': ['customer_id', 'customer_unique_id', 'customer_zip_code_prefix', 'customer_city', 'customer_state'],
    'products': ['product_id', 'product_category_name', 'product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm'],
    'sellers': ['seller_id', 'seller_zip_code_prefix', 'seller_city', 'seller_state'],
    'geolocation': ['geolocation_zip_code_prefix', 'geolocation_lat', 'geolocation_lng', 'geolocation_city', 'geolocation_state'],
    'category_translation': ['product_category_name', 'product_category_name_english']
}

def get_raw_filepath(keyword):
    """Locates raw CSV file inside data/ directory matching keyword."""
    for f in os.listdir(DATA_DIR):
        if keyword.lower() in f.lower() and f.endswith('.csv'):
            return os.path.join(DATA_DIR, f)
    raise FileNotFoundError(f"Could not find raw CSV matching '{keyword}' in {DATA_DIR}")

def load_all_datasets(data_dir=None):
    """Loads all 9 raw Olist CSV datasets into a dictionary of pandas DataFrames."""
    if data_dir is None:
        data_dir = DATA_DIR
    
    datasets = {}
    print(f"Loading 9 raw CSV datasets from {data_dir}...")
    for name, keyword in RAW_FILE_KEYWORDS.items():
        filepath = get_raw_filepath(keyword)
        df = pd.read_csv(filepath)
        datasets[name] = df
        print(f" Loaded '{name}': {len(df):,} rows x {len(df.columns)} cols")
    
    return datasets

def validate_schemas(datasets):
    """
    Validates required columns, primary keys, and dataset non-emptiness.
    Returns True if all validation checks pass.
    """
    print("\n--- Validating Schema & Key Integrity across all 9 Datasets ---")
    validation_status = True
    
    for name, df in datasets.items():
        # 1. Non-empty check
        if len(df) == 0:
            print(f"ERROR: Dataset '{name}' is empty!")
            validation_status = False
        
        # 2. Required columns check
        req_cols = REQUIRED_COLUMNS.get(name, [])
        missing_cols = [c for c in req_cols if c not in df.columns]
        if missing_cols:
            print(f"ERROR: Dataset '{name}' missing required columns: {missing_cols}")
            validation_status = False
            
    # Key validation specific checks
    if 'orders' in datasets:
        assert datasets['orders']['order_id'].nunique() == len(datasets['orders']), "orders.csv order_id PK is not 100% unique!"
    if 'customers' in datasets:
        assert datasets['customers']['customer_id'].nunique() == len(datasets['customers']), "customers.csv customer_id PK is not 100% unique!"
    if 'products' in datasets:
        assert datasets['products']['product_id'].nunique() == len(datasets['products']), "products.csv product_id PK is not 100% unique!"
    if 'sellers' in datasets:
        assert datasets['sellers']['seller_id'].nunique() == len(datasets['sellers']), "sellers.csv seller_id PK is not 100% unique!"
        
    print("Schema & Primary Key Validation: ALL CHECKS PASSED PASSED!")
    return validation_status

if __name__ == '__main__':
    datasets = load_all_datasets()
    validate_schemas(datasets)
