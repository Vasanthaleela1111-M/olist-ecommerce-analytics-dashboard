# Olist Marketplace Analytics: Comprehensive Executive Story

---

## 1. Executive Summary

This document presents the definitive analytical narrative for the **Olist Brazilian E-Commerce Marketplace**, grounded in the audited master analytical dataset ($N = 99,441$ orders across 9 raw CSV files, spanning September 2016 through October 2018).

The objective of this analysis is to evaluate marketplace growth, identify core operational drivers of customer satisfaction, audit seller and geographic bottlenecks, evaluate category and payment friction, establish an evidence-based root-cause hierarchy, and define actionable operational recommendations.

### Key Strategic Discoveries:
1. **Scale Expansion vs. Customer Satisfaction**: Marketplace volume grew **+714%** (from 800 orders in Jan 2017 to 6,512 orders in Aug 2018), generating **R$ 15.84M** total revenue. Monthly customer review scores correlate near zero with monthly order volume ($r = -0.1266$), proving that growth alone does not degrade customer satisfaction.
2. **Logistics Late Delivery as the Primary Dissatisfaction Driver**: On-time delivered orders ($N = 88,644$) exhibit a low-rating rate of **9.49%** (4.28 stars). Late delivered orders ($N = 7,826$) experience a low-rating rate of **54.64%** (2.55 stars), representing an absolute difference of **+45.14 percentage points** (**3.62x Relative Risk** vs. platform baseline **15.09%**). Severe delays ($\ge 4$ days, $N = 4,664$) push low ratings to **75.09%** (**4.97x Relative Risk**).
3. **Geographic Trunk Line Bottlenecks**: **70.57% of seller shipments** originate in São Paulo (`SP`). The single largest interstate route, `SP -> RJ` ($N = 8,431$ orders), suffers a **14.99% late delivery rate** ($N = 1,264$ late orders) and a **22.57% low-rating rate** (**+7.48 percentage points** above baseline).
4. **Heavy Goods Category Friction**: `office_furniture` ($N = 1,264$) registers the lowest category review score at **3.62 stars** and a **22.63% low-rating rate** (**+7.54 percentage points** above baseline). This is associated with heavy dimensions driving an average freight fee of **R$ 53.98** (+136.5% vs. R$ 22.82 baseline) and an average lead time of **20.71 days** (vs. 12.50 days baseline).
5. **Non-Causal Observational Standard**: Operational variables (such as payment method, freight ratio, and repeat buyer status) show negligible direct association with review scores once fulfillment lateness is controlled for.

---

## 2. Marketplace Performance

### Finding 2.1: Volume and Revenue Scaling
- **Exact Metric**: Monthly order volume expanded from 800 orders (Jan 2017) to 6,512 orders (Aug 2018), peaking at 7,544 orders during Black Friday (Nov 2017). Total gross revenue reached **R$ 15,843,553.24** (R$ 13,591,643.70 GMV + R$ 2,251,909.54 Freight).
- **Baseline Benchmark**: Initial 2017 Q1 monthly volume averaged 1,754 orders/month.
- **Difference**: Absolute volume growth of **+5,712 orders/month** (**+714.0%** increase). Monthly GMV scaled from R$ 137.19K (Jan 2017) to R$ 1.18M (Nov 2017).
- **Sample Size ($N$)**: $N = 99,441$ total marketplace orders.
- **Business Implication**: Rapid demand acquisition confirms high market demand for Olist's merchant aggregation model, sustaining monthly GMV over R$ 1.0M throughout 2018.

### Finding 2.2: Average Order Value (AOV) Stability
- **Exact Metric**: Overall Average Order Value (AOV) averaged **R$ 160.58** per order (GMV + Freight).
- **Baseline Benchmark**: Monthly AOV ranged tightly between R$ 145.30 (July 2017) and R$ 171.56 (April 2017).
- **Difference**: Absolute variance across core operating months was within $\pm \text{R\$ } 13.00$ (**< 8.1%** shift).
- **Sample Size ($N$)**: $N = 99,441$ orders.
- **Business Implication**: Revenue expansion was driven almost entirely by new order acquisition rather than basket inflation or price increases.

