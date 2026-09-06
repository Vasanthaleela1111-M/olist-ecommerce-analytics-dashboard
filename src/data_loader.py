"""
Olist Hackathon Data Loader & Integrity Auditor
Loads raw CSV datasets from the data/ directory, performs comprehensive data integrity audits,
and provides standardized dataframes for feature engineering and downstream analysis.
"""

import os
import pandas as pd
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

def get_raw_filepath(filename_keyword):
    """Locates raw file inside data/ directory matching keyword."""
    for f in os.listdir(DATA_DIR):
        if filename_keyword.lower() in f.lower() and f.endswith('.csv'):
            return os.path.join(DATA_DIR, f)
    raise FileNotFoundError(f"Could not find raw CSV matching '{filename_keyword}' in {DATA_DIR}")

def load_raw_data():
    """Loads all raw Olist CSV datasets into a dictionary of DataFrames."""
    datasets = {
        'orders': pd.read_csv(get_raw_filepath('orders.csv')),
        'order_items': pd.read_csv(get_raw_filepath('order_items.csv')),
        'order_payments': pd.read_csv(get_raw_filepath('order_payments.csv')),
        'order_reviews': pd.read_csv(get_raw_filepath('order_reviews.csv')),
        'customers': pd.read_csv(get_raw_filepath('customers.csv')),
        'products': pd.read_csv(get_raw_filepath('products.csv')),
        'sellers': pd.read_csv(get_raw_filepath('sellers.csv')),
        'geolocation': pd.read_csv(get_raw_filepath('geolocation.csv')),
        'category_translation': pd.read_csv(get_raw_filepath('category_translation.csv'))
    }
    return datasets

def audit_data_integrity(datasets=None):
    """
    Performs full data integrity audit across all datasets.
    Reports row counts, unique key counts, missing value counts, and duplicates.
    """
    if datasets is None:
        datasets = load_raw_data()
    
    audit_records = []
    
    key_mapping = {
        'orders': 'order_id',
        'order_items': 'order_id',
        'order_payments': 'order_id',
        'order_reviews': 'review_id',
        'customers': 'customer_id',
        'products': 'product_id',
        'sellers': 'seller_id',
        'geolocation': 'geolocation_zip_code_prefix',
        'category_translation': 'product_category_name'
    }
    
    for name, df in datasets.items():
        primary_key = key_mapping.get(name, df.columns[0])
        audit_records.append({
            'dataset': name,
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'primary_key_column': primary_key,
            'unique_keys': df[primary_key].nunique() if primary_key in df.columns else np.nan,
            'null_values_total': int(df.isnull().sum().sum()),
            'null_columns_count': int((df.isnull().sum() > 0).sum()),
            'duplicate_full_rows': int(df.duplicated().sum())
        })
    
    audit_df = pd.DataFrame(audit_records)
    return audit_df

if __name__ == '__main__':
    print("Testing Data Loader & Audit...")
    datasets = load_raw_data()
    audit_df = audit_data_integrity(datasets)
    print("\n--- DATA INTEGRITY AUDIT SUMMARY ---")
    print(audit_df.to_string(index=False))
