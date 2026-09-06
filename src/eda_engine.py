"""
Olist Exploratory Data Analysis (EDA) Engine
Executes statistical distribution analysis, Tukey outlier detection (1.5x IQR),
tabular exports, and chart generation across 7 core operational dimensions:
A. Marketplace, B. Delivery, C. Customer, D. Seller, E. Geography, F. Product Category, G. Payments.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.visualization import set_chart_style, annotate_bars, save_chart, PALETTE

OUTPUT_TABLES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'outputs', 'tables')
OUTPUT_CHARTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'outputs', 'charts')
MASTER_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'outputs', 'exports', 'master_orders.csv')

def calculate_distribution_stats(series, metric_name="Metric"):
    """
    Computes parametric and non-parametric distribution statistics,
    including Tukey 1.5x IQR outlier detection bounds and counts.
    """
    valid_s = series.dropna()
    n = len(valid_s)
    if n == 0:
        return {}
    
    mean_val = valid_s.mean()
    std_val = valid_s.std()
    median_val = valid_s.median()
    p25 = valid_s.quantile(0.25)
    p75 = valid_s.quantile(0.75)
    iqr = p75 - p25
    
    lower_bound = p25 - 1.5 * iqr
    upper_bound = p75 + 1.5 * iqr
    
    outliers_low = (valid_s < lower_bound).sum()
    outliers_high = (valid_s > upper_bound).sum()
    total_outliers = outliers_low + outliers_high
    outlier_pct = (total_outliers / n) * 100
    
    return {
        'metric_name': metric_name,
        'count_n': n,
        'mean': round(mean_val, 4),
        'std': round(std_val, 4),
        'min': round(valid_s.min(), 4),
        'p25': round(p25, 4),
        'median': round(median_val, 4),
        'p75': round(p75, 4),
        'max': round(valid_s.max(), 4),
        'iqr': round(iqr, 4),
        'tukey_lower_bound': round(lower_bound, 4),
        'tukey_upper_bound': round(upper_bound, 4),
        'outliers_high_count': int(outliers_high),
        'outliers_low_count': int(outliers_low),
        'total_outliers_count': int(total_outliers),
        'outlier_pct': round(outlier_pct, 2)
    }

def run_eda_pipeline():
    """Main execution function for full 7-dimension EDA."""
    os.makedirs(OUTPUT_TABLES, exist_ok=True)
    os.makedirs(OUTPUT_CHARTS, exist_ok=True)
    
    print("Ingesting master order dataset for EDA...")
    df = pd.read_csv(MASTER_PATH)
    
    # Parse dates if needed
    date_cols = ['order_purchase_timestamp', 'order_approved_at', 
                 'order_delivered_carrier_date', 'order_delivered_customer_date', 
                 'order_estimated_delivery_date']
    for c in date_cols:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c])
            
    eda_stats_list = []
    
    print("\n--- SECTION A: MARKETPLACE EDA ---")
    s_price = calculate_distribution_stats(df['total_price'], "Total Item Price per Order (R$)")
    s_freight = calculate_distribution_stats(df['total_freight'], "Total Freight Cost per Order (R$)")
    s_tot_val = calculate_distribution_stats(df['total_order_value'], "Total Order Value (R$)")
    eda_stats_list.extend([s_price, s_freight, s_tot_val])
    
    rev_dist = df['review_score'].value_counts(dropna=False).reset_index()
    rev_dist.columns = ['review_score', 'count']
    rev_dist['share_pct'] = round((rev_dist['count'] / len(df)) * 100, 2)
    rev_dist.to_csv(os.path.join(OUTPUT_TABLES, 'eda_marketplace_review_dist.csv'), index=False)

    print("\n--- SECTION B: DELIVERY EDA ---")
    deliv = df[df['order_status'] == 'delivered'].copy()
    s_lead = calculate_distribution_stats(deliv['delivery_lead_time_days'], "Actual Delivery Lead Time (Days)")
    s_est_lead = calculate_distribution_stats(deliv['estimated_lead_time_days'], "Estimated Delivery Lead Time (Days)")
    s_delay = calculate_distribution_stats(deliv['delivery_delay_days'], "Delivery Delay Days (Actual - Estimated)")
    eda_stats_list.extend([s_lead, s_est_lead, s_delay])
    
    # Chart B: Delivery Lead Time Boxplot (Tukey Outliers Visual)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(data=deliv[['delivery_lead_time_days', 'estimated_lead_time_days']], ax=ax, palette=[PALETTE['secondary'], PALETTE['primary']])
    set_chart_style(ax, title='Delivery Lead Times Distribution & Outlier Spread', xlabel='Metric', ylabel='Days')
    ax.set_xticklabels(['Actual Lead Time', 'Estimated Lead Time'])
    ax.set_ylim(-5, 60)
    save_chart(fig, 'eda_delivery_lead_time_boxplot.png', OUTPUT_CHARTS)

    print("\n--- SECTION C: CUSTOMER EDA ---")
    cust_orders = df.groupby('customer_unique_id')['order_id'].count()
    s_cust_freq = calculate_distribution_stats(cust_orders, "Orders per Customer Unique ID")
    eda_stats_list.append(s_cust_freq)
    
    repeat_buyers_cnt = (cust_orders > 1).sum()
    total_buyers_cnt = len(cust_orders)
    repeat_rate_pct = (repeat_buyers_cnt / total_buyers_cnt) * 100
    
    cust_freq_table = cust_orders.value_counts().reset_index()
    cust_freq_table.columns = ['orders_count', 'customer_count']
    cust_freq_table['buyer_share_pct'] = round((cust_freq_table['customer_count'] / total_buyers_cnt) * 100, 2)
    cust_freq_table.to_csv(os.path.join(OUTPUT_TABLES, 'eda_customer_order_frequency.csv'), index=False)

    print("\n--- SECTION D: SELLER EDA ---")
    seller_summary = df.groupby('primary_seller_id').agg(
        order_count=('order_id', 'count'),
        total_gmv=('total_price', 'sum'),
        avg_review_score=('review_score', 'mean'),
        late_rate_pct=('is_late', lambda x: x.mean() * 100)
    ).reset_index()
    s_seller_orders = calculate_distribution_stats(seller_summary['order_count'], "Order Volume per Seller")
    s_seller_gmv = calculate_distribution_stats(seller_summary['total_gmv'], "Total GMV per Seller (R$)")
    eda_stats_list.extend([s_seller_orders, s_seller_gmv])
    seller_summary.to_csv(os.path.join(OUTPUT_TABLES, 'eda_seller_distributions.csv'), index=False)

    print("\n--- SECTION E: GEOGRAPHY EDA ---")
    state_summary = df.groupby('customer_state').agg(
        order_count=('order_id', 'count'),
        total_gmv=('total_price', 'sum'),
        avg_freight=('total_freight', 'mean'),
        avg_lead_time=('delivery_lead_time_days', 'mean'),
        late_rate_pct=('is_late', lambda x: (x == 1).mean() * 100)
    ).reset_index().sort_values('order_count', ascending=False)
    state_summary.to_csv(os.path.join(OUTPUT_TABLES, 'eda_geographic_state_summary.csv'), index=False)

    print("\n--- SECTION F: PRODUCT CATEGORY EDA ---")
    cat_summary = df.groupby('category_english').agg(
        order_count=('order_id', 'count'),
        total_gmv=('total_price', 'sum'),
        avg_price=('total_price', 'mean'),
        avg_freight=('total_freight', 'mean'),
        avg_review_score=('review_score', 'mean')
    ).reset_index()
    cat_filtered = cat_summary[cat_summary['order_count'] >= 50].sort_values('total_gmv', ascending=False)
    cat_filtered.to_csv(os.path.join(OUTPUT_TABLES, 'eda_product_category_distributions.csv'), index=False)

    print("\n--- SECTION G: PAYMENTS EDA ---")
    pay_summary = df.groupby('primary_payment_type').agg(
        order_count=('order_id', 'count'),
        total_value=('total_payment_value', 'sum'),
        avg_order_value=('total_payment_value', 'mean'),
        median_order_value=('total_payment_value', 'median'),
        avg_review_score=('review_score', 'mean')
    ).reset_index().sort_values('order_count', ascending=False)
    pay_summary.to_csv(os.path.join(OUTPUT_TABLES, 'eda_payment_distributions.csv'), index=False)

    # Save overall distribution statistics table
    df_dist_all = pd.DataFrame(eda_stats_list)
    df_dist_all.to_csv(os.path.join(OUTPUT_TABLES, 'eda_overall_distribution_statistics.csv'), index=False)
    print(f"Saved all distribution stats to {os.path.join(OUTPUT_TABLES, 'eda_overall_distribution_statistics.csv')}")
    
    return df, df_dist_all, state_summary, cat_filtered, pay_summary

if __name__ == '__main__':
    run_eda_pipeline()
