"""
Question 3: Seller and Geographic Patterns
Analyzes seller concentration (Pareto principle), buyer vs seller geographic distributions,
intra-state vs inter-state shipping, regional freight cost disparities, and lead times.
Enforces Data Integrity Rule 14 (sample-size threshold N >= 50).
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

# Brazilian Macro-Region Mapping
STATE_TO_REGION = {
    'SP': 'Southeast', 'RJ': 'Southeast', 'MG': 'Southeast', 'ES': 'Southeast',
    'PR': 'South', 'SC': 'South', 'RS': 'South',
    'BA': 'Northeast', 'PE': 'Northeast', 'CE': 'Northeast', 'MA': 'Northeast', 
    'PB': 'Northeast', 'RN': 'Northeast', 'AL': 'Northeast', 'SE': 'Northeast', 'PI': 'Northeast',
    'GO': 'Center-West', 'MT': 'Center-West', 'MS': 'Center-West', 'DF': 'Center-West',
    'AM': 'North', 'PA': 'North', 'RO': 'North', 'AP': 'North', 'AC': 'North', 'RR': 'North', 'TO': 'North'
}

def analyze_seller_geographic_patterns(df):
    """Executes Question 3 analysis."""
    print("--- Running Q3: Seller & Geographic Patterns ---")
    
    # 1. SELLER CONCENTRATION ANALYSIS (Pareto)
    seller_perf = df.groupby('primary_seller_id').agg(
        order_count=('order_id', 'count'),
        total_gmv=('total_price', 'sum'),
        total_freight=('total_freight', 'sum'),
        seller_state=('seller_state', 'first'),
        avg_review_score=('review_score', 'mean')
    ).reset_index().sort_values('total_gmv', ascending=False)
    
    total_active_sellers = len(seller_perf)
    overall_gmv = seller_perf['total_gmv'].sum()
    
    seller_perf['cum_gmv'] = seller_perf['total_gmv'].cumsum()
    seller_perf['cum_gmv_pct'] = (seller_perf['cum_gmv'] / overall_gmv) * 100
    seller_perf['seller_rank'] = np.arange(1, total_active_sellers + 1)
    seller_perf['seller_rank_pct'] = (seller_perf['seller_rank'] / total_active_sellers) * 100
    
    top_1_pct_count = int(np.ceil(total_active_sellers * 0.01))
    top_5_pct_count = int(np.ceil(total_active_sellers * 0.05))
    top_10_pct_count = int(np.ceil(total_active_sellers * 0.10))
    top_20_pct_count = int(np.ceil(total_active_sellers * 0.20))
    
    top_1_gmv_share = (seller_perf.iloc[:top_1_pct_count]['total_gmv'].sum() / overall_gmv) * 100
    top_5_gmv_share = (seller_perf.iloc[:top_5_pct_count]['total_gmv'].sum() / overall_gmv) * 100
    top_10_gmv_share = (seller_perf.iloc[:top_10_pct_count]['total_gmv'].sum() / overall_gmv) * 100
    top_20_gmv_share = (seller_perf.iloc[:top_20_pct_count]['total_gmv'].sum() / overall_gmv) * 100
    
    print(f"Total Active Sellers: {total_active_sellers:,}")
    print(f"Top 1% Sellers ({top_1_pct_count}): {top_1_gmv_share:.2f}% of GMV")
    print(f"Top 5% Sellers ({top_5_pct_count}): {top_5_gmv_share:.2f}% of GMV")
    print(f"Top 10% Sellers ({top_10_pct_count}): {top_10_gmv_share:.2f}% of GMV")
    print(f"Top 20% Sellers ({top_20_pct_count}): {top_20_gmv_share:.2f}% of GMV")
    
    pareto_df = pd.DataFrame({
        'seller_tier': ['Top 1%', 'Top 5%', 'Top 10%', 'Top 20%', 'Bottom 80%'],
        'seller_count': [top_1_pct_count, top_5_pct_count, top_10_pct_count, top_20_pct_count, total_active_sellers - top_20_pct_count],
        'gmv_share_pct': [
            round(top_1_gmv_share, 2),
            round(top_5_gmv_share, 2),
            round(top_10_gmv_share, 2),
            round(top_20_gmv_share, 2),
            round(100 - top_20_gmv_share, 2)
        ]
    })
    pareto_path = os.path.join(OUTPUT_TABLES, 'q3_seller_concentration_pareto.csv')
    pareto_df.to_csv(pareto_path, index=False)
    
    # 2. INTER-STATE VS INTRA-STATE SHIPPING
    df_valid_geo = df.dropna(subset=['customer_state', 'seller_state']).copy()
    total_geo_orders = len(df_valid_geo)
    
    intrastate = df_valid_geo[df_valid_geo['is_interstate'] == 0]
    interstate = df_valid_geo[df_valid_geo['is_interstate'] == 1]
    
    intra_count = len(intrastate)
    inter_count = len(interstate)
    intra_share = (intra_count / total_geo_orders) * 100
    inter_share = (inter_count / total_geo_orders) * 100
    
    intra_avg_freight = intrastate['total_freight'].mean()
    inter_avg_freight = interstate['total_freight'].mean()
    
    intra_avg_price = intrastate['total_price'].mean()
    inter_avg_price = interstate['total_price'].mean()
    
    # Delivered orders only for lead time
    intra_deliv = intrastate[intrastate['order_status'] == 'delivered']
    inter_deliv = interstate[interstate['order_status'] == 'delivered']
    
    intra_lead_time = intra_deliv['delivery_lead_time_days'].mean()
    inter_lead_time = inter_deliv['delivery_lead_time_days'].mean()
    
    intra_late_rate = intra_deliv['is_late'].mean() * 100
    inter_late_rate = inter_deliv['is_late'].mean() * 100
    
    print(f"\nIntra-State Shipping: {intra_share:.2f}% ({intra_count:,} orders), Avg Freight: R$ {intra_avg_freight:.2f}, Lead Time: {intra_lead_time:.2f}d, Late Rate: {intra_late_rate:.2f}%")
    print(f"Inter-State Shipping: {inter_share:.2f}% ({inter_count:,} orders), Avg Freight: R$ {inter_avg_freight:.2f}, Lead Time: {inter_lead_time:.2f}d, Late Rate: {inter_late_rate:.2f}%")
    
    geo_flow_df = pd.DataFrame({
        'shipping_type': ['Intra-State (Same State)', 'Inter-State (Cross State)'],
        'order_count': [intra_count, inter_count],
        'order_share_pct': [round(intra_share, 2), round(inter_share, 2)],
        'avg_price_rs': [round(intra_avg_price, 2), round(inter_avg_price, 2)],
        'avg_freight_rs': [round(intra_avg_freight, 2), round(inter_avg_freight, 2)],
        'avg_freight_ratio_pct': [round((intra_avg_freight / intra_avg_price) * 100, 2), round((inter_avg_freight / inter_avg_price) * 100, 2)],
        'avg_lead_time_days': [round(intra_lead_time, 2), round(inter_lead_time, 2)],
        'late_delivery_rate_pct': [round(intra_late_rate, 2), round(inter_late_rate, 2)]
    })
    geo_flow_path = os.path.join(OUTPUT_TABLES, 'q3_interstate_vs_intrastate_metrics.csv')
    geo_flow_df.to_csv(geo_flow_path, index=False)
    
    # 3. REGIONAL ANALYSIS (Customer Macro-Regions)
    df_valid_geo['customer_region'] = df_valid_geo['customer_state'].map(STATE_TO_REGION)
    delivered_geo = df_valid_geo[df_valid_geo['order_status'] == 'delivered'].copy()
    
    regional_summary = delivered_geo.groupby('customer_region').agg(
        order_count=('order_id', 'count'),
        total_gmv=('total_price', 'sum'),
        avg_order_price=('total_price', 'mean'),
        avg_freight_value=('total_freight', 'mean'),
        avg_freight_ratio=('freight_ratio', lambda x: x.mean() * 100),
        avg_lead_time_days=('delivery_lead_time_days', 'mean'),
        median_lead_time_days=('delivery_lead_time_days', 'median'),
        late_delivery_rate_pct=('is_late', lambda x: x.mean() * 100),
        avg_review_score=('review_score', 'mean')
    ).reset_index().sort_values('order_count', ascending=False)
    
    regional_summary['order_share_pct'] = (regional_summary['order_count'] / len(delivered_geo)) * 100
    
    # Apply Data Integrity Rule 14 check (N >= 50)
    regional_summary = regional_summary[regional_summary['order_count'] >= 50].copy()
    
    regional_path = os.path.join(OUTPUT_TABLES, 'q3_regional_performance_summary.csv')
    regional_summary.to_csv(regional_path, index=False)
    print(f"Saved regional performance table to {regional_path}")

    # Seller State Performance Summary Table
    df['is_low_rating'] = (df['review_score'] <= 2).astype(int)
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

    seller_state_path = os.path.join(OUTPUT_TABLES, 'q3_seller_geo.csv')
    seller_state_summary.to_csv(seller_state_path, index=False)
    print(f"Saved seller state performance table to {seller_state_path}")

    # Visualizations
    # Chart 1: Seller Pareto Concentration Curve
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(seller_perf['seller_rank_pct'], seller_perf['cum_gmv_pct'], 
            color=PALETTE['primary'], linewidth=2.5, label='Cumulative GMV Share')
    ax.plot([0, 100], [0, 100], color=PALETTE['gray'], linestyle='--', label='Perfect Equality Baseline')
    
    # Annotate Top 10% point
    ax.scatter([10], [top_10_gmv_share], color=PALETTE['danger'], s=80, zorder=5)
    ax.annotate(f'Top 10% Sellers = {top_10_gmv_share:.1f}% GMV', 
                xy=(10, top_10_gmv_share), xytext=(20, top_10_gmv_share - 10),
                arrowprops=dict(facecolor=PALETTE['danger'], shrink=0.08, width=1.5, headwidth=6),
                fontsize=10, fontweight='bold', color=PALETTE['dark_navy'])
    
    set_chart_style(ax, title='Seller Revenue Concentration: Lorenz/Pareto Curve',
                    xlabel='Percentage of Active Sellers (%)', ylabel='Cumulative GMV Share (%)')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 105)
    ax.legend(loc='lower right', frameon=True, facecolor='white', edgecolor='#CBD5E1')
    save_chart(fig, 'q3_seller_pareto_concentration.png', OUTPUT_CHARTS)

    # Chart 2: Regional Freight Ratio & Delivery Lead Time Comparison
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax2 = ax1.twinx()
    
    x = np.arange(len(regional_summary))
    width = 0.35
    
    b1 = ax1.bar(x - width/2, regional_summary['avg_freight_value'], width, color=PALETTE['secondary'], label='Avg Freight Value (R$)')
    b2 = ax2.bar(x + width/2, regional_summary['avg_lead_time_days'], width, color=PALETTE['accent'], label='Avg Delivery Lead Time (Days)')
    
    set_chart_style(ax1, title='Regional Freight Costs & Delivery Speed Across Brazil',
                    xlabel='Customer Macro-Region', ylabel='Average Freight Value (R$)')
    ax2.set_ylabel('Average Lead Time (Days)', fontsize=11, fontweight='semibold', color=PALETTE['accent'])
    ax1.set_xticks(x)
    ax1.set_xticklabels(regional_summary['customer_region'])
    
    annotate_bars(ax1, format_str='R$ {:.1f}', fontsize=9, padding=0.5)
    annotate_bars(ax2, format_str='{:.1f}d', fontsize=9, padding=0.3)
    
    lines = [b1, b2]
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left', frameon=True, facecolor='white', edgecolor='#CBD5E1')
    
    save_chart(fig, 'q3_regional_freight_and_leadtime.png', OUTPUT_CHARTS)
    
    return pareto_df, geo_flow_df, regional_summary

if __name__ == '__main__':
    master_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'outputs', 'master_analytical_dataset.csv')
    df = pd.read_csv(master_path)
    analyze_seller_geographic_patterns(df)