### Finding 2.3: Scale vs. Satisfaction Independence
- **Exact Metric**: Correlation between monthly order volume and average review score is **$r = -0.1266$**. Correlation between monthly late delivery rate and low-rating rate is **$r = +0.7940$**.
- **Baseline Benchmark**: Baseline platform average review score is **4.07 stars** with a **15.09% low-rating rate**.
- **Difference**: Review scores in June 2018 (4.27 stars at 6,167 orders/month) exceeded January 2017 (4.05 stars at 800 orders/month) because June 2018 late delivery rate dropped to **1.36%**.
- **Sample Size ($N$)**: $N = 20$ core operating months (Jan 2017 – Aug 2018).
- **Business Implication**: Marketplace scale does not inherently degrade customer satisfaction. Customer review dips during peak months (Black Friday Nov 2017: 3.89 stars; March 2018: 3.73 stars) are strongly associated with carrier delivery bottlenecks rather than platform volume growth.

---

## 3. Delivery and Customer Satisfaction

### Finding 3.1: On-Time vs. Late Delivery Dissatisfaction Disparity
- **Exact Metric**: Late delivered orders ($N = 7,826$) exhibit a low-rating rate of **54.64%** and an average review score of **2.55 stars**. On-time delivered orders ($N = 88,644$) exhibit a low-rating rate of **9.49%** and an average review score of **4.28 stars**.
- **Baseline Benchmark**: Platform baseline low-rating rate is **15.09%** (**4.07 stars**).
- **Difference**: Absolute low-rating increase of **+45.14 percentage points** above on-time orders (**+39.54 percentage points** above platform baseline). Mean review drop of **-1.74 stars**.
- **Sample Size ($N$)**: $N = 96,470$ delivered orders.
- **Business Implication**: Fulfillment lateness is the single largest operational catalyst for customer dissatisfaction. Passing the estimated delivery date increases low-rating likelihood by **5.75x** relative to on-time delivery (**3.62x Relative Risk** vs. baseline).

### Finding 3.2: Severe and Extreme Delay Thresholds
- **Exact Metric**: Orders delayed by $\ge 4$ days ($N = 4,664$) register a **75.09% low-rating rate** (1.84 stars). Orders delayed by $\ge 10$ days ($N = 2,299$) register a **79.43% low-rating rate** (1.69 stars).
- **Baseline Benchmark**: On-time baseline low-rating rate is **9.49%**.
- **Difference**: Absolute increase of **+65.60 percentage points** for $\ge 4$ day delays (**4.97x Relative Risk** vs. baseline; **7.91x** vs. on-time).
- **Sample Size ($N$)**: $N = 4,664$ severe late orders; $N = 2,299$ extreme late orders.
- **Business Implication**: Lateness beyond 3 days represents a critical non-linear tipping point where customer tolerance vanishes, resulting in near-universal 1-star reviews.

### Finding 3.3: Seller Dispatch Handoff Lag
- **Exact Metric**: Orders with slow seller dispatch handoff ($> 5$ days to carrier, $N = 14,180$) exhibit a low-rating rate of **22.26%** (3.75 stars). Extreme slow dispatch ($> 10$ days, $N = 3,425$) reaches **33.75% low ratings** (3.28 stars). Fast dispatch ($\le 5$ days, $N = 83,464$) exhibits **12.42% low ratings** (4.18 stars).
- **Baseline Benchmark**: Platform baseline low-rating rate is **15.09%**.
- **Difference**: Absolute increase of **+7.17 percentage points** for slow dispatch (**1.47x Relative Risk**); **+18.66 percentage points** for extreme slow dispatch (**2.24x Relative Risk**).
- **Sample Size ($N$)**: $N = 97,644$ orders with dispatch records.
- **Business Implication**: Upstream seller handoff delays consume carrier delivery buffers, directly elevating the probability of final delivery lateness.

---

## 4. Seller and Geographic Hotspots

### Finding 4.1: Seller Volume Concentration (Pareto Distribution)
- **Exact Metric**: Out of 3,085 active merchants, the top 1% of sellers ($N = 31$) generate **26.04% of total GMV** (R$ 3.54M). The top 10% of sellers ($N = 309$) generate **67.46% of total GMV** (R$ 9.17M).
- **Baseline Benchmark**: Uniform merchant distribution baseline would allocate 10% GMV to the top 10% of sellers.
- **Difference**: Top 10% merchants generate **6.75x** their proportional share of total marketplace revenue.
- **Sample Size ($N$)**: $N = 3,085$ active sellers.
- **Business Implication**: Revenue concentration creates structural operational risk. Operational seller dispatch failures among the top 300 merchants disproportionately impact platform-wide revenue and satisfaction.

