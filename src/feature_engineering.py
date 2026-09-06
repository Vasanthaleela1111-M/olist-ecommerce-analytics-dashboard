"""
Olist Feature Engineering Module
Generates delivery lead times, logistics component delays, late flags,
interstate shipping flags, date periods, and delivery delay severity buckets.
"""

import pandas as pd
import numpy as np

def engineer_features(df):
    """Applies feature engineering transformations on master dataset."""
    master = df.copy()
    
    # 1. Delivery Duration Metrics (for delivered orders)
    master['delivery_lead_time_days'] = (master['order_delivered_customer_date'] - master['order_purchase_timestamp']).dt.total_seconds() / 86400.0
    master['estimated_lead_time_days'] = (master['order_estimated_delivery_date'] - master['order_purchase_timestamp']).dt.total_seconds() / 86400.0
    master['delivery_delay_days'] = (master['order_delivered_customer_date'] - master['order_estimated_delivery_date']).dt.total_seconds() / 86400.0
    
    master['is_late'] = np.where(
        master['order_delivered_customer_date'].notnull() & master['order_estimated_delivery_date'].notnull(),
        (master['order_delivered_customer_date'] > master['order_estimated_delivery_date']).astype(int),
        np.nan
    )
    master['delay_magnitude_days'] = np.maximum(0, master['delivery_delay_days'])
    
    # Logistics component phase delays
    master['approval_delay_hours'] = (master['order_approved_at'] - master['order_purchase_timestamp']).dt.total_seconds() / 3600.0
    master['carrier_dispatch_days'] = (master['order_delivered_carrier_date'] - master['order_approved_at']).dt.total_seconds() / 86400.0
    master['carrier_transit_days'] = (master['order_delivered_customer_date'] - master['order_delivered_carrier_date']).dt.total_seconds() / 86400.0

    # Geographic Interstate Flag
    master['is_interstate'] = np.where(
        master['customer_state'].notnull() & master['seller_state'].notnull(),
        (master['customer_state'] != master['seller_state']).astype(int),
        np.nan
    )

    # Date Period Attributes
    master['purchase_year_month'] = master['order_purchase_timestamp'].dt.strftime('%Y-%m')
    master['purchase_year_quarter'] = master['order_purchase_timestamp'].dt.to_period('Q').astype(str)

    # Delay Severity Buckets
    def assign_delay_bucket(row):
        if pd.isnull(row['is_late']):
            return 'Undelivered'
        if row['is_late'] == 0:
            diff = -row['delivery_delay_days'] if pd.notnull(row['delivery_delay_days']) else 0
            if diff >= 10: return '1. Early 10+ days'
            elif diff >= 5: return '2. Early 5-9 days'
            elif diff >= 1: return '3. Early 1-4 days'
            else: return '4. On-Time (0 days)'
        else:
            delay = row['delivery_delay_days']
            if delay <= 3: return '5. Late 1-3 days'
            elif delay <= 7: return '6. Late 4-7 days'
            elif delay <= 14: return '7. Late 8-14 days'
            else: return '8. Late 15+ days'

    master['delay_bucket'] = master.apply(assign_delay_bucket, axis=1)
    
    return master
