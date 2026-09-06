"""
Core Question 3 Analysis Module
Analyzes seller concentration (Pareto), customer state, seller state, and origin-destination route dynamics.
Enforces minimum sample-size thresholds (N >= 50) and isolates high-volume problem hotspots.
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

def run_q3_analysis():
    """Executes Core Question 3 Analysis."""
    os.makedirs(OUTPUT_TABLES, exist_ok=True)
    os.makedirs(OUTPUT_CHARTS, exist_ok=True)
    
    print("Ingesting master order dataset for Q3 Analysis...")
    df = pd.read_csv(MASTER_PATH)
    
    df['is_low_rating'] = (df['review_score'] <= 2).astype(int)
    total_orders = len(df)
    
    # 1. SELLER PARETO CONCENTRATION
    seller_perf = df.groupby('primary_seller_id').agg(
        order_count=('order_id', 'count'),
        total_gmv=('total_price', 'sum'),
        total_freight=('total_freight', 'sum'),
        seller_state=('seller_state', 'first'),
        avg_review_score=('review_score', 'mean'),
        late_rate_pct=('is_late', lambda x: (x == 1).mean() * 100),
        low_rating_rate_pct=('is_low_rating', lambda x: x.mean() * 100)
    ).reset_index().sort_values('total_gmv', ascending=False)
    
    total_active_sellers = len(seller_perf)
    overall_gmv = seller_perf['total_gmv'].sum()
    
    top_1_pct_count = int(np.ceil(total_active_sellers * 0.01))
    top_5_pct_count = int(np.ceil(total_active_sellers * 0.05))
    top_10_pct_count = int(np.ceil(total_active_sellers * 0.10))
    top_20_pct_count = int(np.ceil(total_active_sellers * 0.20))
    
    top_1_share = (seller_perf.iloc[:top_1_pct_count]['total_gmv'].sum() / overall_gmv) * 100
    top_5_share = (seller_perf.iloc[:top_5_pct_count]['total_gmv'].sum() / overall_gmv) * 100
    top_10_share = (seller_perf.iloc[:top_10_pct_count]['total_gmv'].sum() / overall_gmv) * 100
    top_20_share = (seller_perf.iloc[:top_20_pct_count]['total_gmv'].sum() / overall_gmv) * 100
    
    print(f"\n--- SELLER PARETO CONCENTRATION ($N = {total_active_sellers:,}$ Sellers) ---")
    print(f"Top 1% Sellers ({top_1_pct_count}): {top_1_share:.2f}% of total GMV")
    print(f"Top 5% Sellers ({top_5_pct_count}): {top_5_share:.2f}% of total GMV")
    print(f"Top 10% Sellers ({top_10_pct_count}): {top_10_share:.2f}% of total GMV")
    print(f"Top 20% Sellers ({top_20_pct_count}): {top_20_share:.2f}% of total GMV")

    # 2. CUSTOMER STATE PERFORMANCE
    cust_state_summary = df.groupby('customer_state').agg(
        order_count=('order_id', 'count'),
        total_gmv=('total_price', 'sum'),
        total_freight=('total_freight', 'sum'),
        avg_freight_rs=('total_freight', 'mean'),
        avg_lead_time_days=('delivery_lead_time_days', 'mean'),
        avg_estimated_lead_days=('estimated_lead_time_days', 'mean'),
        late_delivery_rate_pct=('is_late', lambda x: (x == 1).mean() * 100),
        avg_review_score=('review_score', 'mean'),
        low_rating_rate_pct=('is_low_rating', lambda x: x.mean() * 100)
    ).reset_index().sort_values('order_count', ascending=False)
    
    cust_state_summary['order_share_pct'] = (cust_state_summary['order_count'] / total_orders) * 100
    cust_state_summary['freight_ratio_pct'] = (cust_state_summary['total_freight'] / cust_state_summary['total_gmv']) * 100

    # 3. SELLER STATE PERFORMANCE
    seller_state_summary = df.groupby('seller_state').agg(
        seller_count=('primary_seller_id', 'nunique'),
        order_count=('order_id', 'count'),
        total_gmv=('total_price', 'sum'),
        total_freight=('total_freight', 'sum'),
        avg_freight_rs=('total_freight', 'mean'),
        avg_dispatch_days=('carrier_dispatch_days', 'mean'),
        late_delivery_rate_pct=('is_late', lambda x: (x == 1).mean() * 100),
        avg_review_score=('review_score', 'mean'),
        low_rating_rate_pct=('is_low_rating', lambda x: x.mean() * 100)
    ).reset_index().sort_values('order_count', ascending=False)

    # Save primary seller state performance table
    seller_state_path = os.path.join(OUTPUT_TABLES, 'q3_seller_geo.csv')
    seller_state_summary.to_csv(seller_state_path, index=False)
    print(f"Saved Q3 seller state performance table to {seller_state_path}")

    # 4. ORIGIN-DESTINATION ROUTE ANALYSIS (Seller State -> Customer State)
    df_valid_route = df.dropna(subset=['seller_state', 'customer_state']).copy()
    df_valid_route['route_code'] = df_valid_route['seller_state'] + ' -> ' + df_valid_route['customer_state']
    
    route_summary = df_valid_route.groupby('route_code').agg(
        seller_state=('seller_state', 'first'),
        customer_state=('customer_state', 'first'),
        order_count=('order_id', 'count'),
        total_gmv=('total_price', 'sum'),
        avg_freight_rs=('total_freight', 'mean'),
        avg_lead_time_days=('delivery_lead_time_days', 'mean'),
        late_delivery_rate_pct=('is_late', lambda x: (x == 1).mean() * 100),
        avg_review_score=('review_score', 'mean'),
        low_rating_rate_pct=('is_low_rating', lambda x: x.mean() * 100)
    ).reset_index()
    
    # Enforce minimum sample-size threshold N >= 50 orders
    route_filtered = route_summary[route_summary['order_count'] >= 50].sort_values('order_count', ascending=False)
    route_filtered.to_csv(os.path.join(OUTPUT_TABLES, 'q3_route_performance.csv'), index=False)

    # 5. HIGH-VOLUME PROBLEM HOTSPOTS IDENTIFICATION (N >= 100, Late Rate > 10% OR Low Rating Rate > 18%)
    hotspots = route_summary[
        (route_summary['order_count'] >= 100) & 
        ((route_summary['late_delivery_rate_pct'] >= 10.0) | (route_summary['low_rating_rate_pct'] >= 18.0))
    ].sort_values('late_delivery_rate_pct', ascending=False)
    
    hotspots_path = os.path.join(OUTPUT_TABLES, 'q3_hotspots.csv')
    hotspots.to_csv(hotspots_path, index=False)
    print(f"Saved Q3 high-volume problem hotspots to {hotspots_path}")
    print(f"Identified {len(hotspots)} high-volume problem routes (N >= 100)!")

    # Visualizations
    # Chart 1: q3_seller_pareto_curve.png
    fig, ax = plt.subplots(figsize=(10, 5.5))
    
    seller_perf['cum_gmv'] = seller_perf['total_gmv'].cumsum()
    seller_perf['cum_gmv_pct'] = (seller_perf['cum_gmv'] / overall_gmv) * 100
    seller_perf['seller_rank_pct'] = (np.arange(1, total_active_sellers + 1) / total_active_sellers) * 100
    
    ax.plot(seller_perf['seller_rank_pct'], seller_perf['cum_gmv_pct'], color=PALETTE['primary'], linewidth=2.5, label='Cumulative GMV Share')
    ax.plot([0, 100], [0, 100], color=PALETTE['gray'], linestyle='--', label='Equal Distribution Baseline')
    
    ax.scatter([10], [top_10_share], color=PALETTE['danger'], s=80, zorder=5)
    ax.annotate(f'Top 10% Sellers = {top_10_share:.1f}% GMV\n({top_10_pct_count} sellers)', 
                xy=(10, top_10_share), xytext=(22, top_10_share - 12),
                arrowprops=dict(facecolor=PALETTE['danger'], shrink=0.08, width=1.5, headwidth=6),
                fontsize=9.5, fontweight='bold', color=PALETTE['dark_navy'])
    
    set_chart_style(ax, title='Seller Revenue Pareto Curve (Top 10% Sellers = 67.5% GMV)',
                    xlabel='Percentage of Active Sellers (%)', ylabel='Cumulative GMV Share (%)')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 105)
    ax.legend(loc='lower right', frameon=True, facecolor='white', edgecolor='#CBD5E1')
    save_chart(fig, 'q3_seller_pareto_curve.png', OUTPUT_CHARTS)

    # Chart 2: q3_state_freight_and_late_rate.png
    fig, ax1 = plt.subplots(figsize=(12, 5.5))
    ax2 = ax1.twinx()
    
    top12_states = cust_state_summary.head(12)
    x_s = np.arange(len(top12_states))
    width = 0.35
    
    b1 = ax1.bar(x_s - width/2, top12_states['avg_freight_rs'], width, color=PALETTE['secondary'], label='Avg Freight Value (R$)')
    b2 = ax2.bar(x_s + width/2, top12_states['late_delivery_rate_pct'], width, color=PALETTE['danger'], label='Late Delivery Rate (%)')
    
    set_chart_style(ax1, title='Top 12 Customer States: Average Freight Value (R$) vs. Late Delivery Rate (%)',
                    xlabel='Customer State', ylabel='Average Freight Value (R$)')
    ax2.set_ylabel('Late Delivery Rate (%)', fontsize=11, fontweight='semibold', color=PALETTE['danger'])
    ax1.set_xticks(x_s)
    ax1.set_xticklabels(top12_states['customer_state'])
    ax2.set_ylim(0, 30)
    
    annotate_bars(ax1, format_str='R$ {:.1f}', fontsize=8.5, padding=0.5)
    annotate_bars(ax2, format_str='{:.1f}%', fontsize=8.5, padding=0.8)
    
    lines = [b1, b2]
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left', frameon=True, facecolor='white', edgecolor='#CBD5E1')
    save_chart(fig, 'q3_state_freight_and_late_rate.png', OUTPUT_CHARTS)

    # Chart 3: q3_route_hotspots_chart.png
    fig, ax = plt.subplots(figsize=(11, 5.5))
    top_hotspots = hotspots.head(8)
    
    x_h = np.arange(len(top_hotspots))
    
    b1 = ax.bar(x_h - width/2, top_hotspots['late_delivery_rate_pct'], width, color=PALETTE['danger'], label='Late Delivery Rate (%)')
    b2 = ax.bar(x_h + width/2, top_hotspots['low_rating_rate_pct'], width, color=PALETTE['accent'], label='Low-Rating Rate (%)')
    
    set_chart_style(ax, title='Top High-Volume Logistics Problem Hotspots (N >= 100 Orders)',
                    xlabel='Origin -> Destination Route', ylabel='Percentage (%)')
    ax.set_xticks(x_h)
    ax.set_xticklabels(top_hotspots['route_code'], rotation=25, ha='right')
    ax.set_ylim(0, 45)
    
    annotate_bars(ax, format_str='{:.1f}%', fontsize=8.5, padding=0.8)
    ax.legend(loc='upper left', frameon=True, facecolor='white', edgecolor='#CBD5E1')
    save_chart(fig, 'q3_route_hotspots_chart.png', OUTPUT_CHARTS)

    return seller_perf, cust_state_summary, hotspots

if __name__ == '__main__':
    run_q3_analysis()