### Finding 4.2: Origin-Destination Mismatch & Inter-State Freight Drag
- **Exact Metric**: **70.57% of seller shipments** ($N = 69,678$) originate from São Paulo (`SP`), whereas **58.2% of buyers** reside outside `SP`. Inter-state shipments ($N = 63,183$, 64.04% of orders) average **R$ 26.96 freight cost** and **15.15 days lead time**, compared to intra-state shipments ($N = 35,483$) which average **R$ 15.46 freight cost** and **7.95 days lead time**.
- **Baseline Benchmark**: Intra-state shipping baseline (R$ 15.46 freight, 7.95 days lead time).
- **Difference**: Inter-state shipping incurs **+74.4% higher freight fees** (+R$ 11.50) and **+90.6% longer lead times** (+7.20 days).
- **Sample Size ($N$)**: $N = 98,666$ state-mapped orders.
- **Business Implication**: Long-distance interstate shipping from SP seller hubs to outer state buyers creates inherent fulfillment friction, higher freight costs, and increased delivery lateness risk.

### Finding 4.3: Trunk Line Corridor Bottleneck: `SP -> RJ`
- **Exact Metric**: The primary interstate shipping corridor from São Paulo sellers to Rio de Janeiro buyers (`SP -> RJ`, $N = 8,431$ orders) experiences a **14.99% late delivery rate** ($N = 1,264$ late orders) and a **22.57% low-rating rate** ($N = 1,903$ low ratings; 3.85 star average).
- **Baseline Benchmark**: Platform baseline low-rating rate is **15.09%** (**4.07 stars**); late delivery baseline is **8.11%**.
- **Difference**: Absolute increase of **+6.88 percentage points** in late rate (**1.85x** baseline late rate) and **+7.48 percentage points** in low-rating rate (**1.50x Relative Risk**).
- **Sample Size ($N$)**: $N = 8,431$ orders on the `SP -> RJ` route.
- **Business Implication**: `SP -> RJ` is Olist's single largest operational bottleneck, generating **1,903 low-rated orders** (12.7% of all platform low ratings). Transit delays between SP hubs and RJ postal distribution centers drive substantial customer dissatisfaction.

---

## 5. Product Category Findings

### Finding 5.1: High-Volume Category Champions
- **Exact Metric**: `health_beauty` ($N = 8,803$ orders, R$ 1.26M GMV) achieves a **4.17 star review score** and a **12.96% low-rating rate**. `sports_leisure` ($N = 7,685$ orders, R$ 987.8K GMV) achieves **4.16 stars** (13.29% low rating). `housewares` ($N = 5,829$ orders, R$ 635.1K GMV) achieves **4.14 stars** (13.42% low rating).
- **Baseline Benchmark**: Platform baseline review score is **4.07 stars** (**15.09% low rating**).
- **Difference**: `health_beauty` low-rating rate is **-2.13 percentage points** lower than platform baseline (**0.86x Relative Risk**).
- **Sample Size ($N$)**: $N = 22,317$ combined orders across top 3 champion categories.
- **Business Implication**: Compact, easily shippable consumer packaged goods maintain high satisfaction due to low freight ratios (14.50%) and fast carrier transit.

### Finding 5.2: High-Volume Friction Categories
- **Exact Metric**: `bed_bath_table` ($N = 9,299$ orders, R$ 1.03M GMV) records an average review score of **3.96 stars** and a **17.08% low-rating rate** ($N = 1,588$ low ratings). `computers_accessories` ($N = 6,661$ orders, R$ 912.7K GMV) records **4.01 stars** (**16.39% low rating**).
- **Baseline Benchmark**: Platform baseline low-rating rate is **15.09%**.
- **Difference**: `bed_bath_table` low-rating rate is **+1.99 percentage points** higher than baseline, generating **10.61% of all low ratings on the platform**.
- **Sample Size ($N$)**: $N = 9,299$ orders for `bed_bath_table`.
- **Business Implication**: `bed_bath_table` is Olist's largest volume category but suffers from non-delivery product quality complaints and sizing issues.

