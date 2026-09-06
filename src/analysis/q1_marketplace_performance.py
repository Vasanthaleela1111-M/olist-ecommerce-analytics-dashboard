"""
Question 1: Marketplace Performance Over Time
Analyzes GMV, order volume, Average Order Value (AOV), growth trajectory across months/quarters,
seasonality, and active seller participation over time.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.visualization import set_chart_style, annotate_bars, save_chart, PALETTE, CHART_COLORS

OUTPUT_TABLES = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'outputs', 'tables')
OUTPUT_CHARTS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'outputs', 'charts')

def analyze_marketplace_performance(df):
    """Executes Question 1 analysis."""
    print("--- Running Q1: Marketplace Performance Over Time ---")
    
    # Filter out 2016-09 and 2018-10 if partial edge months exist with minimal data
    df_valid = df[df['order_purchase_timestamp'].notnull()].copy()
    
    # Overall summary metrics
    total_gmv = df_valid['total_price'].sum()
    total_freight = df_valid['total_freight'].sum()
    total_revenue = df_valid['total_order_value'].sum()
    total_orders = len(df_valid)
    overall_aov_items = total_gmv / df_valid['total_price'].count()
    overall_aov_total = total_revenue / df_valid['total_order_value'].count()
    
    print(f"Total GMV (Item Value): R$ {total_gmv:,.2f}")
    print(f"Total Freight Value: R$ {total_freight:,.2f}")
    print(f"Total Revenue (GMV + Freight): R$ {total_revenue:,.2f}")
    print(f"Total Orders: {total_orders:,}")
    print(f"Overall Item AOV: R$ {overall_aov_items:.2f}")
    print(f"Overall Total Order AOV: R$ {overall_aov_total:.2f}")
    
    # Monthly aggregation
    monthly = df_valid.groupby('purchase_year_month').agg(
        order_count=('order_id', 'count'),
        total_gmv=('total_price', 'sum'),
        total_freight=('total_freight', 'sum'),
        total_revenue=('total_order_value', 'sum'),
        active_sellers=('primary_seller_id', 'nunique'),
        active_customers=('customer_unique_id', 'nunique'),
        delivered_orders=('order_status', lambda x: (x == 'delivered').sum())
    ).reset_index()
    
    # Exclude partial edge months for clean time series analysis if needed (2016-09 has 4 orders, 2018-10 has 4)
    monthly = monthly[(monthly['purchase_year_month'] >= '2017-01') & (monthly['purchase_year_month'] <= '2018-08')].copy()
    
    monthly['item_aov'] = monthly['total_gmv'] / monthly['order_count']
    monthly['total_aov'] = monthly['total_revenue'] / monthly['order_count']
    monthly['gmv_mom_growth_pct'] = monthly['total_gmv'].pct_change() * 100
    monthly['order_mom_growth_pct'] = monthly['order_count'].pct_change() * 100
    
    # Save monthly table
    monthly_path = os.path.join(OUTPUT_TABLES, 'q1_monthly_marketplace_performance.csv')
    monthly.to_csv(monthly_path, index=False)
    print(f"Saved monthly performance table to {monthly_path}")

    # Quarterly aggregation
    quarterly = df_valid.groupby('purchase_year_quarter').agg(
        order_count=('order_id', 'count'),
        total_gmv=('total_price', 'sum'),
        total_freight=('total_freight', 'sum'),
        total_revenue=('total_order_value', 'sum'),
        active_sellers=('primary_seller_id', 'nunique')
    ).reset_index()
    quarterly = quarterly[(quarterly['purchase_year_quarter'] >= '2017Q1') & (quarterly['purchase_year_quarter'] <= '2018Q3')].copy()
    quarterly['item_aov'] = quarterly['total_gmv'] / quarterly['order_count']
    quarterly['total_aov'] = quarterly['total_revenue'] / quarterly['order_count']
    quarterly['gmv_qoq_growth_pct'] = quarterly['total_gmv'].pct_change() * 100
    
    quarterly_path = os.path.join(OUTPUT_TABLES, 'q1_quarterly_marketplace_performance.csv')
    quarterly.to_csv(quarterly_path, index=False)
    print(f"Saved quarterly performance table to {quarterly_path}")

    # Visualizations
    # Chart 1: Monthly GMV and Order Volume Trajectory
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    ax2 = ax1.twinx()
    
    line1 = ax1.plot(monthly['purchase_year_month'], monthly['total_gmv'] / 1000, 
                     color=PALETTE['primary'], marker='o', linewidth=2.5, label='Monthly GMV (k R$)')
    line2 = ax2.plot(monthly['purchase_year_month'], monthly['order_count'], 
                     color=PALETTE['secondary'], marker='s', linewidth=2.5, linestyle='--', label='Order Volume')
    
    # Highlight Black Friday (Nov 2017)
    bf_idx = monthly[monthly['purchase_year_month'] == '2017-11'].index
    if not bf_idx.empty:
        bf_pos = monthly.index.get_loc(bf_idx[0])
        ax1.annotate('Black Friday Spike\n(Nov 2017: ~R$ 1.0M GMV)', 
                     xy=(bf_pos, monthly.loc[bf_idx[0], 'total_gmv']/1000),
                     xytext=(bf_pos - 2, monthly.loc[bf_idx[0], 'total_gmv']/1000 + 150),
                     arrowprops=dict(facecolor=PALETTE['accent'], shrink=0.08, width=1.5, headwidth=8),
                     fontsize=10, fontweight='bold', color=PALETTE['dark_navy'])
    
    set_chart_style(ax1, title='Olist Marketplace Growth: Monthly GMV & Order Volume (2017 - 2018)',
                    xlabel='Year-Month', ylabel='Total GMV (Thousands R$)')
    ax2.set_ylabel('Order Count', fontsize=11, fontweight='semibold', color=PALETTE['secondary'])
    ax1.set_xticklabels(monthly['purchase_year_month'], rotation=45)
    
    # Combined legend
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left', frameon=True, facecolor='white', edgecolor='#CBD5E1')
    
    save_chart(fig, 'q1_gmv_and_order_trends.png', OUTPUT_CHARTS)

    # Chart 2: Active Sellers & Average Order Value (AOV) over time
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()
    
    l1 = ax1.plot(monthly['purchase_year_month'], monthly['active_sellers'], 
                  color=PALETTE['purple'], marker='^', linewidth=2.5, label='Active Sellers')
    l2 = ax2.plot(monthly['purchase_year_month'], monthly['item_aov'], 
                  color=PALETTE['accent'], marker='D', linewidth=2.5, linestyle=':', label='Item AOV (R$)')
    
    set_chart_style(ax1, title='Olist Seller Participation & Average Order Value (AOV) Stability',
                    xlabel='Year-Month', ylabel='Active Sellers Count')
    ax2.set_ylabel('Item AOV (R$)', fontsize=11, fontweight='semibold', color=PALETTE['accent'])
    ax1.set_xticklabels(monthly['purchase_year_month'], rotation=45)
    
    lines = l1 + l2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='center left', frameon=True, facecolor='white', edgecolor='#CBD5E1')
    
    save_chart(fig, 'q1_active_sellers_and_aov.png', OUTPUT_CHARTS)
    
    return monthly, quarterly

if __name__ == '__main__':
    master_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'outputs', 'master_analytical_dataset.csv')
    df = pd.read_csv(master_path)
    analyze_marketplace_performance(df)
