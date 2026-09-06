"""
Core Question 4 Analysis Module
Analyzes product category GMV, order volume, average price, average freight,
review scores, low-rating rates, and late delivery rates.
Classifies categories into High-Volume/High-Satisfaction, High-Volume/Low-Satisfaction,
and High Delivery Problem segments relative to platform baselines.
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

# Overall Platform Baselines for Comparison
BASELINE_PRICE = 137.75
BASELINE_FREIGHT = 22.82
BASELINE_REVIEW = 4.07
BASELINE_LOW_RATING_RATE = 15.04
BASELINE_LATE_RATE = 8.11

def run_q4_analysis():
    """Executes Core Question 4 Category Analysis."""
    os.makedirs(OUTPUT_TABLES, exist_ok=True)
    os.makedirs(OUTPUT_CHARTS, exist_ok=True)
    
    print("Ingesting master order dataset for Q4 Category Analysis...")
    df = pd.read_csv(MASTER_PATH)
    
    df['is_low_rating'] = (df['review_score'] <= 2).astype(int)
    df_cat = df[df['category_english'].notnull()].copy()
    
    # Category level aggregations
    cat_agg = df_cat.groupby('category_english').agg(
        orders=('order_id', 'count'),
        gmv=('total_price', 'sum'),
        freight=('total_freight', 'sum'),
        avg_price=('total_price', 'mean'),
        avg_freight=('total_freight', 'mean'),
        avg_review_score=('review_score', 'mean'),
        low_rating_count=('is_low_rating', 'sum'),
        delivered_orders=('order_status', lambda x: (x == 'delivered').sum()),
        late_count=('is_late', lambda x: (x == 1).sum()),
        avg_lead_time_days=('delivery_lead_time_days', 'mean')
    ).reset_index()
    
    cat_agg['revenue'] = cat_agg['gmv'] + cat_agg['freight']
    cat_agg['freight_ratio_pct'] = (cat_agg['freight'] / cat_agg['gmv']) * 100
    cat_agg['low_rating_rate_pct'] = (cat_agg['low_rating_count'] / cat_agg['orders']) * 100
    cat_agg['late_rate_pct'] = (cat_agg['late_count'] / cat_agg['delivered_orders']) * 100
    
    # Deviations from Baseline
    cat_agg['price_diff_vs_baseline'] = cat_agg['avg_price'] - BASELINE_PRICE
    cat_agg['freight_diff_vs_baseline'] = cat_agg['avg_freight'] - BASELINE_FREIGHT
    cat_agg['review_diff_vs_baseline'] = cat_agg['avg_review_score'] - BASELINE_REVIEW
    cat_agg['low_rating_diff_vs_baseline'] = cat_agg['low_rating_rate_pct'] - BASELINE_LOW_RATING_RATE
    cat_agg['late_rate_diff_vs_baseline'] = cat_agg['late_rate_pct'] - BASELINE_LATE_RATE

    # Apply Rule 14: Filter for N >= 50 orders
    cat_filtered = cat_agg[cat_agg['orders'] >= 50].sort_values('gmv', ascending=False).copy()
    
    # Export full category analysis table
    cat_analysis_path = os.path.join(OUTPUT_TABLES, 'q4_category_analysis.csv')
    cat_filtered.to_csv(cat_analysis_path, index=False)
    print(f"Saved Q4 category analysis table (N >= 50) to {cat_analysis_path}")

    # PRIORITY CATEGORY CLASSIFICATIONS
    def classify_priority(row):
        if row['orders'] >= 1000 and row['avg_review_score'] >= 4.10 and row['low_rating_rate_pct'] <= 14.0:
            return 'High-Volume / High-Satisfaction'
        elif row['orders'] >= 1000 and (row['avg_review_score'] < 4.05 or row['low_rating_rate_pct'] > 15.5):
            return 'High-Volume / Low-Satisfaction'
        elif row['late_rate_pct'] >= 9.5 or row['avg_lead_time_days'] >= 14.0:
            return 'High Delivery Problems'
        else:
            return 'Moderate Volume / Standard'

    cat_filtered['priority_segment'] = cat_filtered.apply(classify_priority, axis=1)
    
    priority_table = cat_filtered[cat_filtered['priority_segment'] != 'Moderate Volume / Standard'].sort_values(['priority_segment', 'gmv'], ascending=[True, False])
    priority_path = os.path.join(OUTPUT_TABLES, 'q4_priority_categories.csv')
    priority_table.to_csv(priority_path, index=False)
    print(f"Saved Q4 priority categories summary to {priority_path}")

    # Visualizations
    # Chart 1: q4_category_revenue_vs_review.png
    fig, ax = plt.subplots(figsize=(11, 6))
    top20 = cat_filtered.head(20)
    
    scatter = ax.scatter(top20['gmv'] / 1000, top20['avg_review_score'], 
                         s=top20['orders'] / 12, color=PALETTE['primary'], alpha=0.7, edgecolors=PALETTE['dark_navy'])
    
    # Benchmark line
    ax.axhline(BASELINE_REVIEW, color=PALETTE['danger'], linestyle='--', linewidth=1.5, label=f'Platform Baseline Review ({BASELINE_REVIEW:.2f})')
    
    for _, r in top20.iterrows():
        ax.annotate(r['category_english'], (r['gmv'] / 1000, r['avg_review_score']),
                    fontsize=8, fontweight='semibold', color='#334155', xytext=(5, 3), textcoords='offset points')
        
    set_chart_style(ax, title='Top 20 Categories: Gross Merchandise Value (GMV) vs. Average Review Score',
                    xlabel='Total GMV (Thousands R$)', ylabel='Average Review Score (1-5 Stars)')
    ax.set_ylim(3.7, 4.4)
    ax.legend(loc='lower right', frameon=True, facecolor='white', edgecolor='#CBD5E1')
    save_chart(fig, 'q4_category_revenue_vs_review.png', OUTPUT_CHARTS)

    # Chart 2: q4_category_freight_impact.png
    fig, ax = plt.subplots(figsize=(11, 6))
    
    scatter = ax.scatter(top20['freight_ratio_pct'], top20['low_rating_rate_pct'], 
                         s=top20['orders'] / 12, color=PALETTE['secondary'], alpha=0.7, edgecolors=PALETTE['dark_navy'])
    
    ax.axhline(BASELINE_LOW_RATING_RATE, color=PALETTE['danger'], linestyle='--', label=f'Platform Baseline Low-Rating Rate ({BASELINE_LOW_RATING_RATE:.1f}%)')
    
    for _, r in top20.iterrows():
        ax.annotate(r['category_english'], (r['freight_ratio_pct'], r['low_rating_rate_pct']),
                    fontsize=8, fontweight='semibold', color='#334155', xytext=(5, 3), textcoords='offset points')
        
    set_chart_style(ax, title='Top 20 Categories: Freight Ratio (%) vs. Low-Rating Rate (1 & 2 Stars %)',
                    xlabel='Freight-to-Price Ratio (%)', ylabel='Low-Rating Rate (%)')
    ax.legend(loc='upper right', frameon=True, facecolor='white', edgecolor='#CBD5E1')
    save_chart(fig, 'q4_category_freight_impact.png', OUTPUT_CHARTS)

    # Chart 3: q4_priority_category_matrix.png
    fig, ax = plt.subplots(figsize=(12, 5.5))
    high_sat = priority_table[priority_table['priority_segment'] == 'High-Volume / High-Satisfaction'].head(5)
    low_sat = priority_table[priority_table['priority_segment'] == 'High-Volume / Low-Satisfaction'].head(5)
    
    comp_df = pd.concat([high_sat, low_sat])
    x_c = np.arange(len(comp_df))
    width = 0.35
    
    colors = [PALETTE['success'] if seg == 'High-Volume / High-Satisfaction' else PALETTE['danger'] for seg in comp_df['priority_segment']]
    
    b1 = ax.bar(x_c, comp_df['avg_review_score'], width, color=colors)
    
    set_chart_style(ax, title='Priority Categories: High-Satisfaction Winners vs. Low-Satisfaction Friction Categories',
                    xlabel='Product Category', ylabel='Average Review Score (1-5 Stars)')
    ax.set_xticks(x_c)
    ax.set_xticklabels(comp_df['category_english'], rotation=35, ha='right')
    ax.set_ylim(3.5, 4.4)
    ax.axhline(BASELINE_REVIEW, color=PALETTE['gray'], linestyle='--', label=f'Baseline ({BASELINE_REVIEW:.2f})')
    
    annotate_bars(ax, format_str='{:.2f}', fontsize=9, padding=0.03)
    ax.legend(loc='lower left', frameon=True, facecolor='white', edgecolor='#CBD5E1')
    save_chart(fig, 'q4_priority_category_matrix.png', OUTPUT_CHARTS)

    return cat_filtered, priority_table

if __name__ == '__main__':
    run_q4_analysis()