### Finding 5.3: Heavy Category Outlier: `office_furniture`
- **Exact Metric**: `office_furniture` ($N = 1,264$ orders, R$ 273.2K GMV) registers an average review score of **3.62 stars** and a **22.63% low-rating rate** ($N = 286$ low-rated orders). Average freight cost is **R$ 53.98** (24.98% freight ratio) and average lead time is **20.71 days**.
- **Baseline Benchmark**: Platform baseline review score is **4.07 stars**; baseline low-rating rate is **15.09%**; baseline freight is **R$ 22.82**; baseline lead time is **12.50 days**.
- **Difference**: Absolute review drop of **-0.45 stars**, low-rating increase of **+7.54 percentage points** (**1.50x Relative Risk**), freight surcharge of **+R$ 31.16** (**+136.5%**), and lead time increase of **+8.21 days** (**+65.7%**).
- **Sample Size ($N$)**: $N = 1,264$ orders.
- **Business Implication**: Heavy, bulky dimensions require specialized freight handling. Standard postal logistics result in transit damage, long lead times, and high freight fees that severely degrade customer satisfaction.

---

## 6. Payment Findings

### Finding 6.1: Credit Card Installment Basket Escalation
- **Exact Metric**: Credit Card transactions ($N = 74,975$, 75.40% of orders, R$ 12.54M GMV) scale in Average Order Value (AOV) based on installment term. Single installment (1-pay, $N = 24,004$) averages **R$ 100.91 AOV**. 7–10 installments ($N = 11,819$) average **R$ 336.44 AOV**. 11+ installments ($N = 341$) average **R$ 360.37 AOV**.
- **Baseline Benchmark**: Single-installment AOV baseline (R$ 100.91).
- **Difference**: 7–10 installments expand AOV by **+R$ 235.53** (**3.33x AOV multiplier**, $+233.4\%$). 11+ installments expand AOV by **+R$ 259.46** (**3.57x AOV multiplier**).
- **Sample Size ($N$)**: $N = 74,975$ credit card orders.
- **Business Implication**: Installment financing (*parcelamento*) is the primary engine enabling buyers to purchase high-ticket items (electronics, appliances, furniture).

### Finding 6.2: Installment Term vs. Low-Rating Rate Escalation
- **Exact Metric**: Single installment credit card orders record a **13.37% low-rating rate** (4.14 stars). 7–10 installments record **17.83% low ratings** (3.98 stars). 11+ installments record **21.70% low ratings** (3.84 stars).
- **Baseline Benchmark**: 1-installment credit card low-rating rate baseline (13.37%).
- **Difference**: Absolute increase of **+4.46 percentage points** for 7–10 installments (**1.33x** vs. 1-pay baseline); **+8.33 percentage points** for 11+ installments (**1.62x** vs. 1-pay baseline).
- **Sample Size ($N$)**: $N = 74,975$ credit card orders.
- **Business Implication**: Higher installment counts correlate with high item prices and heavy/complex items. High-ticket purchases carry higher buyer expectations, resulting in elevated low ratings when fulfillment issues occur.

### Finding 6.3: Boleto Clearance Lag & Late Delivery Penalty
- **Exact Metric**: Boleto Bancário payments ($N = 19,784$, 19.90% order share, R$ 2.87M GMV) record an average review score of **4.07 stars** and a low-rating rate of **14.85%**, but suffer a **8.88% late delivery rate** ($N = 1,757$ late orders), compared to **7.96% for Credit Cards** ($N = 5,968$).
- **Baseline Benchmark**: Credit card late delivery rate baseline (**7.96%**).
- **Difference**: Absolute late delivery rate penalty of **+0.92 percentage points** (**1.12x Relative Risk**). Average review score (4.0714) is virtually identical to credit cards (4.0726).
- **Sample Size ($N$)**: $N = 19,784$ Boleto orders.
- **Business Implication**: Boleto bank slip processing introduces a 1–3 business day clearance lag before order authorization is sent to sellers. This clearance lag consumes fulfillment buffer days, modestly elevating final delivery lateness without directly reducing customer review scores.

---

## 7. Root Cause Hierarchy

