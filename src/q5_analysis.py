"""
Core Question 5: Payment Behavior Analysis Script
Analyzes payment method distribution, credit card installment scaling,
and multi-payment sequential usage patterns using master_orders.csv.
Exports outputs/tables/q5_payment_analysis.csv as requested.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

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
    'dark': '#0F172A'        # Dark Slate
}

def annotate_bars(ax, format_str='{:.1f}', fontsize=9, padding=3):
    """Adds data values directly above bars."""
    for p in ax.patches:
        height = p.get_height()
        if not np.isnan(height) and height > 0:
            ax.annotate(format_str.format(height),
                        (p.get_x() + p.get_width() / 2., height),
                        ha='center', va='bottom',
                        xytext=(0, padding), textcoords='offset points',
                        fontsize=fontsize, fontweight='bold', color='#1E293B')

def run_q5_analysis():
    print("Ingesting master order dataset for Q5 Payment Behavior Analysis...")
    master = pd.read_csv(MASTER_CSV)
    total_orders = len(master)
    
    # 1. Payment Method Breakdown
    valid_pay = master[master['primary_payment_type'].notnull()].copy()
    total_valid_pay = len(valid_pay)
    total_platform_payment_val = valid_pay['total_payment_value'].sum()
    
    pay_dist = valid_pay.groupby('primary_payment_type').agg(
        order_count=('order_id', 'count'),
        total_payment_value=('total_payment_value', 'sum'),
        avg_payment_value=('total_payment_value', 'mean'),
        median_payment_value=('total_payment_value', 'median'),
        avg_review_score=('review_score', 'mean'),
        low_rating_count=('review_score', lambda s: (s <= 2).sum()),
        delivered_orders=('order_delivered_customer_date', 'count'),
        late_count=('is_late', lambda s: (s == 1).sum())
    ).reset_index().sort_values('order_count', ascending=False)
    
    pay_dist['order_share_pct'] = (pay_dist['order_count'] / total_valid_pay) * 100
    pay_dist['value_share_pct'] = (pay_dist['total_payment_value'] / total_platform_payment_val) * 100
    pay_dist['low_rating_rate_pct'] = (pay_dist['low_rating_count'] / pay_dist['order_count']) * 100
    pay_dist['late_rate_pct'] = (pay_dist['late_count'] / pay_dist['delivered_orders']) * 100
    
    pay_dist_path = os.path.join(OUTPUT_TABLES, 'q5_payment_method_distribution.csv')
    pay_dist.to_csv(pay_dist_path, index=False)
    print(f"Saved Q5 payment distribution table to {pay_dist_path}")
    
    # 2. Credit Card Installment Tier Analysis
    cc_orders = valid_pay[valid_pay['primary_payment_type'] == 'credit_card'].copy()
    total_cc_orders = len(cc_orders)
    
    def assign_installment_tier(inst):
        if inst == 1: return '1. 1 Installment (Single Pay)'
        elif inst <= 3: return '2. 2 - 3 Installments'
        elif inst <= 6: return '3. 4 - 6 Installments'
        elif inst <= 10: return '4. 7 - 10 Installments'
        else: return '5. 11+ Installments'
        
    cc_orders['installment_tier'] = cc_orders['max_installments'].apply(assign_installment_tier)
    
    inst_summary = cc_orders.groupby('installment_tier').agg(
        order_count=('order_id', 'count'),
        total_payment_value=('total_payment_value', 'sum'),
        avg_payment_value=('total_payment_value', 'mean'),
        median_payment_value=('total_payment_value', 'median'),
        avg_review_score=('review_score', 'mean'),
        low_rating_count=('review_score', lambda s: (s <= 2).sum()),
        delivered_orders=('order_delivered_customer_date', 'count'),
        late_count=('is_late', lambda s: (s == 1).sum())
    ).reset_index()
    
    inst_summary['order_share_pct'] = (inst_summary['order_count'] / total_cc_orders) * 100
    inst_summary['value_share_pct'] = (inst_summary['total_payment_value'] / cc_orders['total_payment_value'].sum()) * 100
    inst_summary['low_rating_rate_pct'] = (inst_summary['low_rating_count'] / inst_summary['order_count']) * 100
    inst_summary['late_rate_pct'] = (inst_summary['late_count'] / inst_summary['delivered_orders']) * 100
    
    # AOV Scaling ratio compared to 1 installment
    single_pay_aov = inst_summary.loc[inst_summary['installment_tier'].str.startswith('1'), 'avg_payment_value'].values[0]
    inst_summary['aov_multiplier_vs_single'] = inst_summary['avg_payment_value'] / single_pay_aov
    
    inst_path = os.path.join(OUTPUT_TABLES, 'q5_credit_card_installments.csv')
    inst_summary.to_csv(inst_path, index=False)
    print(f"Saved Q5 credit card installments summary to {inst_path}")

    # 3. Create Consolidated q5_payment_analysis.csv
    # Format payment type rows
    df_p_type = pay_dist.copy()
    df_p_type['dimension'] = 'Payment Type'
    df_p_type['segment'] = df_p_type['primary_payment_type']
    
    # Format credit card installment rows
    df_p_inst = inst_summary.copy()
    df_p_inst['dimension'] = 'Credit Card Installment Tier'
    df_p_inst['segment'] = df_p_inst['installment_tier']
    
    cols = ['dimension', 'segment', 'order_count', 'order_share_pct', 'total_payment_value', 'value_share_pct', 'avg_payment_value', 'median_payment_value', 'avg_review_score', 'low_rating_count', 'low_rating_rate_pct', 'late_rate_pct']
    
    q5_consolidated = pd.concat([df_p_type[cols], df_p_inst[cols]], ignore_index=True)
    q5_main_path = os.path.join(OUTPUT_TABLES, 'q5_payment_analysis.csv')
    q5_consolidated.to_csv(q5_main_path, index=False)
    print(f"Saved consolidated Q5 analysis table to {q5_main_path}")

    # 4. Multi-Payment Sequential Analysis
    seq_summary = valid_pay.groupby('payment_sequential_count').agg(
        order_count=('order_id', 'count'),
        total_payment_value=('total_payment_value', 'sum'),
        avg_payment_value=('total_payment_value', 'mean')
    ).reset_index()
    seq_summary['order_share_pct'] = (seq_summary['order_count'] / total_valid_pay) * 100
    
    seq_path = os.path.join(OUTPUT_TABLES, 'q5_multi_payment_summary.csv')
    seq_summary.to_csv(seq_path, index=False)
    print(f"Saved Q5 multi-payment summary to {seq_path}")

    # --- VISUALIZATIONS ---
    # Chart 1: Payment Method Share (%) vs Average Order Value (AOV)
    fig, ax1 = plt.subplots(figsize=(10, 5.5))
    ax2 = ax1.twinx()
    
    x = np.arange(len(pay_dist))
    width = 0.35
    
    b1 = ax1.bar(x - width/2, pay_dist['order_share_pct'], width, color=PALETTE['primary'], label='Order Share (%)')
    b2 = ax2.bar(x + width/2, pay_dist['avg_payment_value'], width, color=PALETTE['secondary'], label='Average Order Value (R$)')
    
    ax1.set_title('Olist Payment Method Distribution & Order Value (AOV)', fontsize=13, fontweight='bold', pad=15)
    ax1.set_xlabel('Primary Payment Method', fontsize=11, fontweight='semibold')
    ax1.set_ylabel('Order Share (%)', fontsize=11, fontweight='semibold', color=PALETTE['primary'])
    ax2.set_ylabel('Average Order Value (R$)', fontsize=11, fontweight='semibold', color=PALETTE['secondary'])
    
    ax1.set_xticks(x)
    ax1.set_xticklabels([t.replace('_', ' ').title() for t in pay_dist['primary_payment_type']], fontsize=10, fontweight='semibold')
    ax1.grid(True, linestyle='--', alpha=0.3, axis='y')
    
    annotate_bars(ax1, format_str='{:.1f}%', fontsize=9, padding=2)
    annotate_bars(ax2, format_str='R$ {:.0f}', fontsize=9, padding=2)
    
    lines = [b1, b2]
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper right', frameon=True, facecolor='white', edgecolor='#CBD5E1')
    
    plt.tight_layout()
    chart1_path = os.path.join(OUTPUT_CHARTS, 'q5_payment_method_shares.png')
    plt.savefig(chart1_path, dpi=300)
    plt.close()
    print(f"Saved chart to {chart1_path}")

    # Chart 2: Credit Card Installment Tier vs Order Value (AOV Multiplier)
    fig, ax1 = plt.subplots(figsize=(10, 5.5))
    ax2 = ax1.twinx()
    
    x_inst = np.arange(len(inst_summary))
    
    b1 = ax1.bar(x_inst - width/2, inst_summary['avg_payment_value'], width, color=PALETTE['accent'], label='Average Order Value (R$)')
    b2 = ax2.bar(x_inst + width/2, inst_summary['order_share_pct'], width, color=PALETTE['purple'], label='Credit Card Order Share (%)')
    
    ax1.set_title('Credit Card Installments: AOV Escalation & Volume Distribution', fontsize=13, fontweight='bold', pad=15)
    ax1.set_xlabel('Installment Tier', fontsize=11, fontweight='semibold')
    ax1.set_ylabel('Average Order Value (R$)', fontsize=11, fontweight='semibold', color=PALETTE['accent'])
    ax2.set_ylabel('Credit Card Order Share (%)', fontsize=11, fontweight='semibold', color=PALETTE['purple'])
    
    ax1.set_xticks(x_inst)
    ax1.set_xticklabels(inst_summary['installment_tier'], rotation=15, ha='right', fontsize=9.5, fontweight='semibold')
    ax1.grid(True, linestyle='--', alpha=0.3, axis='y')
    
    annotate_bars(ax1, format_str='R$ {:.0f}', fontsize=9, padding=2)
    annotate_bars(ax2, format_str='{:.1f}%', fontsize=9, padding=2)
    
    lines = [b1, b2]
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left', frameon=True, facecolor='white', edgecolor='#CBD5E1')
    
    plt.tight_layout()
    chart2_path = os.path.join(OUTPUT_CHARTS, 'q5_installments_vs_order_value.png')
    plt.savefig(chart2_path, dpi=300)
    plt.close()
    print(f"Saved chart to {chart2_path}")

    # Print summary to console
    print("\n=== Q5 PAYMENT METHOD SUMMARY ===")
    print(pay_dist[['primary_payment_type', 'order_count', 'order_share_pct', 'avg_payment_value', 'value_share_pct', 'avg_review_score', 'low_rating_rate_pct']])
    
    print("\n=== Q5 CREDIT CARD INSTALLMENTS SUMMARY ===")
    print(inst_summary[['installment_tier', 'order_count', 'order_share_pct', 'avg_payment_value', 'aov_multiplier_vs_single', 'avg_review_score', 'low_rating_rate_pct']])

if __name__ == '__main__':
    run_q5_analysis()
