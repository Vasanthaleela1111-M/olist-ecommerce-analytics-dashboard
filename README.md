# Olist E-Commerce Executive Analytics Dashboard & Logistics Audit

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Dashboard Status](https://img.shields.io/badge/dashboard-live%20v1.0-brightgreen.svg)](http://localhost:8000/app/index.html)
[![Data Grain](https://img.shields.io/badge/data_grain-1_Row_=_1_Order-orange.svg)]()

An enterprise-grade, evidence-based data analytics platform and interactive web dashboard built on the Brazilian Olist E-Commerce dataset ($N = 99,441$ orders, $R\$ 15.84\text{M}$ GMV across 2016–2018). 

The platform translates complex multi-table relational data into actionable operational strategies, featuring an automated **11-step analytical pipeline**, a **Machine Learning Delivery Risk Classifier**, a **Seller SLA Health Scorecard**, an **Interactive Order Drill-Down Engine**, and a **Real-Time "What-If" Logistics Policy Simulator**.

---

## 🌟 Executive Key Metrics Summary

| Metric | Platform Benchmark Value | Context & Scope |
| :--- | :--- | :--- |
| **Total Analyzed Volume** | **99,441 Orders** | $N = 96,470$ Delivered Orders evaluated for logistics & ratings |
| **Total Platform Gross GMV** | **R\$ 15.84 Million** | R\$ 13.59M Items + R\$ 2.25M Freight |
| **Average Review Score** | **4.07 / 5.0 Stars** | Baseline customer satisfaction rating |
| **Low Rating Rate (1–2 Stars)** | **15.09%** | 15,010 low-rated orders platform-wide |
| **Late Delivery Rate** | **8.11%** | 7,826 orders delivered past estimated date |
| **Inter-State Shipping Share** | **64.04%** | 63,183 orders crossing state boundaries |

---

## 🚀 Key Features

### 🖥️ 1. Interactive Executive Analytics Dashboard
- **Single-Source Canonical Filtering**: Powered by `window.OLIST_DATA.orders_spine` (99,441 order rows), dynamically updating all KPIs, subtitles, data tables, and Chart.js instances in real-time (~2ms response).
- **Multi-Tab Modular Navigation**:
  - **Overview**: 60-second executive story digest, monthly volume scaling vs. review score stability.
  - **Delivery**: Delay severity bucket breakdown, state-by-state late delivery impact.
  - **Geography**: Inter-state vs. intra-state freight cost/lead time comparison, high-volume shipping route hotspots (`SP -> RJ`, `SP -> MG`).
  - **Categories**: Volume vs. review score matrix, heavy bulky category friction (`office_furniture`).
  - **Sellers**: Top seller pareto concentration, Seller SLA Health Scorecard & Badge System.
  - **Payments**: Credit card installment distribution, payment method revenue breakdown.
  - **Root Cause & NLP**: Customer complaint sentiment themes, delay vs. rating impact.
  - **Recommendations**: Prioritized operational roadmap with ROI estimates.

### 🎛️ 2. Real-Time "What-If" Logistics Policy Simulator
- **Interactive Control Sliders**:
  1. **Inject Route Buffer Days** ($0$ to $+7$ days): Extends estimated delivery promise windows to eliminate false lateness penalties.
  2. **Max Seller Dispatch SLA Cap** ($1$ to $10$ days): Enforces carrier handoff SLA caps to eliminate seller warehouse lag.
- **Mathematical Delay Reduction Engine**: Computes exact order-level net delay $D' = D - \text{bufferDays} - \max(0, \text{carrierDispatch} - \text{dispatchSLA})$ across all 99,441 orders in real-time.
- **Projected Impact Outputs**:
  - **Projected Late Delivery Rate (%)** vs. baseline.
  - **Projected Average Review Score** (+0.00 to +0.25 Stars recovery).
  - **1-Star/2-Star Reviews Prevented** count.
  - **Protected GMV Value (R\$)** preserved revenue.

### 🔍 3. Order-Level Drill-Down Modal
- **Detailed Row Inspection**: Clicking any route, state, category, or seller row opens a full order-level drill-down modal displaying order ID, purchase date, customer/seller state, item price, freight cost, review score, and fulfillment status.

### 🤖 4. Machine Learning & Seller SLA Health Scorecard
- **Q9 ML Delivery Delay Risk Classifier**: Predicts high-risk delay orders using seller dispatch lead time, transit distance, state corridor, and category weight.
- **Q10 Seller Health Scorecard**: Automated grading system (A+ to F) evaluating sellers on dispatch SLA compliance ($\le 3$ days), late delivery rate, and low rating percentage with automated badging (`Platinum Preferred`, `Silver At-Risk`, `Terminated`).

---

## 📊 Core Analytical Findings

1. **Marketplace Volume Scaling vs. Rating Lockstep**:
   - Order volume expanded **+714%** (from 788 to 7,380 peak monthly orders) without overall review score degradation (r = -0.13).
   - Monthly average review score drops correlate strictly in lockstep with monthly late delivery rate spikes ($r = +0.79$).

2. **Delivery Lateness Multiplier**:
   - Late delivery is associated with a **5.76x risk multiplier** for customer low ratings (54.64% low ratings for late orders vs. 9.49% for on-time orders).
   - Severe delay ($\ge 4$ days late) leads to **75.09% 1–2 star ratings** (4.97x relative risk vs. baseline).

3. **Geographic Concentration Friction**:
   - **70.57% of sellers** operate in São Paulo state (SP), forcing **64.04% of orders** to cross state borders.
   - Inter-state shipping imposes a **+74.4% freight cost surcharge** (R\$ 24.58 vs R\$ 14.09) and a **+90.6% lead time lag** (15.15 days vs 7.95 days).
   - Shipping corridor `SP -> RJ` ($N = 8,431$) exhibits a 14.99% late delivery rate and 22.57% low rating rate.

4. **Product Category Outliers**:
   - Bulky category `office_furniture` ($N = 1,264$) is the worst fulfillment outlier: **3.62 stars**, **22.63% low rating rate**, **R\$ 53.98 average freight** (+136.5% vs baseline), and **20.71-day lead time**.

---

## 📁 Repository Structure

```
olist-ecommerce-analytics-dashboard/
├── app/                        # Web Dashboard Frontend
│   ├── index.html              # Single-Page Application Markup
│   ├── css/
│   │   └── style.css           # Premium Dark-Theme Glassmorphism Styling
│   └── js/
│       ├── app.js              # Core Application & Filter Engine
│       └── data.js             # Compiled Canonical Order Spine & Aggregates
├── data/                       # Raw Olist Dataset CSVs (Ignored in Git)
│   ├── olist_orders_dataset.csv
│   ├── olist_order_items_dataset.csv
│   ├── olist_order_reviews_dataset.csv
│   └── ...
├── outputs/                    # Processed Analytical Outputs
│   ├── exports/
│   │   └── master_orders.csv   # Canonical Master Dataset (order_id Grain)
│   └── tables/                 # Aggregated CSV Output Tables (Q0 to Q10)
├── src/                        # Python Analytical Engine
│   ├── data_loader.py          # Data Ingestion & Audit Module
│   ├── build_master.py         # Master Dataset Pipeline & Feature Engineering
│   └── analysis/               # Core Analytical Modules (Q1 to Q10)
│       ├── q1_marketplace_performance.py
│       ├── q2_delivery_performance.py
│       ├── q3_seller_geographic.py
│       ├── q4_product_category.py
│       ├── q5_payment_behavior.py
│       ├── q6_root_cause_reviews.py
│       ├── q7_customer_cohorts.py
│       ├── q9_ml_delivery_risk.py
│       └── q10_seller_health.py
├── run_analysis.py             # Master Pipeline Execution Script
└── README.md                   # Project Documentation
```

---

## 🛠️ Quick Start Guide

### Prerequisites
- **Python 3.9+**
- **Pandas, NumPy, Scikit-Learn**
- Modern Web Browser (Chrome, Edge, Firefox, Safari)

### 1. Clone the Repository
```bash
git clone https://github.com/DineshPaul-111V/olist-ecommerce-analytics-dashboard.git
cd olist-ecommerce-analytics-dashboard
```

### 2. Run the Analytical Pipeline
Executes data loading, integrity auditing, master order spine construction, and all 11 analytical modules:
```bash
python run_analysis.py
```
*Outputs are saved to `outputs/tables/` and compiled into `app/js/data.js`.*

### 3. Launch the Web Dashboard
Start a local HTTP server to launch the web dashboard:
```bash
python -m http.server 8000
```
Open your browser and navigate to:
```
http://localhost:8000/app/index.html
```

---

## 📜 License & Credits

This project is licensed under the **MIT License**. Data provided by [Olist](https://www.olist.com/) via Kaggle's [Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).
Author 
  Dinesh Paul T
