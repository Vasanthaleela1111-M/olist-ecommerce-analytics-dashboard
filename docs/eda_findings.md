# Exploratory Data Analysis (EDA) Findings Report

## Executive Summary
This document provides the formal Exploratory Data Analysis (EDA) findings across seven core operational dimensions of the Olist e-commerce dataset using the validated master order dataset (`outputs/exports/master_orders.csv`). 

To ensure objectivity and prevent premature claims, all findings are strictly categorized under four analytical tiers:
1. **Observation**: Statistical property or distributional shape observed in the data.
2. **Evidence**: Empirical metrics, sample size ($N$), parametric (mean, std) and non-parametric (median, P25, P75, IQR) statistics, and Tukey outlier counts ($1.5 \times \text{IQR}$).
3. **Interpretation**: Analytical meaning of the evidence.
4. **Possible Business Implication**: Potential business or operational impact to explore further.

> [!NOTE]
> **Exploratory Scope Notice**: No factor in this document is declared a "root cause". Causal claims are deferred to dedicated statistical hypothesis testing and diagnostic modeling.

---

## Section A: Marketplace Performance & Review Score Distributions

### 1. Observation
- Order item prices, freight values, and total order revenues exhibit right-skewed distributions with high standard deviations relative to their medians.
- Review scores are heavily skewed toward high ratings (5-star ratings dominate), with a secondary spike in 1-star ratings.

### 2. Evidence
- **Sample Size ($N$)**: 98,666 orders with valid items (out of 99,441 total master orders).
- **Total Item Price Distribution**:
  - Mean: **R$ 137.75** | Std: **R$ 210.65** | Min: **R$ 0.85** | Max: **R$ 13,440.00**
  - P25: **R$ 45.90** | Median: **R$ 86.90** | P75: **R$ 149.90** | IQR: **R$ 104.00**
  - Tukey Outlier Threshold ($> \text{P75} + 1.5 \times \text{IQR}$): **> R$ 305.90**
  - High Outlier Count: **7,913 orders** (**8.02%** of item orders).
- **Total Freight Cost Distribution**:
  - Mean: **R$ 22.82** | Std: **R$ 21.65** | Min: **R$ 0.00** | Max: **R$ 1,794.96**
  - P25: **R$ 13.85** | Median: **R$ 17.17** | P75: **R$ 24.04** | IQR: **R$ 10.19**
  - Tukey Outlier Threshold ($> \text{R\$ 39.33}$): **9,941 orders** (**10.08%** of item orders).
- **Total Order Value Distribution**:
  - Mean: **R$ 160.58** | Std: **R$ 220.47** | Median: **R$ 105.29** | P25: **R$ 61.98** | P75: **R$ 176.87**
  - High Outlier Count ($> \text{R\$ 349.21}$): **7,775 orders** (**7.88%**).
- **Review Score Breakdown ($N = 99,441$)**:
  - 5 Stars: **57,320** (**57.64%**)
  - 4 Stars: **19,142** (**19.25%**)
  - 3 Stars: **8,179** (**8.23%**)
  - 2 Stars: **3,157** (**3.17%**)
  - 1 Star: **11,643** (**11.71%**)

### 3. Interpretation
- The median order value (R$ 105.29) is substantially lower than the mean (R$ 160.58), indicating that a minority of high-value transactions pulls the average upward.
- Freight represents an average of **14.2% of total order value**, but for high-freight outliers ($> \text{R\$ 39.33}$), freight cost can rival or exceed the item purchase price.
- **76.89% of customer reviews are positive** (4 or 5 stars), while **14.88% represent negative ratings** (1 or 2 stars).

### 4. Possible Business Implication
- Platform pricing and promotions should be evaluated against median order values rather than means to reflect typical buyer behavior.
- High-freight outliers present a potential friction point for cart abandonment and buyer dissatisfaction.

---

## Section B: Delivery Timing & Delay Distributions

### 1. Observation
- Actual delivery lead time is significantly shorter on average than the estimated delivery lead time promised to customers.
- Delivery delay (Actual Date minus Estimated Date) is negative for the vast majority of orders, indicating conservative delivery buffer estimates by Olist.

### 2. Evidence
- **Sample Size ($N$)**: 96,470 delivered orders with valid delivery timestamps.
- **Actual Delivery Lead Time Distribution**:
  - Mean: **12.56 days** | Std: **9.55 days** | Min: **0.53 days** | Max: **209.63 days**
  - P25: **6.77 days** | Median: **10.22 days** | P75: **15.72 days** | IQR: **8.95 days**
  - High Outlier Threshold ($> 29.15\text{ days}$): **4,896 orders** (**5.08%**).
- **Estimated Delivery Lead Time Distribution**:
  - Mean: **23.74 days** | Std: **8.76 days** | Median: **23.23 days** | P25: **18.33 days** | P75: **28.41 days**
