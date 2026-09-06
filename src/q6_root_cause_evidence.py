"""
Script to compute exact evidence metrics for Core Question 6:
Audits candidate factors for low review scores and produces outputs/tables/root_cause_evidence.csv
"""

import os
import pandas as pd
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASTER_CSV = os.path.join(PROJECT_ROOT, 'outputs', 'exports', 'master_orders.csv')
OUTPUT_TABLES = os.path.join(PROJECT_ROOT, 'outputs', 'tables')
os.makedirs(OUTPUT_TABLES, exist_ok=True)

def compute_evidence():
    df = pd.read_csv(MASTER_CSV)
    df_rev = df[df['review_score'].notnull()].copy()
    
    total_n = len(df_rev)
    base_avg_review = df_rev['review_score'].mean()
    df_rev['is_low_rating'] = (df_rev['review_score'] <= 2).astype(int)
    base_low_rate = df_rev['is_low_rating'].mean() * 100
    
    print(f"Platform Baseline: N = {total_n}, Avg Review = {base_avg_review:.4f}, Low Rating Rate = {base_low_rate:.2f}%")
    
    segments = []
    
    def add_segment(factor_name, segment_name, sub_df):
        n = len(sub_df)
        if n == 0:
            return
        avg_rev = sub_df['review_score'].mean()
        low_count = sub_df['is_low_rating'].sum()
        low_rate = (low_count / n) * 100
        abs_diff_pct = low_rate - base_low_rate
        rel_risk = low_rate / base_low_rate if base_low_rate > 0 else 1.0
        
        segments.append({
            'factor_category': factor_name,
            'segment_definition': segment_name,
            'sample_size_n': n,
            'avg_review_score': round(avg_rev, 4),
            'low_rating_count': low_count,
            'low_rating_rate_pct': round(low_rate, 2),
            'baseline_low_rate_pct': round(base_low_rate, 2),
            'abs_diff_pct_pts': round(abs_diff_pct, 2),
            'relative_risk_ratio': round(rel_risk, 2)
        })

    # 1. Delivery Delay
    delivered_df = df_rev[df_rev['order_status'] == 'delivered']
    add_segment('Delivery Delay', 'On-Time / Early Delivery (Delay <= 0 days)', delivered_df[delivered_df['is_late'] == 0])
    add_segment('Delivery Delay', 'Late Delivery (Delay > 0 days)', delivered_df[delivered_df['is_late'] == 1])
    add_segment('Delivery Delay', 'Severe Late Delivery (Delay >= 4 days)', delivered_df[delivered_df['delivery_delay_days'] >= 4])
    add_segment('Delivery Delay', 'Extreme Late Delivery (Delay >= 10 days)', delivered_df[delivered_df['delivery_delay_days'] >= 10])

    # 2. Seller Execution (Carrier Dispatch Lag)
    add_segment('Seller Execution', 'Fast Seller Dispatch (Carrier dispatch <= 5 days)', df_rev[df_rev['carrier_dispatch_days'] <= 5])
    add_segment('Seller Execution', 'Slow Seller Dispatch (Carrier dispatch > 5 days)', df_rev[df_rev['carrier_dispatch_days'] > 5])
    add_segment('Seller Execution', 'Extreme Slow Seller Dispatch (> 10 days)', df_rev[df_rev['carrier_dispatch_days'] > 10])

    # 3. Product Category Hotspots
    add_segment('Category Hotspots', 'Outlier Category: office_furniture', df_rev[df_rev['category_english'] == 'office_furniture'])
    add_segment('Category Hotspots', 'Outlier Category: audio', df_rev[df_rev['category_english'] == 'audio'])
    add_segment('Category Hotspots', 'High-Volume Friction: bed_bath_table', df_rev[df_rev['category_english'] == 'bed_bath_table'])
    add_segment('Category Hotspots', 'High-Volume Friction: furniture_decor', df_rev[df_rev['category_english'] == 'furniture_decor'])
    add_segment('Category Hotspots', 'High-Volume Winner: health_beauty', df_rev[df_rev['category_english'] == 'health_beauty'])
    add_segment('Category Hotspots', 'High-Volume Winner: luggage_accessories', df_rev[df_rev['category_english'] == 'luggage_accessories'])

    # 4. Geography & Route
    add_segment('Geography', 'Intra-State Shipping (Customer state = Seller state)', df_rev[df_rev['is_interstate'] == 0])
    add_segment('Geography', 'Inter-State Shipping (Customer state != Seller state)', df_rev[df_rev['is_interstate'] == 1])
    # Route Hotspot SP -> RJ
    sp_rj = df_rev[(df_rev['seller_state'] == 'SP') & (df_rev['customer_state'] == 'RJ')]
    add_segment('Geography', 'Hotspot Route: SP Seller -> RJ Customer', sp_rj)

    # 5. Freight Burden
    add_segment('Freight Burden', 'Normal Freight Ratio (Freight <= 50% of price)', df_rev[df_rev['freight_ratio'] <= 0.50])
    add_segment('Freight Burden', 'High Freight Ratio (Freight > 50% of price)', df_rev[df_rev['freight_ratio'] > 0.50])

    # 6. Order Value (Price Level)
    add_segment('Order Value', 'Low Item Price (< R$ 50)', df_rev[df_rev['total_price'] < 50])
    add_segment('Order Value', 'Medium Item Price (R$ 50 - R$ 200)', df_rev[(df_rev['total_price'] >= 50) & (df_rev['total_price'] <= 200)])
    add_segment('Order Value', 'High Item Price (> R$ 200)', df_rev[df_rev['total_price'] > 200])

    # 7. Payment Behavior
    add_segment('Payment Behavior', 'Credit Card: 1 Installment (Single Pay)', df_rev[(df_rev['primary_payment_type'] == 'credit_card') & (df_rev['max_installments'] == 1)])
    add_segment('Payment Behavior', 'Credit Card: High Installments (7-10 Installments)', df_rev[(df_rev['primary_payment_type'] == 'credit_card') & (df_rev['max_installments'].between(7, 10))])
    add_segment('Payment Behavior', 'Credit Card: Extreme Installments (11+ Installments)', df_rev[(df_rev['primary_payment_type'] == 'credit_card') & (df_rev['max_installments'] >= 11)])
    add_segment('Payment Behavior', 'Boleto Bancario Payment', df_rev[df_rev['primary_payment_type'] == 'boleto'])

    # 8. Customer / Repeat Behavior
    cust_counts = df_rev['customer_unique_id'].value_counts()
    repeat_cust_ids = cust_counts[cust_counts > 1].index
    single_cust_ids = cust_counts[cust_counts == 1].index
    
    add_segment('Customer Behavior', 'First-Time Customer (Single order)', df_rev[df_rev['customer_unique_id'].isin(single_cust_ids)])
    add_segment('Customer Behavior', 'Repeat Customer (Multiple orders)', df_rev[df_rev['customer_unique_id'].isin(repeat_cust_ids)])

    res_df = pd.DataFrame(segments)
    out_path = os.path.join(OUTPUT_TABLES, 'root_cause_evidence.csv')
    res_df.to_csv(out_path, index=False)
    print(f"Saved root cause evidence table to {out_path}")
    print("\nRoot Cause Evidence Output Preview:")
    print(res_df.to_string())

if __name__ == '__main__':
    compute_evidence()
