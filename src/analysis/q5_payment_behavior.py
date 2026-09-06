"""
Question 5: Payment Behavior Analysis
Analyzes payment method distribution (credit card, boleto, voucher, debit card),
installment tier patterns vs order value and satisfaction, and multi-payment sequential usage.
Adheres strictly to Data Integrity Rule 7 (order-level payment aggregation).
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

def analyze_payment_behavior(df):
    """Executes Question 5 analysis."""
    print("--- Running Q5: Payment Behavior Analysis ---")
    
    df_valid_pay = df[df['primary_payment_type'].notnull()].copy()
    total_pay_orders = len(df_valid_pay)
    
    # 1. PAYMENT METHOD DISTRIBUTION
    pay_dist = df_valid_pay.groupby('primary_payment_type').agg(
        order_count=('order_id', 'count'),
        total_payment_value=('total_payment_value', 'sum'),
        avg_order_payment=('total_payment_value', 'mean'),
        median_order_payment=('total_payment_value', 'median'),
        avg_review_score=('review_score', 'mean')
    ).reset_index().sort_values('order_count', ascending=False)
    
    pay_dist['order_share_pct'] = (pay_dist['order_count'] / total_pay_orders) * 100
    pay_dist['value_share_pct'] = (pay_dist['total_payment_value'] / df_valid_pay['total_payment_value'].sum()) * 100
    
    pay_dist_path = os.path.join(OUTPUT_TABLES, 'q5_payment_method_distribution.csv')
    pay_dist.to_csv(pay_dist_path, index=False)
    print(f"Saved payment method distribution table to {pay_dist_path}")
    
    print("\n--- PAYMENT METHOD BREAKDOWN ---")
    for _, r in pay_dist.iterrows():
        print(f"{r['primary_payment_type'].upper()}: Orders {r['order_count']:,} ({r['order_share_pct']:.2f}%), Value R$ {r['total_payment_value']:,.2f} ({r['value_share_pct']:.2f}%), AOV R$ {r['avg_order_payment']:.2f}")

    # 2. CREDIT CARD INSTALLMENT ANALYSIS
    cc_orders = df_valid_pay[df_valid_pay['primary_payment_type'] == 'credit_card'].copy()
    total_cc = len(cc_orders)
    
    def get_installment_tier(inst):
        if inst == 1: return '1. 1 Installment (Full Pay)'
        elif inst <= 3: return '2. 2 - 3 Installments'
        elif inst <= 6: return '3. 4 - 6 Installments'
        elif inst <= 10: return '4. 7 - 10 Installments'
        else: return '5. 11+ Installments'

    cc_orders['installment_tier'] = cc_orders['max_installments'].apply(get_installment_tier)
    
    inst_summary = cc_orders.groupby('installment_tier').agg(
        order_count=('order_id', 'count'),
        total_payment_value=('total_payment_value', 'sum'),
        avg_payment_value=('total_payment_value', 'mean'),
        median_payment_value=('total_payment_value', 'median'),
        avg_review_score=('review_score', 'mean')
    ).reset_index()
    
    inst_summary['order_share_pct'] = (inst_summary['order_count'] / total_cc) * 100
    
    inst_path = os.path.join(OUTPUT_TABLES, 'q5_credit_card_installments_analysis.csv')
    inst_summary.to_csv(inst_path, index=False)
    print(f"Saved credit card installments analysis table to {inst_path}")

    # 3. SEQUENTIAL MULTI-PAYMENT USAGE PATTERNS
    multi_pay_summary = df_valid_pay.groupby('payment_methods_distinct').agg(
        order_count=('order_id', 'count'),
        total_payment_value=('total_payment_value', 'sum'),
        avg_payment_value=('total_payment_value', 'mean')
    ).reset_index()
    multi_pay_summary['order_share_pct'] = (multi_pay_summary['order_count'] / total_pay_orders) * 100
    
    multi_seq_summary = df_valid_pay.groupby('payment_sequential_count').agg(
        order_count=('order_id', 'count'),
        total_payment_value=('total_payment_value', 'sum')
    ).reset_index()
    multi_seq_summary['order_share_pct'] = (multi_seq_summary['order_count'] / total_pay_orders) * 100
    
    seq_path = os.path.join(OUTPUT_TABLES, 'q5_payment_sequential_summary.csv')
    multi_seq_summary.to_csv(seq_path, index=False)

    # Visualizations
    # Chart 1: Primary Payment Method Share & AOV Comparison
    fig, ax1 = plt.subplots(figsize=(10, 5.5))
    ax2 = ax1.twinx()
    
    x = np.arange(len(pay_dist))
    width = 0.35
    
    b1 = ax1.bar(x - width/2, pay_dist['order_share_pct'], width, color=PALETTE['primary'], label='Order Share (%)')
    b2 = ax2.bar(x + width/2, pay_dist['avg_order_payment'], width, color=PALETTE['secondary'], label='Average Order Value (R$)')
    
    set_chart_style(ax1, title='Payment Method Share (%) and Average Order Value (AOV)',
                    xlabel='Primary Payment Method', ylabel='Order Volume Share (%)')
    ax2.set_ylabel('Average Order Value (R$)', fontsize=11, fontweight='semibold', color=PALETTE['secondary'])
    ax1.set_xticks(x)
    ax1.set_xticklabels([t.replace('_', ' ').title() for t in pay_dist['primary_payment_type']])
    
    annotate_bars(ax1, format_str='{:.1f}%', fontsize=9, padding=0.5)
    annotate_bars(ax2, format_str='R$ {:.0f}', fontsize=9, padding=1.0)
    
    lines = [b1, b2]
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper right', frameon=True, facecolor='white', edgecolor='#CBD5E1')
    
    save_chart(fig, 'q5_payment_method_shares.png', OUTPUT_CHARTS)

    # Chart 2: Credit Card Installment Tier vs Order Value (AOV)
    fig, ax1 = plt.subplots(figsize=(10, 5.5))
    ax2 = ax1.twinx()
    
    x_inst = np.arange(len(inst_summary))
    
    b1 = ax1.bar(x_inst - width/2, inst_summary['avg_payment_value'], width, color=PALETTE['accent'], label='Average Order Value (R$)')
    b2 = ax2.bar(x_inst + width/2, inst_summary['order_share_pct'], width, color=PALETTE['purple'], label='Credit Card Order Share (%)')
    
    set_chart_style(ax1, title='Credit Card Installments: Order Value Scaling with Installment Count',
                    xlabel='Installment Tier', ylabel='Average Order Value (R$)')
    ax2.set_ylabel('Order Share (%)', fontsize=11, fontweight='semibold', color=PALETTE['purple'])
    ax1.set_xticks(x_inst)
    ax1.set_xticklabels(inst_summary['installment_tier'], rotation=20, ha='right')
    
    annotate_bars(ax1, format_str='R$ {:.0f}', fontsize=9, padding=2.0)
    annotate_bars(ax2, format_str='{:.1f}%', fontsize=9, padding=0.5)
    
    lines = [b1, b2]
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left', frameon=True, facecolor='white', edgecolor='#CBD5E1')
    
    save_chart(fig, 'q5_installments_vs_order_value.png', OUTPUT_CHARTS)
    
    return pay_dist, inst_summary

if __name__ == '__main__':
    master_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'outputs', 'master_analytical_dataset.csv')
    df = pd.read_csv(master_path)
    analyze_payment_behavior(df)