- **Delivery Delay Days Distribution ($\text{Actual} - \text{Estimated}$)**:
  - Mean: **-11.18 days** | Std: **10.18 days** | Median: **-11.95 days**
  - On-Time / Early Rate ($\text{Delay} \le 0$): **91.89%** ($N = 88,644$ orders)
  - Late Delivery Rate ($\text{Delay} > 0$): **8.11%** ($N = 7,826$ orders)
  - Severe Late Outliers ($> +8.39\text{ days}$ late): **2,829 orders** (**2.93%**).

### 3. Interpretation
- Olist sets conservative estimated delivery dates, overestimating actual delivery duration by an average of **11.18 days**.
- While 91.89% of orders arrive before or on the estimated date, **8.11% of delivered orders exceed the promised estimate**, with severe outliers taking up to 209 days.

### 4. Possible Business Implication
- Excessive estimated lead times may depress conversion rates if buyers perceive delivery as too slow.
- Late delivery outliers, though representing ~8% of volume, represent operational failures that warrant targeted logistics tracking.

---

## Section C: Customer Dynamics & Order Frequency

### 1. Observation
- The customer base is almost entirely composed of single-purchase buyers, with an extremely low repeat purchase rate.

### 2. Evidence
- **Sample Size ($N$)**: 96,096 unique customer entities (`customer_unique_id`).
- **Customer Purchase Frequency Distribution**:
  - Mean Orders per Customer: **1.035** | Std: **0.214** | Median: **1.0** | Max: **17.0**
  - Single-Order Customers: **93,099 buyers** (**96.88%** of unique buyers)
  - Repeat Customers ($> 1\text{ order}$): **2,997 buyers** (**3.12%** of unique buyers)
  - Customer Order Count Breakdown:
    - 1 order: 93,099 customers (96.88%)
    - 2 orders: 2,745 customers (2.86%)
    - 3 orders: 203 customers (0.21%)
    - 4+ orders: 50 customers (0.05%)

### 3. Interpretation
- Olist operates predominantly as a one-time transactional marketplace rather than a high-retention subscription or repeat-use platform during the 2016-2018 dataset window.

### 4. Possible Business Implication
- Customer Acquisition Cost (CAC) must be recovered on the first transaction due to low organic repurchase rates.
- Retention programs, post-purchase engagement, and loyalty incentives represent significant unexploited growth opportunities.

---

## Section D: Seller Merchant Profiling & Revenue Concentration

### 1. Observation
- Seller transaction volume and revenue generation are highly concentrated among a small minority of high-volume merchant sellers.

### 2. Evidence
- **Sample Size ($N$)**: 3,085 active sellers (`primary_seller_id`).
- **Seller Order Volume Distribution**:
  - Mean: **31.98 orders** | Std: **104.05** | Min: **1** | Max: **1,841 orders**
  - P25: **2.0** | Median: **6.0** | P75: **21.0** | IQR: **19.0**
  - High Outliers ($> 49.5\text{ orders}$): **424 sellers** (**13.74%** of sellers).
- **Seller Total GMV Distribution**:
  - Mean: **R$ 4,405.72** | Std: **R$ 13,926.29** | Median: **R$ 832.41** | P25: **R$ 210.00** | P75: **R$ 3,322.08**
  - High Outliers ($> \text{R\$ 7,990.20}$): **379 sellers** (**12.29%** of sellers).
- **Pareto Concentration**:
  - Top 1% Sellers (31 sellers) generate **26.04%** of GMV.
  - Top 10% Sellers (309 sellers) generate **67.46%** of GMV.
  - Bottom 50% Sellers generate less than **3.5%** of total GMV.

### 3. Interpretation
- The seller ecosystem exhibits severe revenue asymmetry; over two-thirds of platform GMV relies on just 309 merchant sellers.

### 4. Possible Business Implication
- Operational disruptions, churn, or fulfillment failures among the top 10% of sellers pose systemic revenue risks to Olist.
- Seller enablement efforts should focus on scaling mid-tier sellers (median R$ 832 GMV) into high-volume channels.

---

## Section E: Geographic Logistics Flow & Regional Disparities

### 1. Observation
- Buyers and sellers are geographically mismatched. Sellers are heavily concentrated in São Paulo (SP), while buyers are distributed across Brazil's 27 states.
- Inter-state cross-country shipments bear substantially higher freight costs and longer delivery lead times than intra-state shipments.

### 2. Evidence
- **Sample Size ($N$)**: 98,666 orders with valid geographic metadata.
- **State Concentration**:
  - **Top Seller State**: São Paulo (`SP`) represents **70.6%** of primary seller order dispatches ($N = 69,678$).
  - **Top Customer States**: `SP` (41.8%), `RJ` (12.8%), `MG` (11.6%), `RS` (5.5%), `PR` (5.0%).
- **Inter-State vs. Intra-State Performance Comparison**:
  - Intra-State Shipments ($N = 35,483$, 35.96%): Mean Freight **R$ 15.46** | Mean Lead Time **7.95 days** | Late Rate **6.06%**
  - Inter-State Shipments ($N = 63,183$, 64.04%): Mean Freight **R$ 26.96** | Mean Lead Time **15.15 days** | Late Rate **9.27%**
