"""
Question 2: Delivery Performance and Customer Satisfaction
Analyzes delivery lead time (actual vs estimated), on-time vs late delivery rates,
logistics component delays, and the statistical relationship with review scores.
Follows Data Integrity Rule 11 (delivered orders filter) and Rule 13 (observational language).
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.visualization import set_chart_style, annotate_bars, save_chart, PALETTE

OUTPUT_TABLES = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'outputs', 'tables')
OUTPUT_CHARTS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'outputs', 'charts')

def analyze_delivery_performance(df):
    """Executes Question 2 analysis."""
    print("--- Running Q2: Delivery Performance & Customer Satisfaction ---")
    
    # Rule 11: Filter for delivered orders with valid delivery timestamps
    delivered = df[
        (df['order_status'] == 'delivered') & 
        (df['order_delivered_customer_date'].notnull()) & 
        (df['order_estimated_delivery_date'].notnull())
    ].copy()
    
    total_delivered = len(delivered)
    late_orders = delivered[delivered['is_late'] == 1]
    ontime_orders = delivered[delivered['is_late'] == 0]
    
    ontime_count = len(ontime_orders)
    late_count = len(late_orders)
    ontime_rate = (ontime_count / total_delivered) * 100
    late_rate = (late_count / total_delivered) * 100
    
    avg_actual_lead_time = delivered['delivery_lead_time_days'].mean()
    median_actual_lead_time = delivered['delivery_lead_time_days'].median()
    avg_estimated_lead_time = delivered['estimated_lead_time_days'].mean()
    median_estimated_lead_time = delivered['estimated_lead_time_days'].median()
    
    avg_delay_all = delivered['delivery_delay_days'].mean()
    avg_delay_late_only = late_orders['delivery_delay_days'].mean()
    median_delay_late_only = late_orders['delivery_delay_days'].median()
    
    avg_approval_delay_hrs = delivered['approval_delay_hours'].mean()
    avg_dispatch_days = delivered['carrier_dispatch_days'].mean()
    avg_transit_days = delivered['carrier_transit_days'].mean()
    
    # Review score comparison
    avg_review_ontime = ontime_orders['review_score'].mean()
    avg_review_late = late_orders['review_score'].mean()
    pct_1star_ontime = (ontime_orders['review_score'] == 1).mean() * 100
    pct_1star_late = (late_orders['review_score'] == 1).mean() * 100
    
    # Correlation between delivery delay (days late) and review score
    valid_review_delay = delivered.dropna(subset=['review_score', 'delivery_delay_days'])
    corr_delay_review = valid_review_delay['delivery_delay_days'].corr(valid_review_delay['review_score'])
    
    print(f"Total Delivered Orders Analyzed (N): {total_delivered:,}")
    print(f"On-Time Delivery Rate: {ontime_rate:.2f}% ({ontime_count:,} orders)")
    print(f"Late Delivery Rate: {late_rate:.2f}% ({late_count:,} orders)")
    print(f"Actual Lead Time - Mean: {avg_actual_lead_time:.2f} days, Median: {median_actual_lead_time:.2f} days")
    print(f"Estimated Lead Time - Mean: {avg_estimated_lead_time:.2f} days, Median: {median_estimated_lead_time:.2f} days")
    print(f"Logistics Component Breakdown - Dispatch: {avg_dispatch_days:.2f} days, Transit: {avg_transit_days:.2f} days")
    print(f"Average Review Score - On-Time: {avg_review_ontime:.2f} vs Late: {avg_review_late:.2f}")
    print(f"1-Star Review Rate - On-Time: {pct_1star_ontime:.2f}% vs Late: {pct_1star_late:.2f}%")
    print(f"Correlation (Delivery Delay vs Review Score): r = {corr_delay_review:.4f}")
    
    # Delivery performance summary table
    summary_data = {
        'metric': [
            'Total Delivered Orders (Denominator N)',
            'On-Time Delivery Rate (%)',
            'Late Delivery Rate (%)',
            'Mean Actual Delivery Lead Time (Days)',
            'Median Actual Delivery Lead Time (Days)',
            'Mean Estimated Delivery Lead Time (Days)',
            'Mean Carrier Dispatch Delay (Days)',
            'Mean Carrier Transit Time (Days)',
            'Mean Delay for Late Orders (Days)',
            'Median Delay for Late Orders (Days)',
            'Average Review Score (On-Time Orders)',
            'Average Review Score (Late Orders)',
            '1-Star Review Rate (On-Time Orders %)',
            '1-Star Review Rate (Late Orders %)',
            'Correlation (Delay Days vs Review Score r)'
        ],
        'value': [
            total_delivered,
            round(ontime_rate, 2),
            round(late_rate, 2),
            round(avg_actual_lead_time, 2),
            round(median_actual_lead_time, 2),
            round(avg_estimated_lead_time, 2),
            round(avg_dispatch_days, 2),
            round(avg_transit_days, 2),
            round(avg_delay_late_only, 2),
            round(median_delay_late_only, 2),
            round(avg_review_ontime, 2),
            round(avg_review_late, 2),
            round(pct_1star_ontime, 2),
            round(pct_1star_late, 2),
            round(corr_delay_review, 4)
        ]
    }
    summary_df = pd.DataFrame(summary_data)
    summary_path = os.path.join(OUTPUT_TABLES, 'q2_delivery_performance_summary.csv')
    summary_df.to_csv(summary_path, index=False)
    
    # Granular Delay Buckets Analysis
    def get_delay_bucket(row):
        if row['is_late'] == 0:
            diff = -row['delivery_delay_days'] # early days
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
        pct_5_star=('review_score', lambda x: (x == 5).mean() * 100),
        pct_1_star=('review_score', lambda x: (x == 1).mean() * 100),
        avg_actual_lead_time=('delivery_lead_time_days', 'mean')
    ).reset_index()
    bucket_summary['pct_total_orders'] = (bucket_summary['order_count'] / total_delivered) * 100
    
    bucket_path = os.path.join(OUTPUT_TABLES, 'q2_review_score_by_delay_bucket.csv')
    bucket_summary.to_csv(bucket_path, index=False)
    print(f"Saved delay bucket analysis table to {bucket_path}")

    # Customer State Delivery Performance & Interaction Table
    df['is_low_rating'] = (df['review_score'] <= 2).astype(int)
    delivered['is_low_rating'] = (delivered['review_score'] <= 2).astype(int)

    state_overall = df.groupby('customer_state').agg(
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
    # Chart 1: Actual vs Estimated Lead Time Distribution
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Clip lead times to 50 days for clean visualization
    lead_clipped = delivered['delivery_lead_time_days'].clip(0, 50)
    est_clipped = delivered['estimated_lead_time_days'].clip(0, 50)
    
    sns.histplot(lead_clipped, ax=ax, color=PALETTE['secondary'], label=f'Actual Lead Time (Mean: {avg_actual_lead_time:.1f}d)', 
                 kde=True, stat='density', alpha=0.4, bins=40)
    sns.histplot(est_clipped, ax=ax, color=PALETTE['primary'], label=f'Estimated Lead Time (Mean: {avg_estimated_lead_time:.1f}d)', 
                 kde=True, stat='density', alpha=0.3, bins=40)
    
    set_chart_style(ax, title='Olist Delivery Lead Time Distribution: Actual vs. Estimated',
                    xlabel='Delivery Days', ylabel='Density')
    ax.legend(loc='upper right', frameon=True, facecolor='white', edgecolor='#CBD5E1')
    save_chart(fig, 'q2_delivery_lead_time_distribution.png', OUTPUT_CHARTS)

    # Chart 2: Customer Satisfaction (Review Score & 1-Star Rate) by Delay Severity Bucket
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()
    
    x = np.arange(len(bucket_summary))
    width = 0.4
    
    b1 = ax1.bar(x - width/2, bucket_summary['avg_review_score'], width, color=PALETTE['primary'], label='Avg Review Score (1-5 Stars)')
    b2 = ax2.bar(x + width/2, bucket_summary['pct_1_star'], width, color=PALETTE['danger'], label='1-Star Review Rate (%)')
    
    set_chart_style(ax1, title='Impact of Delivery Lateness on Customer Review Scores',
                    xlabel='Delivery Timing Bucket', ylabel='Average Review Score (1 - 5 Stars)')
    ax2.set_ylabel('1-Star Review Rate (%)', fontsize=11, fontweight='semibold', color=PALETTE['danger'])
    ax1.set_xticks(x)
    ax1.set_xticklabels(bucket_summary['delay_bucket'], rotation=35, ha='right')
    ax1.set_ylim(0, 5.5)
    
    annotate_bars(ax1, format_str='{:.2f}', fontsize=9, padding=0.08)
    annotate_bars(ax2, format_str='{:.1f}%', fontsize=9, padding=0.8)
    
    # Combined legend
    lines = [b1, b2]
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left', frameon=True, facecolor='white', edgecolor='#CBD5E1')
    
    save_chart(fig, 'q2_review_score_vs_delivery_lateness.png', OUTPUT_CHARTS)
    
    return summary_df, bucket_summary

if __name__ == '__main__':
    master_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'outputs', 'master_analytical_dataset.csv')
    df = pd.read_csv(master_path)
    analyze_delivery_performance(df)
