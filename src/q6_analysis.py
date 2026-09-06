"""
Core Question 6: Root-Cause Analysis of Low Review Scores Script
Empirical investigation of factors associated with 1-star and 2-star reviews (~15.0% of orders).
Analyzes operational drivers (lateness, dispatch lags, freight ratios, state routes)
and extracts customer complaint keyphrase themes from Portuguese review text messages.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_TABLES = os.path.join(PROJECT_ROOT, 'outputs', 'tables')
OUTPUT_CHARTS = os.path.join(PROJECT_ROOT, 'outputs', 'charts')
MASTER_CSV = os.path.join(PROJECT_ROOT, 'outputs', 'exports', 'master_orders.csv')

os.makedirs(OUTPUT_TABLES, exist_ok=True)
os.makedirs(OUTPUT_CHARTS, exist_ok=True)

# Custom plot styling
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']
plt.rcParams['axes.edgecolor'] = '#CBD5E1'
plt.rcParams['axes.linewidth'] = 1.0

PALETTE = {
    'primary': '#1E3A8A',    # Dark Blue
    'secondary': '#0EA5E9',  # Sky Blue
    'accent': '#F59E0B',     # Amber
    'purple': '#8B5CF6',     # Purple
    'danger': '#EF4444',     # Red
    'dark': '#0F172A',       # Dark Slate
    'gray': '#94A3B8'        # Slate Gray
}

def annotate_bars(ax, format_str='{:.1f}', is_horizontal=False, fontsize=9, padding=3):
    """Adds data values directly to bars."""
    for p in ax.patches:
        if is_horizontal:
            width = p.get_width()
            if not np.isnan(width) and width > 0:
                ax.annotate(format_str.format(width),
                            (width, p.get_y() + p.get_height() / 2.),
                            ha='left', va='center',
                            xytext=(padding, 0), textcoords='offset points',
                            fontsize=fontsize, fontweight='bold', color='#1E293B')
        else:
            height = p.get_height()
            if not np.isnan(height) and height > 0:
                ax.annotate(format_str.format(height),
                            (p.get_x() + p.get_width() / 2., height),
                            ha='center', va='bottom',
                            xytext=(0, padding), textcoords='offset points',
                            fontsize=fontsize, fontweight='bold', color='#1E293B')

def run_q6_analysis():
    print("Ingesting master order dataset for Q6 Root-Cause Analysis...")
    master = pd.read_csv(MASTER_CSV)
    
    # Filter for reviewed orders
    df_rev = master[master['review_score'].notnull()].copy()
    total_reviewed = len(df_rev)
    
    # 1. Review Score Frequency & Breakdown
    score_counts = df_rev['review_score'].value_counts().reset_index()
    score_counts.columns = ['review_score', 'order_count']
    score_counts['review_score'] = score_counts['review_score'].astype(int)
    score_counts = score_counts.sort_values('review_score')
    score_counts['order_share_pct'] = (score_counts['order_count'] / total_reviewed) * 100
    
    score_dist_path = os.path.join(OUTPUT_TABLES, 'q6_review_score_distribution.csv')
    score_counts.to_csv(score_dist_path, index=False)
    
    # Low-rating flag (1 or 2 stars)
    df_rev['is_low_review'] = (df_rev['review_score'] <= 2).astype(int)
    total_low = df_rev['is_low_review'].sum()
    baseline_low_rate = (total_low / total_reviewed) * 100
    
    print(f"\nTotal Reviewed Orders (N): {total_reviewed:,}")
    print(f"Low Ratings (1-2 Stars): {total_low:,} ({baseline_low_rate:.2f}%)")
    print(f"  1-Star Count: {(df_rev['review_score'] == 1).sum():,} ({(df_rev['review_score'] == 1).mean()*100:.2f}%)")
    print(f"  2-Star Count: {(df_rev['review_score'] == 2).sum():,} ({(df_rev['review_score'] == 2).mean()*100:.2f}%)")

    # 2. Operational Factor Dissection & Relative Risk Calculation
    delivered_rev = df_rev[df_rev['order_status'] == 'delivered'].copy()
    
    # Driver 1: Late Delivery (delivered > estimated)
    late_orders = delivered_rev[delivered_rev['is_late'] == 1]
    ontime_orders = delivered_rev[delivered_rev['is_late'] == 0]
    late_low_rate = late_orders['is_low_review'].mean() * 100
    ontime_low_rate = ontime_orders['is_low_review'].mean() * 100
    
    # Driver 2: Severe Delay (delay >= 4 days late)
    severe_late_orders = delivered_rev[delivered_rev['delivery_delay_days'] >= 4]
    severe_late_low_rate = severe_late_orders['is_low_review'].mean() * 100
    
    # Driver 3: Slow Seller Carrier Dispatch (> 5 days to dispatch)
    slow_dispatch_orders = df_rev[df_rev['carrier_dispatch_days'] > 5]
    fast_dispatch_orders = df_rev[df_rev['carrier_dispatch_days'] <= 5]
    slow_dispatch_low_rate = slow_dispatch_orders['is_low_review'].mean() * 100
    fast_dispatch_low_rate = fast_dispatch_orders['is_low_review'].mean() * 100
    
    # Driver 4: High Freight Burden Ratio (freight_ratio > 0.50)
    high_freight_orders = df_rev[df_rev['freight_ratio'] > 0.50]
    normal_freight_orders = df_rev[df_rev['freight_ratio'] <= 0.50]
    high_freight_low_rate = high_freight_orders['is_low_review'].mean() * 100
    normal_freight_low_rate = normal_freight_orders['is_low_review'].mean() * 100

    # Driver 5: Interstate Route (customer_state != seller_state)
    interstate_orders = df_rev[df_rev['is_interstate'] == 1]
    intrastate_orders = df_rev[df_rev['is_interstate'] == 0]
    interstate_low_rate = interstate_orders['is_low_review'].mean() * 100
    intrastate_low_rate = intrastate_orders['is_low_review'].mean() * 100
    
    drivers_summary = pd.DataFrame({
        'operational_factor': [
            'Baseline Marketplace Average',
            'Delivery Status: On-Time / Early',
            'Delivery Status: Late (Delivered after estimated date)',
            'Delivery Status: Severe Late (>= 4 days late)',
            'Seller Dispatch: Fast (<= 5 days to carrier)',
            'Seller Dispatch: Slow (> 5 days to carrier)',
            'Freight Burden: Normal (Freight <= 50% of price)',
            'Freight Burden: High (Freight > 50% of price)',
            'Shipping Scope: Intra-State (Same state)',
            'Shipping Scope: Inter-State (Cross-state)'
        ],
        'sample_size_n': [
            total_reviewed,
            len(ontime_orders),
            len(late_orders),
            len(severe_late_orders),
            len(fast_dispatch_orders),
            len(slow_dispatch_orders),
            len(normal_freight_orders),
            len(high_freight_orders),
            len(intrastate_orders),
            len(interstate_orders)
        ],
        'low_review_rate_pct': [
            round(baseline_low_rate, 2),
            round(ontime_low_rate, 2),
            round(late_low_rate, 2),
            round(severe_late_low_rate, 2),
            round(fast_dispatch_low_rate, 2),
            round(slow_dispatch_low_rate, 2),
            round(normal_freight_low_rate, 2),
            round(high_freight_low_rate, 2),
            round(intrastate_low_rate, 2),
            round(interstate_low_rate, 2)
        ],
        'relative_risk_vs_baseline': [
            1.00,
            round(ontime_low_rate / baseline_low_rate, 2),
            round(late_low_rate / baseline_low_rate, 2),
            round(severe_late_low_rate / baseline_low_rate, 2),
            round(fast_dispatch_low_rate / baseline_low_rate, 2),
            round(slow_dispatch_low_rate / baseline_low_rate, 2),
            round(normal_freight_low_rate / baseline_low_rate, 2),
            round(high_freight_low_rate / baseline_low_rate, 2),
            round(intrastate_low_rate / baseline_low_rate, 2),
            round(interstate_low_rate / baseline_low_rate, 2)
        ]
    })
    
    drivers_path = os.path.join(OUTPUT_TABLES, 'q6_root_cause_analysis.csv')
    drivers_summary.to_csv(drivers_path, index=False)
    print(f"Saved Q6 root cause analysis table to {drivers_path}")

    # 3. Customer Review Comment Text Keyphrase Theme Extraction
    low_comments = df_rev[df_rev['is_low_review'] == 1]['review_comment_message'].dropna().str.lower()
    total_low_comments = len(low_comments)
    
    keywords_logistics = ['não recebi', 'nao recebi', 'atrasou', 'atraso', 'demora', 'prazo', 'recebi', 'chegou', 'entrega', 'transportadora', 'espera', 'nunca']
    keywords_quality = ['defeito', 'quebrado', 'estragado', 'diferente', 'pessima', 'péssima', 'ruim', 'qualidade', 'produto', 'falso', 'menor', 'rasgado', 'estragou']
    keywords_service = ['cancelar', 'cancelamento', 'atendimento', 'resposta', 'loja', 'seller', 'vendedor', 'nota fiscal', 'contato', 'devolução', 'devolver']
    
    cnt_logistics = low_comments.apply(lambda text: any(kw in text for kw in keywords_logistics)).sum()
    cnt_quality = low_comments.apply(lambda text: any(kw in text for kw in keywords_quality)).sum()
    cnt_service = low_comments.apply(lambda text: any(kw in text for kw in keywords_service)).sum()
    
    text_themes_df = pd.DataFrame({
        'complaint_theme': [
            'Logistics & Non-Delivery / Delay ("não recebi", "atraso", "demora", "prazo")',
            'Product Defect / Quality / Discrepancy ("defeito", "quebrado", "ruim", "qualidade")',
            'Seller Service & Post-Sale Support ("atendimento", "vendedor", "cancelar", "contato")'
        ],
        'comment_count': [cnt_logistics, cnt_quality, cnt_service],
        'pct_low_review_comments': [
            round((cnt_logistics / total_low_comments) * 100, 2),
            round((cnt_quality / total_low_comments) * 100, 2),
            round((cnt_service / total_low_comments) * 100, 2)
        ]
    })
    
    themes_path = os.path.join(OUTPUT_TABLES, 'q6_complaint_themes.csv')
    text_themes_df.to_csv(themes_path, index=False)
    print(f"Saved Q6 complaint text themes table to {themes_path}")

    # --- VISUALIZATIONS ---
    # Chart 1: Operational Factors Driving Low Ratings (Relative Risk Waterfall)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    
    plot_df = drivers_summary[drivers_summary['operational_factor'] != 'Baseline Marketplace Average'].copy()
    plot_df = plot_df.sort_values('low_review_rate_pct', ascending=True)
    
    colors = [PALETTE['primary'] if r <= 1.0 else PALETTE['danger'] for r in plot_df['relative_risk_vs_baseline']]
    
    bars = ax.barh(plot_df['operational_factor'], plot_df['low_review_rate_pct'], color=colors, height=0.6)
    
    ax.set_title('Operational Factors Associated with Low Review Scores (1-2 Stars %)', fontsize=13, fontweight='bold', pad=15)
    ax.set_xlabel('Low Review Rate (%)', fontsize=11, fontweight='semibold')
    ax.axvline(baseline_low_rate, color=PALETTE['dark'], linestyle='--', linewidth=1.5, label=f'Baseline Rate ({baseline_low_rate:.1f}%)')
    
    ax.grid(True, linestyle='--', alpha=0.3, axis='x')
    annotate_bars(ax, format_str='{:.1f}%', is_horizontal=True, fontsize=9, padding=3)
    ax.legend(loc='lower right', frameon=True, facecolor='white', edgecolor='#CBD5E1')
    
    plt.tight_layout()
    chart1_path = os.path.join(OUTPUT_CHARTS, 'q6_low_review_drivers.png')
    plt.savefig(chart1_path, dpi=300)
    plt.close()
    print(f"Saved chart to {chart1_path}")

    # Chart 2: Customer Complaint Text Themes Breakdown
    fig, ax = plt.subplots(figsize=(9, 5))
    
    b = ax.bar(text_themes_df['complaint_theme'], text_themes_df['pct_low_review_comments'], 
               color=[PALETTE['danger'], PALETTE['accent'], PALETTE['purple']], width=0.45)
    
    ax.set_title(f'Customer Complaint Themes in Low-Rated Review Comments (N = {total_low_comments:,})', fontsize=13, fontweight='bold', pad=15)
    ax.set_xlabel('Complaint Category (Portuguese Keyphrase Extraction)', fontsize=11, fontweight='semibold')
    ax.set_ylabel('Share of Low Rating Comments (%)', fontsize=11, fontweight='semibold')
    ax.set_xticklabels(['Logistics / Delivery\n(Delay & Non-Arrival)', 'Product Quality\n(Defect & Discrepancy)', 'Seller & Customer Service\n(Support & Cancellation)'], fontsize=10, fontweight='semibold')
    
    ax.grid(True, linestyle='--', alpha=0.3, axis='y')
    annotate_bars(ax, format_str='{:.1f}%', fontsize=10, padding=3)
    
    plt.tight_layout()
    chart2_path = os.path.join(OUTPUT_CHARTS, 'q6_complaint_themes.png')
    plt.savefig(chart2_path, dpi=300)
    plt.close()
    print(f"Saved chart to {chart2_path}")

    # Print summary to console
    print("\n=== Q6 ROOT CAUSE DRIVERS SUMMARY ===")
    print(drivers_summary[['operational_factor', 'sample_size_n', 'low_review_rate_pct', 'relative_risk_vs_baseline']])
    
    print("\n=== Q6 COMPLAINT TEXT THEMES SUMMARY ===")
    print(text_themes_df)

if __name__ == '__main__':
    run_q6_analysis()