- **Regional Disparities**:
  - Southeast (`SE`): Mean Freight **R$ 18.84** | Mean Lead Time **10.51 days**
  - Northeast (`NE`): Mean Freight **R$ 33.64** | Mean Lead Time **18.73 days**
  - North (`N`): Mean Freight **R$ 38.65** | Mean Lead Time **19.82 days**

### 3. Interpretation
- Inter-state shipping imposes a **+74.4% freight cost penalty** and **+90.6% lead time penalty** compared to local intra-state orders.
- Customers in the North and Northeast regions suffer from double the delivery lead time and nearly double the freight costs of Southeast customers.

### 4. Possible Business Implication
- Regional fulfillment centers or seller onboarding incentives in North/Northeast/South regions could dramatically improve delivery speed and reduce shipping fees.

---

## Section F: Product Category Profiling & Benchmarks

### 1. Observation
- Product sales are concentrated in high-volume consumer goods categories, while heavy/bulky categories bear extreme freight-to-price ratios.

### 2. Evidence
- **Sample Size ($N$)**: 73 product categories ($N \ge 50$ orders threshold applied).
- **Top 5 Categories by Total GMV**:
  1. `health_beauty`: GMV **R$ 1,259,968.04** ($N = 8,803$ orders, Item Price R$ 130.17, Freight R$ 19.34, Review 4.17)
  2. `watches_gifts`: GMV **R$ 1,203,090.21** ($N = 5,603$ orders, Item Price R$ 201.44, Freight R$ 18.06, Review 4.05)
  3. `bed_bath_table`: GMV **R$ 1,031,939.54** ($N = 9,299$ orders, Item Price R$ 93.30, Freight R$ 19.82, Review 3.96)
  4. `sports_leisure`: GMV **R$ 987,819.48** ($N = 7,685$ orders, Item Price R$ 114.33, Freight R$ 21.05, Review 4.16)
  5. `computers_accessories`: GMV **R$ 912,684.83** ($N = 6,661$ orders, Item Price R$ 116.92, Freight R$ 20.35, Review 4.02)
- **Extreme Freight-to-Price Ratio Categories**:
  - `furniture_mattress_office`: Freight Ratio **52.4%** (Mean Freight R$ 56.40 vs Price R$ 107.60)
  - `furniture_decor`: Freight Ratio **29.8%** (Mean Freight R$ 25.40 vs Price R$ 85.20)

### 3. Interpretation
- Categories involving bulky items (furniture, office decor) face heavy shipping penalties that often represent >30-50% of the item purchase price.
- High-performing categories (`health_beauty`, `watches_gifts`) benefit from compact dimensions and favorable weight-to-value ratios.

### 4. Possible Business Implication
- Bulky category logistics require specialized carrier partnerships or subsidized shipping tiers to remain competitive.

---

## Section G: Payment Behavior & Installment Financing

### 1. Observation
- Credit Card is the primary payment mechanism, with a large share of transactions utilizing multi-month installment financing.
- Order values scale upwards significantly as the number of installments increases.

### 2. Evidence
- **Sample Size ($N$)**: 99,440 orders with payment records.
- **Payment Method Distribution**:
  - **Credit Card**: **74,975 orders** (**75.40%** share) | Total GMV **R$ 12.54M** (**78.35%**) | Mean Order Value **R$ 167.29**
  - **Boleto (Bank Slip)**: **19,784 orders** (**19.90%** share) | Total GMV **R$ 2.87M** (**17.92%**) | Mean Order Value **R$ 145.03**
  - **Voucher**: **3,151 orders** (**3.17%** share) | Total GMV **R$ 0.38M** (**2.37%**) | Mean Order Value **R$ 120.29**
  - **Debit Card**: **1,527 orders** (**1.54%** share) | Total GMV **R$ 0.22M** (**1.36%**) | Mean Order Value **R$ 142.72**
- **Credit Card Installment Tier Breakdown ($N = 74,975$)**:
  - 1 Installment: 32,555 orders (43.42%) | Mean Order Value **R$ 135.53** | Median **R$ 85.30** | Review **4.16**
  - 2 - 3 Installments: 21,714 orders (28.96%) | Mean Order Value **R$ 141.05** | Median **R$ 102.50** | Review **4.15**
  - 4 - 6 Installments: 12,042 orders (16.06%) | Mean Order Value **R$ 202.94** | Median **R$ 157.90** | Review **4.10**
  - 7 - 10 Installments: 8,367 orders (11.16%) | Mean Order Value **R$ 277.67** | Median **R$ 208.80** | Review **4.04**
  - 11+ Installments: 297 orders (0.40%) | Mean Order Value **R$ 432.18** | Median **R$ 345.90** | Review **3.88**

### 3. Interpretation
- Installment credit options enable Brazilian consumers to purchase significantly higher-value items. Orders paid in 7-10 installments have **more than double the Average Order Value** (R$ 277.67 vs R$ 135.53) of single-payment orders.

### 4. Possible Business Implication
- Installment financing is an essential driver of platform GMV and basket size. Promoting flexible 4-10 installment options for high-ticket electronics and furniture can directly expand revenue.
