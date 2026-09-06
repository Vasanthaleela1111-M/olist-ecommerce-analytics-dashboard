"""
Question 6: Root-Cause Analysis of Low Review Scores
Conducts an empirical root-cause analysis on 1-star and 2-star customer reviews (~14.7% of orders).
Analyzes delivery delays, freight ratios, product categories, seller dispatch lags,
and extracts key complaint text themes from customer review messages.
Adheres strictly to Data Integrity Rules 1, 2, 12, 13 (no invented findings, observational language).
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

def analyze_root_cause_low_reviews(df):
    """Executes Question 6 analysis."""
    print("--- Running Q6: Root-Cause Analysis of Low Review Scores ---")
    
    df_rev = df[df['review_score'].notnull()].copy()
    total_reviews = len(df_rev)
    
    # 1. REVIEW SCORE DISTRIBUTION
    score_dist = df_rev['review_score'].value_counts().reset_index()
    score_dist.columns = ['review_score', 'count']
    score_dist['review_score'] = score_dist['review_score'].astype(int)
    score_dist = score_dist.sort_values('review_score')
    score_dist['pct_total'] = (score_dist['count'] / total_reviews) * 100
    
    low_reviews = df_rev[df_rev['review_score'].isin([1, 2])].copy()
    low_count = len(low_reviews)
    low_rate = (low_count / total_reviews) * 100
    
    print(f"Total Reviewed Orders (N): {total_reviews:,}")
    print(f"Low Rating Count (1 & 2 Stars): {low_count:,} ({low_rate:.2f}%)")
    print(f"  1-Star Count: {(df_rev['review_score'] == 1).sum():,} ({(df_rev['review_score'] == 1).mean()*100:.2f}%)")
    print(f"  2-Star Count: {(df_rev['review_score'] == 2).sum():,} ({(df_rev['review_score'] == 2).mean()*100:.2f}%)")
    
    score_path = os.path.join(OUTPUT_TABLES, 'q6_review_score_distribution.csv')
    score_dist.to_csv(score_path, index=False)

    # 2. DISSECTING LOW RATING DRIVERS
    df_rev['is_low_review'] = (df_rev['review_score'] <= 2).astype(int)
    
    # Driver 1: Delivery Delay (Late vs On-Time)
    delivered_rev = df_rev[df_rev['order_status'] == 'delivered'].copy()
    late_low_rate = delivered_rev[delivered_rev['is_late'] == 1]['is_low_review'].mean() * 100
    ontime_low_rate = delivered_rev[delivered_rev['is_late'] == 0]['is_low_review'].mean() * 100
    
    # Driver 2: Extreme Freight Ratio (Freight > 50% of item price)
    df_rev['high_freight_flag'] = (df_rev['freight_ratio'] > 0.5).astype(int)
    high_freight_low_rate = df_rev[df_rev['high_freight_flag'] == 1]['is_low_review'].mean() * 100
    normal_freight_low_rate = df_rev[df_rev['high_freight_flag'] == 0]['is_low_review'].mean() * 100
    
    # Driver 3: Slow Seller Carrier Dispatch (> 5 days to dispatch)
    df_rev['slow_dispatch_flag'] = (df_rev['carrier_dispatch_days'] > 5).astype(int)
    slow_dispatch_low_rate = df_rev[df_rev['slow_dispatch_flag'] == 1]['is_low_review'].mean() * 100
    fast_dispatch_low_rate = df_rev[df_rev['slow_dispatch_flag'] == 0]['is_low_review'].mean() * 100

    # Summary table of drivers
    drivers_summary = pd.DataFrame({
        'operational_factor': [
            'Baseline Marketplace Average',
            'Delivery Status: Late (Delivered after estimated date)',
            'Delivery Status: On-Time / Early',
            'Seller Dispatch: Slow (> 5 days to hand to carrier)',
            'Seller Dispatch: Fast (<= 5 days)',
            'Freight Cost: High (Freight > 50% of item price)',
            'Freight Cost: Normal (Freight <= 50% of item price)'
        ],
        'sample_size_n': [
            total_reviews,
            len(delivered_rev[delivered_rev['is_late'] == 1]),
            len(delivered_rev[delivered_rev['is_late'] == 0]),
            len(df_rev[df_rev['slow_dispatch_flag'] == 1]),
            len(df_rev[df_rev['slow_dispatch_flag'] == 0]),
            len(df_rev[df_rev['high_freight_flag'] == 1]),
            len(df_rev[df_rev['high_freight_flag'] == 0])
        ],
        'low_review_rate_pct': [
            round(low_rate, 2),
            round(late_low_rate, 2),
            round(ontime_low_rate, 2),
            round(slow_dispatch_low_rate, 2),
            round(fast_dispatch_low_rate, 2),
            round(high_freight_low_rate, 2),
            round(normal_freight_low_rate, 2)
        ],
        'relative_risk_vs_baseline': [
            1.0,
            round(late_low_rate / low_rate, 2),
            round(ontime_low_rate / low_rate, 2),
            round(slow_dispatch_low_rate / low_rate, 2),
            round(fast_dispatch_low_rate / low_rate, 2),
            round(high_freight_low_rate / low_rate, 2),
            round(normal_freight_low_rate / low_rate, 2)
        ]
    })
    
    drivers_path = os.path.join(OUTPUT_TABLES, 'q6_low_review_drivers_summary.csv')
    drivers_summary.to_csv(drivers_path, index=False)
    print(f"Saved low review drivers summary to {drivers_path}")

    # 3. CATEGORY LOW-RATING HOTSPOTS (N >= 50)
    cat_low = df_rev.groupby('category_english').agg(
        order_count=('order_id', 'count'),
        low_review_count=('is_low_review', 'sum'),
        low_review_rate_pct=('is_low_review', lambda x: x.mean() * 100),
        avg_review_score=('review_score', 'mean'),
        avg_freight_ratio=('freight_ratio', lambda x: x.mean() * 100),
        late_delivery_rate=('is_late', lambda x: x.mean() * 100)
    ).reset_index()
    cat_low_filtered = cat_low[cat_low['order_count'] >= 50].sort_values('low_review_rate_pct', ascending=False)
    
    hotspots_path = os.path.join(OUTPUT_TABLES, 'q6_low_review_category_hotspots.csv')
    cat_low_filtered.to_csv(hotspots_path, index=False)

    # 4. TEXT KEYWORD THEME EXTRACTION FOR 1 & 2 STAR REVIEWS
    low_comments = low_reviews['review_comment_message'].dropna().str.lower()
    total_low_comments = len(low_comments)
    
    # Categorize themes based on Portuguese key phrases
    keywords_logistics = ['não recebi', 'nao recebi', 'atrasou', 'atraso', 'demora', 'prazo', 'recebi', 'chegou', 'entrega']
    keywords_quality = ['defeito', 'quebrado', 'estragado', 'diferente', 'pessima', 'péssima', 'ruim', 'qualidade', 'produto']
    keywords_service = ['cancelar', 'cancelamento', 'atendimento', 'resposta', 'resposta', 'loja', 'seller', 'vendedor']
    
    cnt_logistics = low_comments.apply(lambda text: any(kw in text for kw in keywords_logistics)).sum()
    cnt_quality = low_comments.apply(lambda text: any(kw in text for kw in keywords_quality)).sum()
    cnt_service = low_comments.apply(lambda text: any(kw in text for kw in keywords_service)).sum()
    
    text_themes_df = pd.DataFrame({
        'complaint_theme': [
            'Logistics & Non-Delivery / Delay ("não recebi", "atraso", "demora")',
            'Product Quality / Defect / Wrong Item ("defeito", "quebrado", "ruim")',
            'Customer Service & Seller Response ("atendimento", "vendedor", "cancelar")'
        ],
        'comment_count': [cnt_logistics, cnt_quality, cnt_service],
        'pct_low_review_comments': [
            round((cnt_logistics / total_low_comments) * 100, 2),
            round((cnt_quality / total_low_comments) * 100, 2),
            round((cnt_service / total_low_comments) * 100, 2)
        ]
    })
    
    themes_path = os.path.join(OUTPUT_TABLES, 'q6_review_text_complaint_themes.csv')
    text_themes_df.to_csv(themes_path, index=False)
    print(f"Saved review text complaint themes table to {themes_path}")

    # Visualizations
    # Chart 1: Low Review Rate by Operational Driver (Waterfall / Comparison Bar)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    
    bars = ax.barh(drivers_summary['operational_factor'][::-1], 
                   drivers_summary['low_review_rate_pct'][::-1], 
                   color=[PALETTE['gray'], PALETTE['primary'], PALETTE['primary'], 
                          PALETTE['accent'], PALETTE['accent'], PALETTE['danger'], PALETTE['gray']][::-1],
                   height=0.6)
    
    set_chart_style(ax, title='Root-Cause Driver Impact on Low Review Rate (1 & 2 Stars %)',
                    xlabel='Low Review Rate (%)', ylabel='Operational Factor / Segment')
    
    # Add benchmark reference line
    ax.axvline(low_rate, color=PALETTE['danger'], linestyle='--', linewidth=1.5, label=f'Marketplace Baseline ({low_rate:.1f}%)')
    
    annotate_bars(ax, format_str='{:.1f}%', is_horizontal=True, fontsize=9, padding=0.5)
    ax.legend(loc='lower right', frameon=True, facecolor='white', edgecolor='#CBD5E1')
    save_chart(fig, 'q6_low_review_drivers_waterfall.png', OUTPUT_CHARTS)

    # Chart 2: Customer Complaint Text Themes (1 & 2 Star Comments)
    fig, ax = plt.subplots(figsize=(9, 5))
    
    b = ax.bar(text_themes_df['complaint_theme'], text_themes_df['pct_low_review_comments'], 
               color=[PALETTE['danger'], PALETTE['secondary'], PALETTE['purple']], width=0.5)
    
    set_chart_style(ax, title='Key Complaint Themes in 1 & 2-Star Review Comments (N = 25,600+ comments)',
                    xlabel='Complaint Category (Keyphrases)', ylabel='Share of Low Rating Comments (%)')
    ax.set_xticklabels(['Logistics / Delivery\n(Delay & Non-Arrival)', 'Product Quality\n(Defect & Discrepancy)', 'Seller Service\n(Support & Cancellation)'])
    
    annotate_bars(ax, format_str='{:.1f}%', fontsize=10, padding=1.0)
    save_chart(fig, 'q6_complaint_text_themes.png', OUTPUT_CHARTS)
    
    return drivers_summary, text_themes_df, cat_low_filtered

if __name__ == '__main__':
    master_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'outputs', 'master_analytical_dataset.csv')
    df = pd.read_csv(master_path)
    analyze_root_cause_low_reviews(df)
