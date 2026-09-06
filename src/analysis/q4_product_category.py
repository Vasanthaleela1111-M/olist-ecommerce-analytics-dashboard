"""
Question 4: Product Category Performance
Analyzes product category GMV, order volume, Average Order Value (AOV), average review scores,
freight-to-price ratios, and high-growth vs declining categories.
Enforces Data Integrity Rule 14 (minimum sample size N >= 50 orders).
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

def analyze_product_category_performance(df):
    """Executes Question 4 analysis."""
    print("--- Running Q4: Product Category Performance ---")
    
    # Filter valid category rows
    df_cat = df[df['category_english'].notnull()].copy()
    
    # Aggregate category metrics
    cat_summary = df_cat.groupby('category_english').agg(
        order_count=('order_id', 'count'),
        total_gmv=('total_price', 'sum'),
        total_freight=('total_freight', 'sum'),
        avg_item_price=('total_price', 'mean'),
        avg_item_freight=('total_freight', 'mean'),
        avg_review_score=('review_score', 'mean'),
        delivered_count=('order_status', lambda x: (x == 'delivered').sum()),
        avg_lead_time_days=('delivery_lead_time_days', 'mean')
    ).reset_index()
    
    cat_summary['total_revenue'] = cat_summary['total_gmv'] + cat_summary['total_freight']
    cat_summary['aov'] = cat_summary['total_gmv'] / cat_summary['order_count']
    cat_summary['freight_ratio_pct'] = (cat_summary['total_freight'] / cat_summary['total_gmv']) * 100
    cat_summary['gmv_share_pct'] = (cat_summary['total_gmv'] / df_cat['total_price'].sum()) * 100
    
    # Apply Data Integrity Rule 14: Filter for minimum sample size N >= 50 orders
    cat_filtered = cat_summary[cat_summary['order_count'] >= 50].copy()
    
    cat_sorted_gmv = cat_filtered.sort_values('total_gmv', ascending=False)
    
    # Save category summary table
    cat_path = os.path.join(OUTPUT_TABLES, 'q4_product_category_performance.csv')
    cat_sorted_gmv.to_csv(cat_path, index=False)
    print(f"Saved product category performance table to {cat_path}")
    
    # Top 10 by GMV
    top10_gmv = cat_sorted_gmv.head(10)
    # Bottom 10 by GMV (with N >= 50)
    bottom10_gmv = cat_sorted_gmv.tail(10)
    
    print("\n--- TOP 5 CATEGORIES BY GMV ---")
    for idx, r in top10_gmv.head(5).iterrows():
        print(f"{r['category_english']}: GMV R$ {r['total_gmv']:,.2f} ({r['gmv_share_pct']:.2f}%), Orders: {r['order_count']:,}, Review: {r['avg_review_score']:.2f}")
        
    print("\n--- BOTTOM 5 CATEGORIES BY GMV (N >= 50) ---")
    for idx, r in bottom10_gmv.tail(5).iterrows():
        print(f"{r['category_english']}: GMV R$ {r['total_gmv']:,.2f}, Orders: {r['order_count']:,}, Review: {r['avg_review_score']:.2f}")

    # Category Growth Analysis (2017 H2 vs 2018 H1)
    df_cat_growth = df_cat[
        (df_cat['purchase_year_month'] >= '2017-07') & (df_cat['purchase_year_month'] <= '2018-06')
    ].copy()
    
    df_cat_growth['period'] = np.where(
        df_cat_growth['purchase_year_month'] <= '2017-12', '2017_H2', '2018_H1'
    )
    
    growth_piv = df_cat_growth.groupby(['category_english', 'period'])['total_price'].sum().unstack().fillna(0)
    growth_piv['total_period_gmv'] = growth_piv['2017_H2'] + growth_piv['2018_H1']
    growth_piv = growth_piv[growth_piv['total_period_gmv'] >= 10000].copy() # N threshold for growth
    
    growth_piv['gmv_growth_pct'] = ((growth_piv['2018_H1'] - growth_piv['2017_H2']) / growth_piv['2017_H2']) * 100
    growth_piv = growth_piv.reset_index().sort_values('gmv_growth_pct', ascending=False)
    
    growth_path = os.path.join(OUTPUT_TABLES, 'q4_category_growth_2017h2_vs_2018h1.csv')
    growth_piv.to_csv(growth_path, index=False)

    # Visualizations
    # Chart 1: Top 10 Categories by GMV
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.barh(top10_gmv['category_english'][::-1], top10_gmv['total_gmv'][::-1] / 1000, 
                   color=PALETTE['primary'], height=0.65)
    
    set_chart_style(ax, title='Top 10 Product Categories by Gross Merchandise Value (GMV)',
                    xlabel='Total GMV (Thousands R$)', ylabel='Product Category')
    
    annotate_bars(ax, format_str='R$ {:.0f}k', is_horizontal=True, fontsize=9, padding=10)
    save_chart(fig, 'q4_top_categories_by_gmv.png', OUTPUT_CHARTS)

    # Chart 2: Freight Ratio vs Review Score (Scatter with Category Labels)
    fig, ax = plt.subplots(figsize=(10, 6))
    
    top20_cats = cat_sorted_gmv.head(20)
    
    scatter = ax.scatter(top20_cats['freight_ratio_pct'], top20_cats['avg_review_score'], 
                         s=top20_cats['order_count'] / 15, color=PALETTE['secondary'], alpha=0.7, edgecolors=PALETTE['dark_navy'])
    
    for _, r in top20_cats.iterrows():
        ax.annotate(r['category_english'], (r['freight_ratio_pct'], r['avg_review_score']),
                    fontsize=8, fontweight='semibold', color='#334155', xytext=(4, 2), textcoords='offset points')
        
    set_chart_style(ax, title='Top 20 Categories: Freight Ratio (%) vs. Average Review Score',
                    xlabel='Freight-to-Price Ratio (%)', ylabel='Average Review Score (1-5 Stars)')
    ax.set_ylim(3.6, 4.5)
    save_chart(fig, 'q4_category_freight_ratio_vs_reviews.png', OUTPUT_CHARTS)
    
    return cat_sorted_gmv, growth_piv

if __name__ == '__main__':
    master_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'outputs', 'master_analytical_dataset.csv')
    df = pd.read_csv(master_path)
    analyze_product_category_performance(df)
