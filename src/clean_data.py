"""
Olist Data Cleaning & Preprocessing Module
Handles date parsing, string standardization, missing category fill,
and category translation mapping with fallback controls.
"""

import pandas as pd
import numpy as np

def clean_timestamps(df, timestamp_cols):
    """Converts string date/timestamp columns into datetime objects."""
    df_clean = df.copy()
    for col in timestamp_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
    return df_clean

def clean_product_categories(products_df, translation_df):
    """
    Joins products dataset with category translation dictionary.
    Handles missing category names and unmapped Portuguese categories using fallback.
    """
    prod_clean = products_df.copy()
    trans_clean = translation_df.copy()
    
    # Merge on product_category_name
    merged = prod_clean.merge(trans_clean, on='product_category_name', how='left')
    
    # Fill missing translation with original Portuguese category name, or 'uncategorized'
    merged['category_english'] = merged['product_category_name_english'].fillna(
        merged['product_category_name'].fillna('uncategorized')
    )
    
    return merged

def clean_text_fields(df, text_cols):
    """Strips leading/trailing whitespace and converts empty strings to NaN."""
    df_clean = df.copy()
    for col in text_cols:
        if col in df_clean.columns and df_clean[col].dtype == 'object':
            df_clean[col] = df_clean[col].astype(str).str.strip()
            df_clean[col] = df_clean[col].replace({'': np.nan, 'nan': np.nan, 'None': np.nan})
    return df_clean
