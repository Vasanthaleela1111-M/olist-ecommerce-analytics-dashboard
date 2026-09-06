"""
Core Question 1 Analysis Module
Analyzes monthly trends in order volume, revenue, Average Order Value (AOV),
average review score, and low-rating rate (1 & 2 stars %).
Investigates whether marketplace volume growth moved together with customer satisfaction.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.visualization import set_chart_style, annotate_bars, save_chart, PALETTE

OUTPUT_TABLES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'outputs', 'tables')
OUTPUT_CHARTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'outputs', 'charts')
MASTER_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'outputs', 'exports', 'master_orders.csv')

def run_q1_analysis():
    """Executes Core Question 1 Monthly Performance Analysis."""
    os.makedirs(OUTPUT_TABLES, exist_ok=True)
    os.makedirs(OUTPUT_CHARTS, exist_ok=True)
    
    print("Ingesting master order dataset for Q1 Analysis...")
    df = pd.read_csv(MASTER_PATH)
    
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    df['purchase_year_month'] = df['order_purchase_timestamp'].dt.strftime('%Y-%m')
    
    # Monthly aggregation
    monthly = df.groupby('purchase_year_month').agg(
        orders=('order_id', 'count'),
        revenue=('total_order_value', 'sum'),
        gmv=('total_price', 'sum'),
        freight=('total_freight', 'sum'),
        avg_review_score=('review_score', 'mean'),
        low_rating_count=('review_score', lambda x: (x <= 2).sum()),
        deliv_late_count=('is_late', lambda x: (x == 1).sum()),
        delivered_orders=('order_status', lambda x: (x == 'delivered').sum())
    ).reset_index()
    
    monthly['aov'] = monthly['revenue'] / monthly['orders']
    monthly['item_aov'] = monthly['gmv'] / monthly['orders']
    monthly['low_rating_rate_pct'] = (monthly['low_rating_count'] / monthly['orders']) * 100
    monthly['late_rate_pct'] = (monthly['deliv_late_count'] / monthly['delivered_orders']) * 100
    
    monthly['revenue_mom_growth_pct'] = monthly['revenue'].pct_change() * 100
    monthly['orders_mom_growth_pct'] = monthly['orders'].pct_change() * 100

    # Save monthly performance table
    monthly_path = os.path.join(OUTPUT_TABLES, 'q1_monthly_performance.csv')
    monthly.to_csv(monthly_path, index=False)
    print(f"Saved Q1 monthly performance table to {monthly_path}")

    # Core operational window (2017-01 to 2018-08) for correlation analysis
    core_months = monthly[(monthly['purchase_year_month'] >= '2017-01') & (monthly['purchase_year_month'] <= '2018-08')].copy()
    
    corr_volume_review = core_months['orders'].corr(core_months['avg_review_score'])
    corr_volume_low_rating = core_months['orders'].corr(core_months['low_rating_rate_pct'])
    corr_revenue_review = core_months['revenue'].corr(core_months['avg_review_score'])
    corr_late_low_rating = core_months['late_rate_pct'].corr(core_months['low_rating_rate_pct'])
    
    print("\n--- CO-MOVEMENT CORRELATION ANALYSIS (2017-01 to 2018-08) ---")
    print(f"Correlation (Order Volume vs Avg Review Score): r = {corr_volume_review:.4f}")
    print(f"Correlation (Order Volume vs Low Rating Rate %): r = {corr_volume_low_rating:.4f}")
    print(f"Correlation (Revenue vs Avg Review Score): r = {corr_revenue_review:.4f}")
    print(f"Correlation (Monthly Late Rate % vs Low Rating Rate %): r = {corr_late_low_rating:.4f}")

    # Render Chart 1: q1_orders.png
    fig, ax = plt.subplots(figsize=(12, 5.5))
    plot_df = monthly[(monthly['purchase_year_month'] >= '2017-01') & (monthly['purchase_year_month'] <= '2018-08')]
    
    ax.plot(plot_df['purchase_year_month'], plot_df['orders'], 
            color=PALETTE['primary'], marker='o', linewidth=2.5, label='Monthly Orders')
    
    set_chart_style(ax, title='Olist Monthly Order Volume Growth Trajectory (2017 - 2018)',
                    xlabel='Year-Month', ylabel='Total Orders')
    ax.set_xticks(range(len(plot_df)))
    ax.set_xticklabels(plot_df['purchase_year_month'], rotation=45)
    
    # Annotate Black Friday 2017
    bf_idx = plot_df[plot_df['purchase_year_month'] == '2017-11'].index
    if not bf_idx.empty:
        pos = plot_df.index.get_loc(bf_idx[0])
        val = plot_df.loc[bf_idx[0], 'orders']
        ax.annotate(f'Black Friday Peak\n(Nov 2017: {val:,} orders)', 
                    xy=(pos, val), xytext=(pos - 2.5, val + 600),
                    arrowprops=dict(facecolor=PALETTE['accent'], shrink=0.08, width=1.5, headwidth=7),
                    fontsize=9.5, fontweight='bold', color=PALETTE['dark_navy'])
        
    save_chart(fig, 'q1_orders.png', OUTPUT_CHARTS)

    # Render Chart 2: q1_revenue.png
    fig, ax1 = plt.subplots(figsize=(12, 5.5))
    ax2 = ax1.twinx()
    
    x_pos = np.arange(len(plot_df))
    
    l1 = ax1.plot(x_pos, plot_df['revenue'] / 1000, 
                  color=PALETTE['secondary'], marker='s', linewidth=2.5, label='Gross Revenue (GMV + Freight, k R$)')
    l2 = ax2.plot(x_pos, plot_df['aov'], 
                  color=PALETTE['accent'], marker='D', linewidth=2.0, linestyle='--', label='Average Order Value (AOV, R$)')
    
    set_chart_style(ax1, title='Olist Monthly Gross Revenue (Thousands R$) & Average Order Value (AOV)',
                    xlabel='Year-Month', ylabel='Total Gross Revenue (Thousands R$)')
    ax2.set_ylabel('Average Order Value (R$)', fontsize=11, fontweight='semibold', color=PALETTE['accent'])
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(plot_df['purchase_year_month'], rotation=45)
    ax2.set_ylim(120, 200)
    
    lines = l1 + l2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left', frameon=True, facecolor='white', edgecolor='#CBD5E1')
    
    save_chart(fig, 'q1_revenue.png', OUTPUT_CHARTS)

    # Render Chart 3: q1_review_score.png
    fig, ax1 = plt.subplots(figsize=(12, 5.5))
    ax2 = ax1.twinx()
    
    l1 = ax1.plot(x_pos, plot_df['avg_review_score'], 
                  color=PALETTE['primary'], marker='^', linewidth=2.5, label='Average Review Score (1-5 Stars)')
    l2 = ax2.plot(x_pos, plot_df['low_rating_rate_pct'], 
                  color=PALETTE['danger'], marker='v', linewidth=2.5, linestyle=':', label='Low-Rating Rate (1 & 2 Stars %)')
    
    set_chart_style(ax1, title='Monthly Customer Satisfaction: Average Review Score vs. Low-Rating Rate (%)',
                    xlabel='Year-Month', ylabel='Average Review Score (1 - 5 Stars)')
    ax2.set_ylabel('Low-Rating Rate (%)', fontsize=11, fontweight='semibold', color=PALETTE['danger'])
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(plot_df['purchase_year_month'], rotation=45)
    ax1.set_ylim(3.5, 4.5)
    ax2.set_ylim(5, 30)
    
    # Highlight March 2018 satisfaction dip
    mar_idx = plot_df[plot_df['purchase_year_month'] == '2018-03'].index
    if not mar_idx.empty:
        pos = plot_df.index.get_loc(mar_idx[0])
        val = plot_df.loc[mar_idx[0], 'avg_review_score']
        ax1.annotate(f'Satisfaction Dip\n(March 2018: {val:.2f} stars)', 
                     xy=(pos, val), xytext=(pos - 2, val - 0.35),
                     arrowprops=dict(facecolor=PALETTE['danger'], shrink=0.08, width=1.5, headwidth=7),
                     fontsize=9, fontweight='bold', color=PALETTE['danger'])
        
    lines = l1 + l2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='lower right', frameon=True, facecolor='white', edgecolor='#CBD5E1')
    
    save_chart(fig, 'q1_review_score.png', OUTPUT_CHARTS)

    return monthly, core_months

if __name__ == '__main__':
    run_q1_analysis()
