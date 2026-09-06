"""
Olist Analytics Metrics Module
Contains calculation routines for marketplace performance, delivery satisfaction,
seller concentration, category benchmarks, payment behavior, and low-review risk factors.
"""

import pandas as pd
import numpy as np

def compute_marketplace_metrics(df):
    """Calculates overall marketplace revenue, volume, and AOV metrics."""
    valid_df = df[df['order_purchase_timestamp'].notnull()].copy()
    
    total_gmv = valid_df['total_price'].sum()
    total_freight = valid_df['total_freight'].sum()
    total_revenue = valid_df['total_order_value'].sum()
    total_orders = len(valid_df)
    item_aov = total_gmv / valid_df['total_price'].count()
    total_aov = total_revenue / valid_df['total_order_value'].count()
    
    return {
        'total_gmv_rs': round(total_gmv, 2),
        'total_freight_rs': round(total_freight, 2),
        'total_revenue_rs': round(total_revenue, 2),
        'total_orders': total_orders,
        'item_aov_rs': round(item_aov, 2),
        'total_aov_rs': round(total_aov, 2)
    }

def compute_delivery_metrics(df):
    """Calculates delivery lead times, on-time rates, and review score correlations."""
    delivered = df[
        (df['order_status'] == 'delivered') & 
        (df['order_delivered_customer_date'].notnull()) & 
        (df['order_estimated_delivery_date'].notnull())
    ].copy()
    
    total_delivered = len(delivered)
    ontime_count = (delivered['is_late'] == 0).sum()
    late_count = (delivered['is_late'] == 1).sum()
    
    ontime_rate = (ontime_count / total_delivered) * 100
    late_rate = (late_count / total_delivered) * 100
    
    avg_actual_lead = delivered['delivery_lead_time_days'].mean()
    avg_est_lead = delivered['estimated_lead_time_days'].mean()
    
    avg_rev_ontime = delivered[delivered['is_late'] == 0]['review_score'].mean()
    avg_rev_late = delivered[delivered['is_late'] == 1]['review_score'].mean()
    
    pct_1star_ontime = (delivered[delivered['is_late'] == 0]['review_score'] == 1).mean() * 100
    pct_1star_late = (delivered[delivered['is_late'] == 1]['review_score'] == 1).mean() * 100
    
    valid_corr = delivered.dropna(subset=['delivery_delay_days', 'review_score'])
    delay_review_corr = valid_corr['delivery_delay_days'].corr(valid_corr['review_score'])
    
    return {
        'total_delivered_orders': total_delivered,
        'ontime_rate_pct': round(ontime_rate, 2),
        'late_rate_pct': round(late_rate, 2),
        'avg_actual_lead_time_days': round(avg_actual_lead, 2),
        'avg_estimated_lead_time_days': round(avg_est_lead, 2),
        'avg_review_score_ontime': round(avg_rev_ontime, 2),
        'avg_review_score_late': round(avg_rev_late, 2),
        'pct_1star_ontime': round(pct_1star_ontime, 2),
        'pct_1star_late': round(pct_1star_late, 2),
        'delay_review_corr_r': round(delay_review_corr, 4)
    }

def compute_seller_pareto_metrics(df):
    """Calculates seller GMV concentration (Pareto principle)."""
    seller_gmv = df.groupby('primary_seller_id')['total_price'].sum().sort_values(ascending=False)
    total_active_sellers = len(seller_gmv)
    overall_gmv = seller_gmv.sum()
    
    top_1_pct = int(np.ceil(total_active_sellers * 0.01))
    top_5_pct = int(np.ceil(total_active_sellers * 0.05))
    top_10_pct = int(np.ceil(total_active_sellers * 0.10))
    top_20_pct = int(np.ceil(total_active_sellers * 0.20))
    
    return {
        'total_active_sellers': total_active_sellers,
        'top_1pct_gmv_share_pct': round((seller_gmv.iloc[:top_1_pct].sum() / overall_gmv) * 100, 2),
        'top_5pct_gmv_share_pct': round((seller_gmv.iloc[:top_5_pct].sum() / overall_gmv) * 100, 2),
        'top_10pct_gmv_share_pct': round((seller_gmv.iloc[:top_10_pct].sum() / overall_gmv) * 100, 2),
        'top_20pct_gmv_share_pct': round((seller_gmv.iloc[:top_20_pct].sum() / overall_gmv) * 100, 2)
    }
