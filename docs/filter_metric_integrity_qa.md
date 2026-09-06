# Filter & Metric Integrity QA Report

**Platform**: Olist Executive Analytics Platform  
**Module**: Unified Canonical Interactive Filtering Architecture  
**Date**: 2026-09-06  

---

## 1. Root Cause Analysis

A critical metric consistency issue was identified in the web dashboard filtering engine:
- **Anomalous Behavior Observed**: Selecting `State = AC` and `Category = baby` displayed `Total Orders = 3`, but `Total Revenue = R$ 479.8K`.
- **Root Cause**: `app/js/app.js` previously attempted to synthesize multi-filter metrics by combining separate pre-aggregated summary tables (`eda_state_summary` and `q4_category_analysis`). Selecting `Category = baby` retrieved `match.revenue` from `q4_categories` (which represents the platform-wide category total of R$ 479.8K across all 27 states) and completely ignored the active `State = AC` filter.
- **Architectural Solution**: The filtering architecture was overhauled to embed a compact, canonical order-level dataset (`data.orders_spine`, 99,441 records at `order_id` grain) into `app/js/data.js`. The JS engine filters `orders_spine` in real time (~2ms execution), ensuring that **all 5 top-level KPIs, subtitles, view tables, and charts derive their metrics from the exact same filtered order subset**.

---

## 2. Files Changed

1. **`scratch/build_dashboard_data.py`**
   - Ingested `outputs/exports/master_orders.csv` to build compact `orders_spine` array with fields: `st` (customer state), `sst` (seller state), `cat` (category), `stat` (order status), `late` (is_late flag), `slow` (slow dispatch flag), `t10` (top 10% seller flag), `rev` (total revenue), `score` (review score), `low` (is_low_rating flag).
   - Compiled `data.orders_spine` into `app/js/data.js`.

2. **`app/js/app.js`**
   - Implemented `getFilteredOrders()` to evaluate global filter state (`filterState`, `filterCategory`, `filterStatus`, `filterSeller`) dynamically against `data.orders_spine`.
   - Re-architected `updateKPIs()` to calculate Total Orders, Total Revenue, Average Review, Low Rating Rate, and Late Delivery Rate strictly from `filteredOrders`.
   - Updated KPI card subtitles dynamically to reflect filtered counts (`"[N] low-rated orders"`, `"[N] late delivered orders"`).
   - Updated view table renderers (`renderDelivery`, `renderSellers`, `renderCategories`) to aggregate state/category tables directly from `getFilteredOrders()`.

3. **`scratch/test_filter_reconciliation.py`**
   - Created Python script to compute independent ground-truth analytical metrics directly from `master_orders.csv` across 10 filter test scenarios.

4. **`scratch/test_dashboard_engine.js`**
   - Created automated JavaScript test suite verifying JS engine calculations against Python ground-truth metrics.

5. **`docs/filter_metric_integrity_qa.md`**
   - Generated complete QA report documenting calculations, test cases, and pass results.

---

## 3. KPI Calculations Audited

| KPI Card | Formula / Calculation | Denominator | Subtitle Behavior |
|---|---|---|---|
| **Total Orders** | `filteredOrders.length` | Total matching orders | `Filtered Subset (N = [N])` or platform grain |
| **Total Revenue** | `sum(r.rev)` across `filteredOrders` | Sum of total_price + total_freight | `Filtered Revenue Subset` or platform total |
| **Average Review** | `mean(r.score)` for `r.score >= 1` | Orders with valid review score | `Filtered Avg Score (N = [N])` |
| **Low Rating Rate** | `count(r.low == 1) / count(valid review) * 100` | Orders with valid review score | `[FILTERED_LOW_COUNT] low-rated orders` |
| **Late Delivery Rate** | `count(delivered && late==1) / count(delivered) * 100` | Delivered orders (`r.stat == 'delivered'`) | `[FILTERED_LATE_COUNT] late delivered orders` |

---

## 4. Reconciliation Test Results (10 Test Cases)