Based on empirical evidence across $N = 99,441$ reviewed orders, candidate operational, geographic, financial, and behavioral factors are classified into four evidence-based tiers:

| Evidence Tier | Operational Factor | Sample Size ($N$) | Mean Review | Low Rating Rate (%) | Baseline Low Rate (%) | Abs Diff (pp) | Relative Risk vs Baseline | Evidence Classification |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Tier 1** | **Delivery Delay ($> 0$ days)** | $7,826$ | **2.55** | **54.64%** | 15.09% | **+39.54** | **3.62x** | **PRIMARY-LIKE FACTOR** |
| **Tier 1** | **Severe Delay ($\ge 4$ days)** | $4,664$ | **1.84** | **75.09%** | 15.09% | **+59.99** | **4.97x** | **PRIMARY-LIKE FACTOR** |
| **Tier 1** | **Extreme Delay ($\ge 10$ days)**| $2,299$ | **1.69** | **79.43%** | 15.09% | **+64.33** | **5.26x** | **PRIMARY-LIKE FACTOR** |
| **Tier 2** | **Slow Seller Dispatch ($> 5$ days)**| $14,180$| **3.75** | **22.26%** | 15.09% | **+7.17** | **1.47x** | **SECONDARY CONTRIBUTOR** |
| **Tier 2** | **High Item Price ($> \text{R\$ } 200$)**| $14,992$| **3.95** | **18.59%** | 15.09% | **+3.50** | **1.23x** | **SECONDARY CONTRIBUTOR** |
| **Tier 2** | **CC 7–10 Installments** | $11,819$| **3.98** | **17.83%** | 15.09% | **+2.73** | **1.18x** | **SECONDARY CONTRIBUTOR** |
| **Tier 3** | **Outlier: `office_furniture`**| $1,264$ | **3.62** | **22.63%** | 15.09% | **+7.54** | **1.50x** | **SEGMENT HOTSPOT** |
| **Tier 3** | **Route: `SP -> RJ` Corridor** | $8,431$ | **3.85** | **22.57%** | 15.09% | **+7.48** | **1.50x** | **SEGMENT HOTSPOT** |
| **Tier 3** | **Friction: `bed_bath_table`**| $9,299$ | **3.96** | **17.08%** | 15.09% | **+1.99** | **1.13x** | **SEGMENT HOTSPOT** |
| **Tier 4** | **High Freight Ratio ($> 50\%$)**| $15,610$| **4.04** | **15.27%** | 15.09% | **+0.18** | **1.01x** | **WEAK / UNSUPPORTED** |
| **Tier 4** | **Payment Method: Boleto** | $19,784$| **4.07** | **14.85%** | 15.09% | **-0.24** | **0.98x** | **WEAK / UNSUPPORTED** |
| **Tier 4** | **Repeat Buyer Status** | $6,342$ | **4.10** | **14.81%** | 15.09% | **-0.28** | **0.98x** | **WEAK / UNSUPPORTED** |

```
                    [ Hierarchy of Root-Cause Factor Impact ]

 Tier 1: PRIMARY-LIKE FACTORS
  └── Delivery Delay (> 0 Days)        [Low Rating: 54.64%, Relative Risk: 3.62x]
  └── Severe Delay (>= 4 Days)         [Low Rating: 75.09%, Relative Risk: 4.97x]

 Tier 2: SECONDARY CONTRIBUTORS
  └── Slow Seller Dispatch (> 5 Days)  [Low Rating: 22.26%, Relative Risk: 1.47x]
  └── High Item Price (> R$ 200)       [Low Rating: 18.59%, Relative Risk: 1.23x]
  └── High Credit Card Installments    [Low Rating: 17.83%, Relative Risk: 1.18x]

 Tier 3: SEGMENT-SPECIFIC HOTSPOTS
  └── Outlier Category office_furniture [Low Rating: 22.63%, Relative Risk: 1.50x]
  └── Hotspot Route SP -> RJ           [Low Rating: 22.57%, Relative Risk: 1.50x]
  └── High-Volume Friction bed_bath_table [Low Rating: 17.08%, N = 1,588 low ratings]

 Tier 4: WEAK / UNSUPPORTED FACTORS
  └── Freight Burden Ratio (> 50%)     [Low Rating: 15.27%, Relative Risk: 1.01x -- No Impact]
  └── Payment Method (Boleto vs CC)    [Low Rating: 14.85%, Relative Risk: 0.98x -- No Impact]
  └── Repeat Buyer Status              [Low Rating: 14.81%, Relative Risk: 0.98x -- No Impact]
```

