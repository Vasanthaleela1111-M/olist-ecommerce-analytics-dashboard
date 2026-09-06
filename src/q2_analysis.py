"""
Core Question 2 Analysis Module
Analyzes delivery timing relative to estimated delivery date and its relationship with customer review scores.
Calculates absolute differences, relative risk multipliers, sample sizes (N),
and category/state interaction effects.
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

def run_q2_analysis():
    """Executes Core Question 2 Analysis."""
    os.makedirs(OUTPUT_TABLES, exist_ok=True)
    os.makedirs(OUTPUT_CHARTS, exist_ok=True)
    
    print("Ingesting master order dataset for Q2 Analysis...")
    df = pd.read_csv(MASTER_PATH)
    
    # Rule 11: Delivered orders with valid delivery timestamps
    delivered = df[
        (df['order_status'] == 'delivered') & 
        (df['order_delivered_customer_date'].notnull()) & 
        (df['order_estimated_delivery_date'].notnull())
    ].copy()
    
    delivered['is_low_rating'] = (delivered['review_score'] <= 2).astype(int)
    delivered['is_1star'] = (delivered['review_score'] == 1).astype(int)
    
    total_delivered = len(delivered)
    print(f"Total Delivered Orders Analyzed (N): {total_delivered:,}")

    # 1. DELIVERY STATUS VS REVIEW SCORE (On-Time vs Late)
    status_summary = delivered.groupby('is_late').agg(
        order_count=('order_id', 'count'),
        avg_review_score=('review_score', 'mean'),
        pct_1star=('is_1star', lambda x: x.mean() * 100),
        low_rating_rate_pct=('is_low_rating', lambda x: x.mean() * 100),
        avg_actual_lead_time=('delivery_lead_time_days', 'mean'),
        avg_estimated_lead_time=('estimated_lead_time_days', 'mean')
    ).reset_index()
    
    status_summary['delivery_status'] = np.where(status_summary['is_late'] == 1, 'Late (Delivered > Estimated Date)', 'On-Time / Early (Delivered <= Estimated Date)')
    status_summary['order_share_pct'] = (status_summary['order_count'] / total_delivered) * 100
    
    ontime_row = status_summary[status_summary['is_late'] == 0].iloc[0]
    late_row = status_summary[status_summary['is_late'] == 1].iloc[0]
    
    abs_diff_review = late_row['avg_review_score'] - ontime_row['avg_review_score']
    rel_diff_review = ((late_row['avg_review_score'] - ontime_row['avg_review_score']) / ontime_row['avg_review_score']) * 100
    
    abs_diff_1star = late_row['pct_1star'] - ontime_row['pct_1star']
    rel_ratio_1star = late_row['pct_1star'] / ontime_row['pct_1star']
    
    abs_diff_low_rating = late_row['low_rating_rate_pct'] - ontime_row['low_rating_rate_pct']
    rel_ratio_low_rating = late_row['low_rating_rate_pct'] / ontime_row['low_rating_rate_pct']
    
    print("\n--- DELIVERY STATUS VS REVIEW SCORE METRICS ---")
    print(f"On-Time Orders (N={ontime_row['order_count']:,}): Avg Review = {ontime_row['avg_review_score']:.2f}, 1-Star % = {ontime_row['pct_1star']:.2f}%, Low-Rating % = {ontime_row['low_rating_rate_pct']:.2f}%")
    print(f"Late Orders (N={late_row['order_count']:,}): Avg Review = {late_row['avg_review_score']:.2f}, 1-Star % = {late_row['pct_1star']:.2f}%, Low-Rating % = {late_row['low_rating_rate_pct']:.2f}%")
    print(f"Absolute Diff (Review Score): {abs_diff_review:.2f} stars ({rel_diff_review:.1f}%)")
    print(f"1-Star Rate Impact: Absolute Diff = +{abs_diff_1star:.2f} percentage points, Relative Risk = {rel_ratio_1star:.2f}x")
    print(f"Low-Rating Rate Impact: Absolute Diff = +{abs_diff_low_rating:.2f} percentage points, Relative Risk = {rel_ratio_low_rating:.2f}x")

    # 2. DELAY BUCKETS VS LOW-RATING RATE
    def get_delay_bucket(row):
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

    delivered['delay_bucket'] = delivered.apply(get_delay_bucket, axis=1)
    
    bucket_summary = delivered.groupby('delay_bucket').agg(
        order_count=('order_id', 'count'),
        avg_review_score=('review_score', 'mean'),
        pct_1star=('is_1star', lambda x: x.mean() * 100),
        low_rating_rate_pct=('is_low_rating', lambda x: x.mean() * 100),
        avg_actual_lead_time=('delivery_lead_time_days', 'mean')
    ).reset_index()
    bucket_summary['order_share_pct'] = (bucket_summary['order_count'] / total_delivered) * 100
    
    # Save primary export table
    export_path = os.path.join(OUTPUT_TABLES, 'q2_delivery_analysis.csv')
    bucket_summary.to_csv(export_path, index=False)
    print(f"Saved Q2 delivery analysis table to {export_path}")

    # 3. CATEGORY X DELIVERY INTERACTION (Top Categories, N >= 50 per cell)
    cat_deliv = delivered.groupby(['category_english', 'is_late']).agg(
        order_count=('order_id', 'count'),
        avg_review_score=('review_score', 'mean'),
        low_rating_rate_pct=('is_low_rating', lambda x: x.mean() * 100)
    ).reset_index()
    
    cat_piv = cat_deliv.pivot(index='category_english', columns='is_late', values=['order_count', 'low_rating_rate_pct', 'avg_review_score'])
    cat_piv.columns = ['cnt_ontime', 'cnt_late', 'low_rate_ontime', 'low_rate_late', 'score_ontime', 'score_late']
    cat_piv['total_orders'] = cat_piv['cnt_ontime'].fillna(0) + cat_piv['cnt_late'].fillna(0)
    
    # Filter for N >= 50 orders in both ontime and late groups
    cat_piv_filtered = cat_piv[(cat_piv['cnt_ontime'] >= 50) & (cat_piv['cnt_late'] >= 50)].copy()
    cat_piv_filtered['low_rate_abs_diff'] = cat_piv_filtered['low_rate_late'] - cat_piv_filtered['low_rate_ontime']
    cat_piv_filtered['low_rate_rel_risk'] = cat_piv_filtered['low_rate_late'] / cat_piv_filtered['low_rate_ontime']
    cat_piv_filtered = cat_piv_filtered.sort_values('total_orders', ascending=False)
    
    cat_piv_filtered.to_csv(os.path.join(OUTPUT_TABLES, 'q2_category_delivery_interaction.csv'))

    # 4. CUSTOMER STATE X DELIVERY INTERACTION
    state_overall = master_df.groupby('customer_state').agg(
        total_orders=('order_id', 'count'),
        avg_review_score=('review_score', 'mean'),
        low_rating_rate_pct=('is_low_rating', lambda x: x.mean() * 100)
    )

    state_deliv_lead = delivered.groupby('customer_state').agg(
        delivered_orders=('order_id', 'count'),
        avg_lead_time_days=('delivery_lead_time_days', 'mean'),
        late_rate_pct=('is_late', lambda x: x.mean() * 100)
    )

    state_deliv = delivered.groupby(['customer_state', 'is_late']).agg(
        order_count=('order_id', 'count'),
        avg_review_score=('review_score', 'mean'),
        low_rating_rate_pct=('is_low_rating', lambda x: x.mean() * 100)
    ).reset_index()
    
    state_piv = state_deliv.pivot(index='customer_state', columns='is_late', values=['order_count', 'low_rating_rate_pct', 'avg_review_score'])
    state_piv.columns = ['cnt_ontime', 'cnt_late', 'low_rate_ontime', 'low_rate_late', 'score_ontime', 'score_late']
    state_piv['low_rate_abs_diff'] = state_piv['low_rate_late'] - state_piv['low_rate_ontime']
    state_piv['low_rate_rel_risk'] = state_piv['low_rate_late'] / state_piv['low_rate_ontime']

    state_combined = state_overall.join(state_deliv_lead).join(state_piv).reset_index()
    state_combined = state_combined.sort_values('total_orders', ascending=False)
    state_combined.to_csv(os.path.join(OUTPUT_TABLES, 'q2_state_delivery_interaction.csv'), index=False)

    # Visualizations
    # Chart 1: q2_delivery_status_vs_reviews.png
    fig, ax1 = plt.subplots(figsize=(9, 5))
    ax2 = ax1.twinx()
    
    x = np.arange(len(status_summary))
    width = 0.35
    
    b1 = ax1.bar(x - width/2, status_summary['avg_review_score'], width, color=PALETTE['primary'], label='Average Review Score (1-5 Stars)')
    b2 = ax2.bar(x + width/2, status_summary['low_rating_rate_pct'], width, color=PALETTE['danger'], label='Low-Rating Rate (1 & 2 Stars %)')
    
    set_chart_style(ax1, title='Delivery Status vs. Customer Satisfaction Metrics (N = 96,470 Delivered Orders)',
                    xlabel='Delivery Status Relative to Estimated Date', ylabel='Average Review Score (1-5 Stars)')
    ax2.set_ylabel('Low-Rating Rate (%)', fontsize=11, fontweight='semibold', color=PALETTE['danger'])
    ax1.set_xticks(x)
    ax1.set_xticklabels(['On-Time / Early\n(N = 88,644)', 'Late Delivery\n(N = 7,826)'])
    ax1.set_ylim(0, 5.5)
    ax2.set_ylim(0, 70)
    
    annotate_bars(ax1, format_str='{:.2f}', fontsize=10, padding=0.1)
    annotate_bars(ax2, format_str='{:.1f}%', fontsize=10, padding=1.0)
    
    lines = [b1, b2]
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper right', frameon=True, facecolor='white', edgecolor='#CBD5E1')
    save_chart(fig, 'q2_delivery_status_vs_reviews.png', OUTPUT_CHARTS)

    # Chart 2: q2_delay_bucket_low_rating_trend.png
    fig, ax1 = plt.subplots(figsize=(11, 5.5))
    ax2 = ax1.twinx()
    
    x_b = np.arange(len(bucket_summary))
    
    b1 = ax1.bar(x_b - width/2, bucket_summary['avg_review_score'], width, color=PALETTE['secondary'], label='Avg Review Score (1-5 Stars)')
    b2 = ax2.bar(x_b + width/2, bucket_summary['low_rating_rate_pct'], width, color=PALETTE['danger'], label='Low-Rating Rate (1 & 2 Stars %)')
    
    set_chart_style(ax1, title='Customer Review Score & Low-Rating Rate by Delivery Timing Bucket',
                    xlabel='Delivery Timing Bucket', ylabel='Average Review Score (1-5 Stars)')
    ax2.set_ylabel('Low-Rating Rate (%)', fontsize=11, fontweight='semibold', color=PALETTE['danger'])
    ax1.set_xticks(x_b)
    ax1.set_xticklabels(bucket_summary['delay_bucket'], rotation=25, ha='right')
    ax1.set_ylim(0, 5.5)
    ax2.set_ylim(0, 85)
    
    annotate_bars(ax1, format_str='{:.2f}', fontsize=8.5, padding=0.1)
    annotate_bars(ax2, format_str='{:.1f}%', fontsize=8.5, padding=1.0)
    
    lines = [b1, b2]
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left', frameon=True, facecolor='white', edgecolor='#CBD5E1')
    save_chart(fig, 'q2_delay_bucket_low_rating_trend.png', OUTPUT_CHARTS)

    # Chart 3: q2_category_delivery_interaction.png
    fig, ax = plt.subplots(figsize=(12, 6))
    top10_cat_inter = cat_piv_filtered.head(10)
    
    x_c = np.arange(len(top10_cat_inter))
    
    b1 = ax.bar(x_c - width/2, top10_cat_inter['low_rate_ontime'], width, color=PALETTE['primary'], label='On-Time Low-Rating Rate (%)')
    b2 = ax.bar(x_c + width/2, top10_cat_inter['low_rate_late'], width, color=PALETTE['danger'], label='Late Low-Rating Rate (%)')
    
    set_chart_style(ax, title='Top 10 Categories: Low-Rating Rate (%) for On-Time vs. Late Deliveries',
                    xlabel='Product Category', ylabel='Low-Rating Rate (1 & 2 Stars %)')
    ax.set_xticks(x_c)
    ax.set_xticklabels(top10_cat_inter.index, rotation=35, ha='right')
    
    annotate_bars(ax, format_str='{:.1f}%', fontsize=8, padding=0.5)
    ax.legend(loc='upper left', frameon=True, facecolor='white', edgecolor='#CBD5E1')
    save_chart(fig, 'q2_category_delivery_interaction.png', OUTPUT_CHARTS)

    return status_summary, bucket_summary, cat_piv_filtered, state_piv

if __name__ == '__main__':
    run_q2_analysis()
