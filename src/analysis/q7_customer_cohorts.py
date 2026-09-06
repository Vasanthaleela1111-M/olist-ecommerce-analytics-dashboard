"""
Question 7: Customer Cohort & Repeat Purchase Analysis
Evaluates customer repeat purchase rates, order frequency distribution,
unit economics (AOV, GMV share, review scores) of single vs. repeat buyers,
and computes monthly signup cohort retention matrices across 99,441 orders.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.visualization import set_chart_style, annotate_bars, save_chart, PALETTE, CHART_COLORS

OUTPUT_TABLES = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'outputs', 'tables')
OUTPUT_CHARTS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'outputs', 'charts')

def analyze_customer_cohorts(df):
    """Executes Question 7 Customer Cohort & Repeat Purchase Analysis."""
    print("--- Running Q7: Customer Cohort & Repeat Purchase Analysis ---")
    
    df_valid = df.copy()
    
    # Clean timestamp
    df_valid['purchase_date'] = pd.to_datetime(df_valid['order_purchase_timestamp'])
    df_valid['purchase_year_month'] = df_valid['purchase_date'].dt.to_period('M')
    
    # Calculate Total Revenue per order (price + freight)
    df_valid['order_total_rev'] = df_valid['total_price'].fillna(0) + df_valid['total_freight'].fillna(0)
    
    # 1. CUSTOMER PURCHASE FREQUENCY AGGREGATION
    customer_agg = df_valid.groupby('customer_unique_id').agg(
        total_orders=('order_id', 'nunique'),
        total_spent=('order_total_rev', 'sum'),
        avg_order_value=('order_total_rev', 'mean'),
        first_purchase_date=('purchase_date', 'min'),
        last_purchase_date=('purchase_date', 'max'),
        avg_review_score=('review_score', 'mean')
    ).reset_index()
    
    total_unique_cust = len(customer_agg)
    single_cust = (customer_agg['total_orders'] == 1).sum()
    repeat_cust = (customer_agg['total_orders'] > 1).sum()
    repeat_rate_pct = (repeat_cust / total_unique_cust) * 100
    
    print(f"Total Unique Customers: {total_unique_cust:,}")
    print(f"Single-Purchase Customers: {single_cust:,} ({single_cust/total_unique_cust*100:.2f}%)")
    print(f"Repeat Purchase Customers (2+ Orders): {repeat_cust:,} ({repeat_rate_pct:.2f}%)")
    print(f"Max Orders by Single Customer: {customer_agg['total_orders'].max()}")
    
    # Order Frequency Breakdown Buckets
    def bucket_orders(n):
        if n == 1:
            return '1 Order (Single)'
        elif n == 2:
            return '2 Orders'
        elif n <= 5:
            return '3-5 Orders'
        else:
            return '6+ Orders'
            
    customer_agg['order_bucket'] = customer_agg['total_orders'].apply(bucket_orders)
    
    freq_summary = customer_agg.groupby('order_bucket').agg(
        customer_count=('customer_unique_id', 'count'),
        total_orders_placed=('total_orders', 'sum'),
        total_revenue_generated=('total_spent', 'sum'),
        avg_aov=('avg_order_value', 'mean'),
        avg_review_score=('avg_review_score', 'mean')
    ).reset_index()
    
    freq_summary['pct_customers'] = (freq_summary['customer_count'] / total_unique_cust) * 100
    total_platform_rev = customer_agg['total_spent'].sum()
    freq_summary['pct_revenue'] = (freq_summary['total_revenue_generated'] / total_platform_rev) * 100
    
    freq_summary_path = os.path.join(OUTPUT_TABLES, 'q7_repeat_customer_summary.csv')
    freq_summary.to_csv(freq_summary_path, index=False)
    print(f"Saved repeat customer summary table to {freq_summary_path}")
    
    # 2. MONTHLY SIGNUP COHORT RETENTION MATRIX
    customer_agg['cohort_month'] = customer_agg['first_purchase_date'].dt.to_period('M')
    
    # Join cohort month back to df_valid
    df_cohort = df_valid.merge(customer_agg[['customer_unique_id', 'cohort_month']], on='customer_unique_id', how='left')
    
    df_cohort['cohort_index'] = (df_cohort['purchase_year_month'].dt.year - df_cohort['cohort_month'].dt.year) * 12 + \
                                (df_cohort['purchase_year_month'].dt.month - df_cohort['cohort_month'].dt.month)
                                
    # Pivot cohort counts
    cohort_matrix = df_cohort.pivot_table(
        index='cohort_month',
        columns='cohort_index',
        values='customer_unique_id',
        aggfunc='nunique'
    )
    
    # Calculate Retention Rate % (relative to Month 0 size)
    cohort_size = cohort_matrix.iloc[:, 0]
    retention_matrix = cohort_matrix.divide(cohort_size, axis=0) * 100
    
    retention_csv_path = os.path.join(OUTPUT_TABLES, 'q7_customer_cohort_retention.csv')
    retention_matrix.to_csv(retention_csv_path)
    print(f"Saved cohort retention matrix table to {retention_csv_path}")

    # 3. CHART 1: CUSTOMER ORDER FREQUENCY DISTRIBUTION
    fig, ax = plt.subplots(figsize=(9, 5))
    set_chart_style(ax, title=f'Olist Customer Purchase Frequency Distribution (N = {total_unique_cust:,} Unique Customers)', xlabel='Order Frequency Category', ylabel='Number of Unique Customers')
    order_bucket_order = ['1 Order (Single)', '2 Orders', '3-5 Orders', '6+ Orders']
    freq_plot_df = freq_summary.set_index('order_bucket').reindex(order_bucket_order).reset_index()
    
    bars = ax.bar(freq_plot_df['order_bucket'], freq_plot_df['customer_count'], color=['#0EA5E9', '#6366F1', '#8B5CF6', '#EC4899'], width=0.55)
    
    for bar in bars:
        height = bar.get_height()
        pct = (height / total_unique_cust) * 100
        ax.annotate(f'{int(height):,}\n({pct:.2f}%)',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4), textcoords="offset points",
                    ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#1E293B')
                    
    save_chart(fig, 'q7_customer_repeat_distribution.png')
    
    # 4. CHART 2: COHORT RETENTION HEATMAP
    valid_cohort_indices = [c for c in retention_matrix.columns if c >= 0 and c <= 12]
    filtered_cohort_matrix = retention_matrix.loc['2017-01':'2018-06', valid_cohort_indices]
    
    fig, ax = plt.subplots(figsize=(11, 6))
    set_chart_style(ax, title='Monthly Customer Cohort Retention Rate (%) Matrix (2017–2018 Signup Cohorts)', xlabel='Months Since Initial Purchase (Cohort Index)', ylabel='First Purchase Cohort Month')
    sns.heatmap(
        filtered_cohort_matrix,
        annot=True,
        fmt='.2f',
        cmap='Blues',
        vmin=0,
        vmax=1.5,
        cbar_kws={'label': 'Retention Rate (%)'},
        ax=ax,
        linewidths=0.5
    )
    
    save_chart(fig, 'q7_cohort_retention_heatmap.png')
    
    # 5. CHART 3: SINGLE VS REPEAT CUSTOMER METRICS COMPARISON
    single_avg_aov = customer_agg[customer_agg['total_orders'] == 1]['avg_order_value'].mean()
    repeat_avg_aov = customer_agg[customer_agg['total_orders'] > 1]['avg_order_value'].mean()
    
    single_avg_score = customer_agg[customer_agg['total_orders'] == 1]['avg_review_score'].mean()
    repeat_avg_score = customer_agg[customer_agg['total_orders'] > 1]['avg_review_score'].mean()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
    set_chart_style(ax1, title='Average Order Value (AOV)', ylabel='Average Order Value (R$)')
    set_chart_style(ax2, title='Average Customer Review Score', ylabel='Review Score (Stars)')
    
    bars1 = ax1.bar([f'Single Buyers\n(N={single_cust:,})', f'Repeat Buyers\n(N={repeat_cust:,})'], [single_avg_aov, repeat_avg_aov], color=['#38BDF8', '#10B981'], width=0.45)
    for bar in bars1:
        h = bar.get_height()
        ax1.annotate(f'R$ {h:.2f}', xy=(bar.get_x() + bar.get_width() / 2, h), xytext=(0, 4), textcoords="offset points", ha='center', va='bottom', fontweight='bold', color='#1E293B')
        
    bars2 = ax2.bar(['Single Buyers', 'Repeat Buyers'], [single_avg_score, repeat_avg_score], color=['#6366F1', '#8B5CF6'], width=0.45)
    ax2.set_ylim(3.5, 4.5)
    for bar in bars2:
        h = bar.get_height()
        ax2.annotate(f'{h:.2f} Stars', xy=(bar.get_x() + bar.get_width() / 2, h), xytext=(0, 4), textcoords="offset points", ha='center', va='bottom', fontweight='bold', color='#1E293B')
        
    plt.suptitle('Unit Economics & Satisfaction: Single vs. Repeat Buyers', fontsize=13, fontweight='bold', y=1.03)
    save_chart(fig, 'q7_repeat_vs_single_metrics.png')
    
    print("Q7 Customer Cohort Analysis Complete!")