---

## 8. Three Highest-Priority Recommendations

### Recommendation 1: Dynamic Promised-Date Buffer Adjustment on High-Delay Routes (`SP -> RJ`)
- **Action**: Increase estimated delivery date buffers by **+3 to +4 business days** on identified bottleneck interstate routes, specifically `SP -> RJ` ($N = 8,431$ orders, 14.99% late rate) and Northeast routes (`SP -> AL`, `SP -> MA`).
- **Targeted Impact**: Eliminates false lateness triggers for ~1,200 orders annually on the `SP -> RJ` corridor alone. Preventing late delivery status on these orders is associated with reducing low ratings from **54.64% down to 9.49%**, protecting an estimated **R$ 200K+ in annual GMV**.

### Recommendation 2: Strict 3-Day Seller Dispatch SLA Enforcement & Performance Penalties
- **Action**: Enforce a mandatory **3-business-day carrier dispatch SLA** for sellers, backed by automatic search ranking downgrades and merchant suspension for repeated slow dispatch ($> 5$ days, $N = 14,180$ orders).
- **Targeted Impact**: Prevents upstream seller delays from eating into carrier shipping windows. Eliminating slow dispatch reduces low-rating rate on affected orders from **22.26% down to 12.42%** (**-9.84 percentage points** absolute reduction).

### Recommendation 3: Specialized Bulky Freight Logistics Partnership for `office_furniture`
- **Action**: Establish specialized heavy-goods carrier agreements (with white-glove assembly options) for heavy categories like `office_furniture` ($N = 1,264$ orders, R$ 53.98 average freight, 20.71-day lead time).
- **Targeted Impact**: Reduces delivery lead times from **20.71 days down to ~12.50 days** and minimizes transit damage, targeting a reduction in `office_furniture` low ratings from **22.63% down to the 15.09% platform baseline**.

---

## 9. Measurement KPIs

To track operational improvements following implementation, Olist leadership should monitor the following core KPIs:

| KPI Category | Metric Name | Baseline Value ($N = 99,441$) | Target Value (12-Month) | Primary Operational Objective |
| :--- | :--- | :---: | :---: | :--- |
| **Fulfillment** | **Platform Late Delivery Rate (%)** | **8.11%** | **< 4.00%** | Cut overall carrier delivery lateness by 50%. |
| **Fulfillment** | **`SP -> RJ` Route Late Rate (%)** | **14.99%** | **< 6.00%** | Resolve largest interstate corridor bottleneck. |
| **Seller Ops** | **Seller Slow Dispatch Rate ($> 5$d %)**| **14.26%** | **< 5.00%** | Enforce 3-day merchant handoff SLA. |
| **Customer Sat**| **Platform Low-Rating Rate (1-2 Stars %)**| **15.09%** | **< 11.50%** | Reduce overall customer dissatisfaction rate. |
| **Customer Sat**| **Overall Average Review Score** | **4.07 stars** | **> 4.25 stars** | Elevate baseline marketplace review score. |
| **Category Ops**| **`office_furniture` Low-Rating Rate (%)**| **22.63%** | **< 15.00%** | Restructure heavy-goods logistics pipeline. |

---

## 10. Limitations

1. **Observational Data Constraint**: All findings represent empirical associations derived from historical e-commerce transaction logs. No controlled experimental A/B testing was conducted. Causal language is strictly avoided.
2. **Missing Customer Service Interaction Logs**: The dataset lacks pre-review customer service ticket logs, live chat interactions, or buyer return request histories, which could provide additional context for non-delivery product quality complaints.
3. **Third-Party Carrier Operational Visibility**: Specific carrier identities (e.g., Correios vs. private courier networks) are anonymized in the raw datasets, precluding direct carrier-by-carrier SLA benchmarking.
4. **Text Review Mining Subsample**: Customer text review comments are present for $N = 6,742$ low-rated orders out of $N = 14,955$ total low-rated orders ($45.1\%$ comment availability rate). Text mining keyphrase findings reflect this reviewed subsample.