| Test Case | Filter Criteria | Metric | Expected Ground Truth | Dashboard Actual | Status |
|---|---|---|---|---|---|
| **1. All Baseline** | All States + All Categories | Orders<br>Revenue<br>Avg Review<br>Low Rating<br>Late Delivery | 99,441<br>R$ 15.84M<br>4.07 / 5.0<br>15.09% (15,010)<br>8.11% (7,826) | 99,441<br>R$ 15.84M<br>4.07 / 5.0<br>15.09% (15,010)<br>8.11% (7,826) | **PASS** |
| **2. AC State** | AC + All Categories | Orders<br>Revenue<br>Avg Review<br>Low Rating<br>Late Delivery | 81<br>R$ 19.67K<br>4.05 / 5.0<br>16.05% (13)<br>3.75% (3) | 81<br>R$ 19.67K<br>4.05 / 5.0<br>16.05% (13)<br>3.75% (3) | **PASS** |
| **3. AC + baby** | AC + Category = baby | Orders<br>Revenue<br>Avg Review<br>Low Rating<br>Late Delivery | 3<br>R$ 871.97<br>5.00 / 5.0<br>0.00% (0)<br>0.00% (0) | 3<br>R$ 871.97<br>5.00 / 5.0<br>0.00% (0)<br>0.00% (0) | **PASS** |
| **4. AC + health_beauty** | AC + Category = health_beauty | Orders<br>Revenue<br>Avg Review<br>Low Rating<br>Late Delivery | 6<br>R$ 1,655.00<br>4.17 / 5.0<br>16.67% (1)<br>0.00% (0) | 6<br>R$ 1,655.00<br>4.17 / 5.0<br>16.67% (1)<br>0.00% (0) | **PASS** |
| **5. SP State** | SP + All Categories | Orders<br>Revenue<br>Avg Review<br>Low Rating<br>Late Delivery | 41,746<br>R$ 5.92M<br>4.16 / 5.0<br>12.98% (5,420)<br>5.89% (2,387) | 41,746<br>R$ 5.92M<br>4.16 / 5.0<br>12.98% (5,420)<br>5.89% (2,387) | **PASS** |
| **6. SP + baby** | SP + Category = baby | Orders<br>Revenue<br>Avg Review<br>Low Rating<br>Late Delivery | 1,167<br>R$ 177.56K<br>4.15 / 5.0<br>12.77% (149)<br>6.48% (73) | 1,167<br>R$ 177.56K<br>4.15 / 5.0<br>12.77% (149)<br>6.48% (73) | **PASS** |
| **7. Category Only** | All States + Category = baby | Orders<br>Revenue<br>Avg Review<br>Low Rating<br>Late Delivery | 2,840<br>R$ 479.80K<br>4.04 / 5.0<br>16.02% (455)<br>9.26% (256) | 2,840<br>R$ 479.80K<br>4.04 / 5.0<br>16.02% (455)<br>9.26% (256) | **PASS** |
| **8. Multi-Filter** | SP + baby + Delivery = Late | Orders<br>Revenue<br>Avg Review<br>Low Rating<br>Late Delivery | 73<br>R$ 11.53K<br>2.41 / 5.0<br>57.53% (42)<br>100.00% (73) | 73<br>R$ 11.53K<br>2.41 / 5.0<br>57.53% (42)<br>100.00% (73) | **PASS** |
| **9. Segment Filter** | SP + health_beauty + Top 10% Seller | Orders<br>Revenue<br>Avg Review<br>Low Rating<br>Late Delivery | 2,109<br>R$ 347.00K<br>4.26 / 5.0<br>11.00% (232)<br>7.38% (153) | 2,109<br>R$ 347.00K<br>4.26 / 5.0<br>11.00% (232)<br>7.38% (153) | **PASS** |
| **10. Zero Records** | AC + non_existent_cat | Orders<br>Revenue<br>Avg Review<br>Low Rating<br>Late Delivery | 0<br>R$ 0.00<br>- / 5.0<br>- % (0)<br>- % (0) | 0<br>R$ 0.00<br>- / 5.0<br>- % (0)<br>- % (0) | **PASS** |

---

## 5. Final Verification Summary

- **Total Test Scenarios Audited**: 10
- **Reconciliation Errors**: **0 (Zero)**
- **Console Exceptions**: **0 (Zero)**
- **Stale Platform Subtitles**: **0 (Zero)**

All displayed dashboard metrics are 100% reconciled against the underlying analytical dataset.
