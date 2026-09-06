# Frontend Bugfix QA Document

**Platform**: Olist Executive Analytics Platform  
**Module**: Web Application Engine (`app/js/app.js`, `app/js/data.js`, Analytical Data Pipelines)  
**Date**: 2026-09-06  

---

## 1. Bug Description

Runtime crashes occurred in the browser console when navigating to the **Delivery** or **Sellers** tabs or when interacting with global filter dropdowns (State, Category, Delivery Status, Seller Segment):

1. `Uncaught TypeError: Cannot read properties of undefined (reading 'toLocaleString') at app.js:633` (in `renderSellers`)
2. `Uncaught TypeError: Cannot read properties of undefined (reading 'toLocaleString') at app.js:427` (in `renderDelivery`)

The errors resulted in broken tables, missing metrics, or uncaught exceptions during user interactions.

---

## 2. Root Cause Analysis

A thorough audit revealed four underlying data-contract mismatches between the analytical data generation layer and the frontend application engine:

1. **Sellers View Data-Contract Mismatch (`q3_seller_geo.csv`)**:
   - `renderSellers()` expected `seller_state` and `seller_count` on `data.q3_seller_geo`.
   - The pipeline script `src/q3_analysis.py` (and `src/analysis/q3_seller_geographic.py`) mistakenly exported customer state aggregations (`cust_state_summary`) into `q3_seller_geo.csv` instead of seller state aggregations (`seller_state_summary`).
   - Consequently, `r.seller_count` and `r.seller_state` were `undefined`, causing `r.seller_count.toLocaleString()` to crash with a `TypeError`.

2. **Delivery View Schema Incompleteness (`q2_state_delivery`)**:
   - `renderDelivery()` expected state-level totals (`total_orders`, `delivered_orders`, `late_rate_pct`, `avg_lead_time_days`, `avg_review_score`, `low_rating_rate_pct`).
   - The underlying table `q2_state_delivery_interaction.csv` contained only pivot metrics (`cnt_ontime`, `cnt_late`, `score_ontime`, `score_late`), missing overall state totals and lead time averages.

3. **Reactive State Filter KPI Failure (`updateKPIs()`)**:
   - Selecting a state in the filter bar caused `updateKPIs()` to look for `total_orders` and `total_revenue` on `eda_state_summary`.
   - The actual fields in `eda_state_summary` were `order_count` and `total_gmv`, making `orders` and `revenue` evaluate to `undefined` and causing `orders.toLocaleString()` to crash on filter change.

4. **Overview & Delivery Delay Bucket Schema Mismatches**:
   - `renderOverview()` called `monthly.map(r => r.order_count)`, whereas the column name in `q1_monthly_performance.csv` is `orders`.
   - `renderDelivery()` read `data.q2_delay_buckets` (which has `pct_1_star`) instead of `data.q2_delivery` (which has `low_rating_rate_pct`).

---

## 3. Files Changed

1. **`src/q2_analysis.py`**
   - Enriched `q2_state_delivery_interaction.csv` to export state-level total metrics (`total_orders`, `delivered_orders`, `late_rate_pct`, `avg_lead_time_days`, `avg_review_score`, `low_rating_rate_pct`) alongside on-time/late pivot counts.

2. **`src/analysis/q2_delivery_performance.py`**
   - Added state-level combined delivery performance aggregation and exported to `q2_state_delivery_interaction.csv`.

3. **`src/q3_analysis.py`**
   - Corrected `q3_seller_geo.csv` export to save `seller_state_summary` (containing `seller_state`, `seller_count`, `order_count`, `total_gmv`, `avg_freight_rs`, `avg_review_score`, `low_rating_rate_pct`).

4. **`src/analysis/q3_seller_geographic.py`**
   - Added `seller_state_summary` aggregation and exported to `q3_seller_geo.csv`.

5. **`run_analysis.py`**
   - Fixed module imports and executed pipeline runner to update all CSV files in `outputs/tables/`.

6. **`scratch/build_dashboard_data.py`**
   - Executed script to compile updated CSV outputs into `app/js/data.js`.

7. **`app/js/app.js`**
   - Added reusable formatting helpers (`formatNumber`, `formatCurrency`, `formatPercent`, `formatScore`) that perform strict type/numeric checks before formatting.
   - Updated `updateKPIs()` to use safe fallback lookups across `order_count`/`total_orders` and `total_gmv`/`total_revenue`.
   - Fixed `renderOverview()` to use `r.orders ?? r.order_count`.
   - Fixed `renderDelivery()` to use `data.q2_delivery` for delay bucket charts and updated schema fields for `tbodyDeliveryState`.
   - Fixed `renderSellers()` to map `r.seller_state`, `r.seller_count`, `r.total_gmv`, `r.avg_freight_rs`, `r.avg_review_score`, `r.low_rating_rate_pct`.
   - Preserved empty state rendering (`renderEmptyTable`) whenever filters produce zero matching records.

8. **`scratch/test_dashboard_engine.js`**
   - Created automated node regression test suite validating tab navigation, filter updates, and zero-record handling.

---

## 4. Fix Details

- **Data Contract Source-of-Truth**: Upstream analytical Python scripts generate all required fields (`seller_state`, `seller_count`, `delivered_orders`, `avg_lead_time_days`, etc.) directly from the master order dataset without altering underlying calculations.
- **Safe Number Formatting**: Implemented `formatNumber()`, `formatCurrency()`, `formatPercent()`, `formatScore()` in `app/js/app.js` to ensure `.toLocaleString()` and `.toFixed()` are only invoked on valid numeric values (`typeof val === 'number' && !isNaN(val)`). Missing values render as clean dash placeholders (`'-'`) rather than fake zeroes.

---

## 5. Tests Performed

1. **Pipeline Execution**: Ran `python run_analysis.py` — verified 6/6 pipeline automated validation checks passed.
2. **Data Bundle Build**: Ran `python scratch/build_dashboard_data.py` — confirmed `app/js/data.js` rebuilt cleanly.
3. **Automated JS Engine Suite (`scratch/test_dashboard_engine.js`)**: Executed 33 test cases covering:
   - Navigation across all 8 dashboard tabs.
   - State filter changes (`ALL`, `SP`, `RJ`, `MG`, `RS`, `PR`, `BA`, `DF`, `RR`).
   - Category filter changes (`ALL`, `health_beauty`, `bed_bath_table`, `sports_leisure`, `computers_accessories`).
   - Delivery status filter changes (`ALL`, `delivered`, `late`, `undelivered`).
   - Seller segment filter changes (`ALL`, `top10`, `slow`).
   - Multi-filter combinations across tabs.
   - Filter reset and zero-record empty states.

---

## 6. Test Result

- **Total Tests Executed**: 33
- **Passed**: 33
- **Failed**: 0
- **Uncaught Console Errors**: **0 (Zero)**

All displayed metrics match the validated underlying analytical outputs.
