"""
Question 10: Seller SLA Health Scorecard & Automated Badge System
Evaluates performance metrics across all 3,095 sellers on the Olist platform,
computes Dispatch SLA compliance rates, late delivery rates, and review score averages,
and assigns automated performance grades (Grades A+, A, B, C, F) for executive seller governance.
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

def analyze_seller_health_scorecard(df):
    """Executes Question 10 Seller SLA Health Scorecard Analysis."""
    print("--- Running Q10: Seller SLA Health Scorecard & Automated Badge System ---")
    
    df_valid = df[df['primary_seller_id'].notnull()].copy()
    
    # 1. SELLER AGGREGATION AT SELLER_ID GRAIN
    seller_agg = df_valid.groupby('primary_seller_id').agg(
        seller_state=('seller_state', 'first'),
        order_count=('order_id', 'nunique'),
        total_gmv=('total_price', lambda x: x.fillna(0).sum()),
        total_freight=('total_freight', lambda x: x.fillna(0).sum()),
        avg_review_score=('review_score', 'mean'),
        review_count=('review_score', lambda x: x.notnull().sum()),
        low_rating_count=('review_score', lambda x: (x <= 2).sum()),
        delivered_count=('order_status', lambda x: (x == 'delivered').sum()),
        late_delivery_count=('is_late', lambda x: (x == 1).sum()),
        slow_dispatch_count=('carrier_dispatch_days', lambda x: (x > 3).sum())
    ).reset_index()
    
    # Derived percentage metrics
    seller_agg['low_rating_rate_pct'] = np.where(seller_agg['review_count'] > 0, (seller_agg['low_rating_count'] / seller_agg['review_count']) * 100, np.nan)
    seller_agg['late_delivery_rate_pct'] = np.where(seller_agg['delivered_count'] > 0, (seller_agg['late_delivery_count'] / seller_agg['delivered_count']) * 100, 0.0)
    seller_agg['dispatch_sla_compliance_pct'] = np.where(seller_agg['order_count'] > 0, (1 - (seller_agg['slow_dispatch_count'] / seller_agg['order_count'])) * 100, 100.0)
    
    # 2. AUTOMATED SELLER HEALTH GRADING ALGORITHM
    def assign_seller_grade(row):
        score = row['avg_review_score']
        late = row['late_delivery_rate_pct']
        sla = row['dispatch_sla_compliance_pct']
        
        if pd.isna(score) or row['order_count'] < 3:
            return 'Grade B (Unrated / New)'
            
        if score >= 4.4 and late <= 4.0 and sla >= 90.0:
            return 'Grade A+ (Elite Champion)'
        elif score >= 4.1 and late <= 7.0 and sla >= 80.0:
            return 'Grade A (High Performer)'
        elif score >= 3.8 and late <= 10.0 and sla >= 70.0:
            return 'Grade B (Standard)'
        elif score >= 3.4 and late <= 15.0:
            return 'Grade C (At Risk)'
        else:
            return 'Grade F (Critical Intervention)'
            
    seller_agg['health_grade'] = seller_agg.apply(assign_seller_grade, axis=1)
    
    total_sellers = len(seller_agg)
    print(f"Total Evaluated Sellers: {total_sellers:,}")
    
    # Export seller scorecard table
    scorecard_path = os.path.join(OUTPUT_TABLES, 'q10_seller_health_scorecard.csv')
    seller_agg.to_csv(scorecard_path, index=False)
    print(f"Saved seller health scorecard to {scorecard_path}")
    
    # 3. GRADE DISTRIBUTION SUMMARY
    grade_dist = seller_agg.groupby('health_grade').agg(
        seller_count=('primary_seller_id', 'count'),
        total_orders=('order_count', 'sum'),
        total_gmv=('total_gmv', 'sum'),
        avg_review=('avg_review_score', 'mean'),
        avg_late_rate=('late_delivery_rate_pct', 'mean'),
        avg_dispatch_sla=('dispatch_sla_compliance_pct', 'mean')
    ).reset_index()
    
    grade_dist['pct_sellers'] = (grade_dist['seller_count'] / total_sellers) * 100
    total_platform_gmv = seller_agg['total_gmv'].sum()
    grade_dist['pct_gmv'] = (grade_dist['total_gmv'] / total_platform_gmv) * 100
    
    grade_order = [
        'Grade A+ (Elite Champion)',
        'Grade A (High Performer)',
        'Grade B (Standard)',
        'Grade B (Unrated / New)',
        'Grade C (At Risk)',
        'Grade F (Critical Intervention)'
    ]
    
    grade_dist = grade_dist.set_index('health_grade').reindex(grade_order).dropna(subset=['seller_count']).reset_index()
    
    dist_path = os.path.join(OUTPUT_TABLES, 'q10_seller_grade_distribution.csv')
    grade_dist.to_csv(dist_path, index=False)
    print(f"Saved seller grade distribution summary to {dist_path}")
    
    print("\n--- SELLER HEALTH GRADE DISTRIBUTION SUMMARY ---")
    print(grade_dist[['health_grade', 'seller_count', 'pct_sellers', 'total_orders', 'pct_gmv', 'avg_review']].to_string(index=False))
    
    # 4. CHART 1: SELLER HEALTH GRADE DISTRIBUTION BAR CHART
    fig, ax = plt.subplots(figsize=(10, 5.5))
    set_chart_style(ax, title=f'Olist Seller Network Health Grade Distribution (N = {total_sellers:,} Sellers)', xlabel='Seller Count', ylabel='Health Grade Tier')
    
    grade_colors = ['#10B981', '#38BDF8', '#6366F1', '#94A3B8', '#F59E0B', '#EF4444']
    bars = ax.barh(grade_dist['health_grade'], grade_dist['seller_count'], color=grade_colors, height=0.6)
    ax.invert_yaxis()
    
    for bar in bars:
        w = bar.get_width()
        pct = (w / total_sellers) * 100
        ax.annotate(f'{int(w):,} ({pct:.1f}%)', xy=(w, bar.get_y() + bar.get_height()/2), xytext=(5, 0), textcoords="offset points", ha='left', va='center', fontweight='bold', color='#1E293B')
        
    save_chart(fig, 'q10_seller_grade_distribution.png')
    
    # 5. CHART 2: DISPATCH SLA COMPLIANCE VS REVIEW SCORE RELATIONSHIP
    fig, ax = plt.subplots(figsize=(9, 5))
    set_chart_style(ax, title='Seller Dispatch SLA Compliance (%) vs. Average Review Score', xlabel='Dispatch SLA Compliance Rate (%)', ylabel='Average Review Score (Stars)')
    
    ax.scatter(seller_agg['dispatch_sla_compliance_pct'], seller_agg['avg_review_score'], alpha=0.35, color='#0EA5E9', edgecolors='none', s=25)
    ax.axvline(80, color='#F59E0B', linestyle='--', linewidth=1.5, label='80% Dispatch SLA Target')
    ax.axhline(4.0, color='#10B981', linestyle='--', linewidth=1.5, label='4.0 Star Rating Target')
    ax.legend(loc='lower right', facecolor='#F8FAFC', edgecolor='#CBD5E1')
    
    save_chart(fig, 'q10_seller_dispatch_vs_review.png')
    
    print("Q10 Seller SLA Health Scorecard Analysis Complete!")
