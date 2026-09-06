"""
Reconciles 10 Filter Test Cases against master_orders.csv
Computes expected values for:
1. All States + All Categories
2. AC + All Categories
3. AC + baby
4. AC + health_beauty
5. SP + All Categories
6. SP + baby
7. All States + baby
8. SP + baby + Late
9. SP + health_beauty + Top 10% Seller
10. Deliberately empty combination (e.g. AC + non_existent_cat)
"""

import pandas as pd

df = pd.read_csv('outputs/exports/master_orders.csv')

# Determine top 10% sellers
seller_gmv = df.groupby('primary_seller_id')['total_price'].sum().sort_values(ascending=False)
top_10_pct_count = int(len(seller_gmv) * 0.10)
top_10_sellers = set(seller_gmv.iloc[:top_10_pct_count].index)

df['is_top10_seller'] = df['primary_seller_id'].isin(top_10_sellers)
df['is_slow_dispatch'] = df['carrier_dispatch_days'] > 5
df['is_low_rating'] = df['review_score'] <= 2
df['total_revenue'] = df['total_price'].fillna(0) + df['total_freight'].fillna(0)

test_cases = [
    ("1. All States + All Categories", {}),
    ("2. AC + All Categories", {'st': 'AC'}),
    ("3. AC + baby", {'st': 'AC', 'cat': 'baby'}),
    ("4. AC + health_beauty", {'st': 'AC', 'cat': 'health_beauty'}),
    ("5. SP + All Categories", {'st': 'SP'}),
    ("6. SP + baby", {'st': 'SP', 'cat': 'baby'}),
    ("7. All States + baby", {'cat': 'baby'}),
    ("8. SP + baby + Late", {'st': 'SP', 'cat': 'baby', 'stat': 'late'}),
    ("9. SP + health_beauty + Top 10% Seller", {'st': 'SP', 'cat': 'health_beauty', 't10': True}),
    ("10. Deliberately Empty (AC + non_existent)", {'st': 'AC', 'cat': 'non_existent_category'})
]

results = []

for name, filters in test_cases:
    sub = df.copy()
    if 'st' in filters:
        sub = sub[sub['customer_state'] == filters['st']]
    if 'cat' in filters:
        sub = sub[sub['category_english'] == filters['cat']]
    if 'stat' in filters:
        if filters['stat'] == 'delivered':
            sub = sub[sub['order_status'] == 'delivered']
        elif filters['stat'] == 'late':
            sub = sub[(sub['order_status'] == 'delivered') & (sub['is_late'] == 1)]
        elif filters['stat'] == 'undelivered':
            sub = sub[sub['order_status'] != 'delivered']
    if 't10' in filters:
        sub = sub[sub['is_top10_seller'] == filters['t10']]
    if 'slow' in filters:
        sub = sub[sub['is_slow_dispatch'] == filters['slow']]

    n_orders = len(sub)
    tot_rev = sub['total_revenue'].sum() if n_orders > 0 else 0.0
    avg_rev = sub['review_score'].mean() if n_orders > 0 else None
    
    low_cnt = sub['is_low_rating'].sum() if n_orders > 0 else 0
    low_pct = (sub['is_low_rating'].mean() * 100) if n_orders > 0 else None

    deliv_sub = sub[sub['order_status'] == 'delivered']
    n_deliv = len(deliv_sub)
    late_cnt = (deliv_sub['is_late'] == 1).sum() if n_deliv > 0 else 0
    late_pct = ((deliv_sub['is_late'] == 1).mean() * 100) if n_deliv > 0 else None

    results.append({
        'Case': name,
        'Orders': n_orders,
        'Revenue': round(tot_rev, 2),
        'AvgReview': round(avg_rev, 2) if avg_rev is not None else None,
        'LowCount': low_cnt,
        'LowRatePct': round(low_pct, 2) if low_pct is not None else None,
        'Delivered': n_deliv,
        'LateCount': late_cnt,
        'LateRatePct': round(late_pct, 2) if late_pct is not None else None
    })

res_df = pd.DataFrame(results)
print(res_df.to_string(index=False))

# Export ground truth reconciliation CSV
res_df.to_csv('outputs/tables/filter_reconciliation_ground_truth.csv', index=False)
