# Core Question 4: Product Category Performance Analysis

## Executive Summary

Product category performance across the Olist marketplace demonstrates significant heterogeneity in order volume, revenue, freight burden, delivery execution, and customer satisfaction. While the platform baseline average review score is **4.07 stars** with a **15.04% low-rating rate** and **8.11% late delivery rate**, customer experience varies drastically by product type.

Out of 71 total product categories present in the dataset, **59 categories** meet the minimum statistical sample size threshold of $N \ge 50$ orders (accounting for $98,409$ orders or $98.96\%$ of all platform orders).

Key Insights:
1. **High-Volume Winners**: `health_beauty` ($N = 8,803$, GMV: R$ 1,259,968.04), `sports_leisure` ($N = 7,685$, GMV: R$ 987,819.48), and `housewares` ($N = 5,829$, GMV: R$ 635,149.98) maintain above-average review scores ($\ge 4.13.17$ stars) and low late delivery rates ($7.01\% - 9.00\%$).
2. **High-Volume Friction Hotspots**: `bed_bath_table` ($N = 9,299$, GMV: R$ 1,031,939.54) and `computers_accessories` ($N = 6,661$, GMV: R$ 912,684.83$) underperform baseline customer satisfaction with **3.96 stars** ($17.08\%$ low ratings) and **4.01 stars** ($16.39\%$ low ratings) respectively.
3. **Severe Satisfaction Bottleneck**: `office_furniture` ($N = 1,264$) represents the platform's worst-performing major category, registering an average review score of **3.62 stars** and a **22.63% low-rating rate** (a **+7.59 percentage point spike** over baseline). This is driven by heavy bulky dimensions causing an average freight cost of **R$ 53.98** ($24.98\%$ freight ratio, $+136.5\%$ higher than baseline) and an average delivery lead time of **20.71 days** (vs. 12.50 days baseline).
4. **Logistics Risk Categories**: Electronics and heavy audio equipment (`electronics`, `audio`, `home_confort`) suffer from elevated delivery late rates ($9.86\% - 13.01\%$), leading to low-rating spikes up to **22.13%**.

---

## 1. Analytical Baseline & Methodology

To establish comparative benchmarks, all category metrics are evaluated against the overall platform baseline ($N = 99,441$ orders):

| Metric | Platform Baseline Value |
| :--- | :--- |
| **Total Orders** | $99,441$ |
| **Total GMV** | R$ 13,594,402.41 |
| **Mean Item Price** | R$ 137.75 |
| **Mean Freight Value** | R$ 22.82 |
| **Mean Review Score** | **4.0700 stars** |
| **Low-Rating Rate (1-2 Stars)** | **15.0400%** |
| **Late Delivery Rate** | **8.1100%** |
| **Mean Lead Time** | **12.50 days** |

### Priority Segmentation Logic
Categories with $N \ge 50$ orders are categorized into four actionable strategic segments:
- **High-Volume / High-Satisfaction**: Volume $\ge 1,000$ orders, Review Score $\ge 4.07$ stars, Low-Rating Rate $\le 15.04\%$.
- **High-Volume / Low-Satisfaction**: Volume $\ge 1,000$ orders, Review Score $< 4.07$ stars OR Low-Rating Rate $> 15.04\%$.
- **High Delivery Problems**: Late Delivery Rate $> 9.50\%$ (at least $+1.39$ percentage points above platform baseline).
- **Specialty / Niche High-Performers**: Niche categories with distinct ticket prices or high satisfaction.

---

## 2. Priority Category Segment Performance

Below is the summary of the 28 priority categories identified in `outputs/tables/q4_priority_categories.csv`:

| Priority Segment | Category | Orders ($N$) | GMV (R$) | Avg Price (R$) | Avg Freight (R$) | Freight Ratio (%) | Avg Review | Low-Rating Rate (%) | Late Rate (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **High-Volume / High-Sat** | `health_beauty` | 8,803 | R$ 1,259,968.04 | R$ 143.13 | R$ 20.75 | 14.50% | **4.17** | 12.96% | 9.00% |
| **High-Volume / High-Sat** | `sports_leisure` | 7,685 | R$ 987,819.48 | R$ 128.54 | R$ 21.93 | 17.06% | **4.16** | 13.29% | 7.78% |
| **High-Volume / High-Sat** | `housewares` | 5,829 | R$ 635,149.98 | R$ 108.96 | R$ 25.13 | 23.06% | **4.14** | 13.42% | 7.01% |
| **High-Volume / High-Sat** | `cool_stuff` | 3,597 | R$ 634,415.95 | R$ 176.37 | R$ 23.33 | 13.23% | **4.17** | 12.57% | 6.90% |
| **High-Volume / High-Sat** | `garden_tools` | 3,480 | R$ 486,417.93 | R$ 139.78 | R$ 28.45 | 20.35% | **4.14** | 13.22% | 8.03% |
| **High-Volume / High-Sat** | `toys` | 3,863 | R$ 483,475.83 | R$ 125.16 | R$ 20.10 | 16.06% | **4.17** | 13.10% | 7.54% |
| **High-Volume / High-Sat** | `perfumery` | 3,149 | R$ 399,511.48 | R$ 126.87 | R$ 17.23 | 13.58% | **4.20** | 13.27% | 7.42% |
| **High-Volume / High-Sat** | `stationery` | 2,299 | R$ 232,080.79 | R$ 100.95 | R$ 20.46 | 20.26% | **4.24** | 11.61% | 7.77% |
| **High-Volume / High-Sat** | `pet_shop` | 1,703 | R$ 214,462.58 | R$ 125.93 | R$ 23.25 | 18.46% | **4.24** | 11.63% | 6.31% |
| **High-Volume / High-Sat** | `fashion_bags_acc` | 1,855 | R$ 152,842.65 | R$ 82.39 | R$ 16.99 | 20.62% | **4.18** | 11.97% | 6.68% |
| **High-Volume / High-Sat** | `luggage_acc` | 1,028 | R$ 140,387.92 | R$ 136.56 | R$ 29.59 | 21.66% | **4.33** | 9.14% | 5.53% |
| **High-Volume / Low-Sat** | `bed_bath_table` | 9,299 | R$ 1,031,939.54 | R$ 110.97 | R$ 21.95 | 19.78% | **3.96** | **17.08%** | 8.83% |
| **High-Volume / Low-Sat** | `watches_gifts` | 5,603 | R$ 1,203,090.21 | R$ 214.72 | R$ 17.99 | 8.38% | **4.05** | **15.51%** | 8.55% |
| **High-Volume / Low-Sat** | `computers_acc` | 6,661 | R$ 912,684.83 | R$ 137.02 | R$ 22.10 | 16.13% | **4.01** | **16.39%** | 7.74% |
| **High-Volume / Low-Sat** | `furniture_decor` | 6,351 | R$ 732,081.75 | R$ 115.27 | R$ 27.20 | 23.60% | **4.01** | **16.64%** | 8.57% |
| **High-Volume / Low-Sat** | `baby` | 2,840 | R$ 411,556.27 | R$ 144.91 | R$ 24.03 | 16.58% | **4.04** | **16.02%** | 9.26% |
| **High-Volume / Low-Sat** | `telephony` | 4,181 | R$ 323,217.86 | R$ 77.31 | R$ 17.02 | 22.02% | **4.00** | **15.69%** | 8.54% |
| **High-Volume / Low-Sat** | `office_furniture` | 1,264 | R$ 273,173.47 | R$ 216.12 | **R$ 53.98** | **24.98%** | **3.62** | **22.63%** | 9.24% |
| **High Delivery Risk** | `electronics` | 2,539 | R$ 160,861.70 | R$ 63.36 | R$ 18.46 | 29.14% | **4.08** | 14.26% | **9.86%** |
| **High Delivery Risk** | `home_confort` | 373 | R$ 57,993.91 | R$ 155.48 | R$ 23.11 | 14.86% | **3.92** | **18.23%** | **10.60%** |
| **High Delivery Risk** | `audio` | 348 | R$ 51,922.50 | R$ 149.20 | R$ 16.52 | 11.07% | **3.82** | **22.13%** | **13.01%** |
| **High Delivery Risk** | `food` | 445 | R$ 29,269.65 | R$ 65.77 | R$ 16.30 | 24.77% | **4.25** | 12.36% | **10.09%** |
| **High Delivery Risk** | `books_technical` | 259 | R$ 19,213.98 | R$ 74.19 | R$ 16.74 | 22.57% | **4.38** | 10.42% | **10.98%** |
| **High Delivery Risk** | `fashion_underwear` | 121 | R$ 9,541.55 | R$ 78.86 | R$ 15.84 | 20.08% | **3.91** | **19.01%** | **12.82%** |
| **High Delivery Risk** | `christmas_supplies`| 128 | R$ 8,816.82 | R$ 68.88 | R$ 25.27 | 36.69% | **4.04** | 13.28% | **9.60%** |

---

## 3. Detailed Findings & Strategic Takeaways

### A. High-Volume / High-Satisfaction (The Platform Growth Core)
- **`health_beauty`** ($N = 8,803$) is Olist’s single largest GMV generator (R$ 1.26M). It achieves a **4.17 star rating** with a low-rating rate of **12.96%** ($-2.08$ percentage points lower than baseline). Freight ratio is low ($14.50\%$), and lead times average 12.09 days.
- **`sports_leisure`** ($N = 7,685$) generates R$ 987.8K GMV with **4.16 stars** and a low late delivery rate of **7.78%**.
- **`luggage_accessories`** ($N = 1,028$) achieves the highest satisfaction among high-volume categories at **4.33 stars** and a low-rating rate of only **9.14%** ($-5.90$ percentage points lower than baseline).

### B. High-Volume / Low-Satisfaction (Friction Hotspots)
- **`bed_bath_table`** ($N = 9,299$) is Olist’s largest category by order count, generating R$ 1.03M GMV. However, it suffers from an average rating of **3.96 stars** and a high low-rating rate of **17.08%** ($1,588$ low-rated orders). This accounts for **10.61% of all low ratings across the entire marketplace**.
- **`watches_gifts`** ($N = 5,603$) generates R$ 1.20M GMV with an average price of R$ 214.72. Despite a low freight ratio ($8.38\%$), its low-rating rate reaches **15.51%** (869 low-rated orders), suggesting product quality or buyer expectation mismatch issues rather than shipping costs.
- **`furniture_decor`** ($N = 6,351$) and **`computers_accessories`** ($N = 6,661$) both register **4.01 stars** with low-rating rates of **16.64%** and **16.39%** respectively.

### C. The `office_furniture` Extreme Outlier
- **`office_furniture`** ($N = 1,264$, R$ 273.17K GMV) represents the single worst satisfaction failure on the platform:
  - **Average Review Score**: **3.62 stars** ($-0.45$ stars below baseline).
  - **Low-Rating Rate**: **22.63%** ($286$ low-rated orders out of 1,264; $+7.59$ percentage points above baseline).
  - **Average Freight Cost**: **R$ 53.98** (vs. R$ 22.82 baseline, a **$+136.5\%$ freight surcharge**).
  - **Average Lead Time**: **20.71 days** (vs. 12.50 days baseline, $+8.21$ extra delivery days).
  - **Root Cause Evidence**: Large dimensions and weight require specialized freight carriers, leading to transit delays and high shipping fees that destroy customer satisfaction.

### D. High Delivery Problem Categories (Logistics Risks)
- **`audio`** ($N = 348$): **13.01% late rate** (vs. 8.11% baseline) leads directly to a **22.13% low-rating rate** and **3.82 star average**.
- **`home_confort`** ($N = 373$): **10.60% late rate** drives an **18.23% low-rating rate** (3.92 stars).
- **`fashion_underwear_beach`** ($N = 121$): **12.82% late rate** drives a **19.01% low-rating rate** (3.91 stars).

### E. High-Ticket Niche Standouts
- **`computers`** ($N = 181$): Average price of **R$ 1,232.27** (vs. R$ 137.75 baseline, a $+794.6\%$ premium), generating R$ 223.0K GMV on few orders with a low freight ratio ($4.44\%$) and **4.14 star rating**.
- **`small_appliances`** ($N = 627$): Average price **R$ 302.48**, generating R$ 189.7K GMV with **4.15 stars**.
- **`books_general_interest`** ($N = 509$): Highest review score among medium categories at **4.46 stars** with a low-rating rate of only **8.25%**.

---

## 4. Visualizations & Analytical Artifacts

The following visual artifacts have been generated in `outputs/charts/`:
1. `q4_category_revenue_vs_review.png`: Scatter plot comparing GMV vs. Average Review Score across high-volume categories, highlighting `health_beauty` as the top winner and `bed_bath_table` / `office_furniture` as key friction zones.
2. `q4_category_freight_impact.png`: Bar plot comparing Average Freight Cost and Low-Rating Rates across priority categories, clearly exposing `office_furniture` and heavy categories.
3. `q4_priority_category_matrix.png`: 4-quadrant strategic priority matrix categorizing product categories for operational interventions.

---

## 5. Summary Table of Priority Segments

```
               [ Category Satisfaction vs. Delivery Performance Matrix ]

        High Review Score (>= 4.10)                Low Review Score (< 4.10)
  +-----------------------------------------+-----------------------------------------+
H | WINNERS:                                | FRICTION HOTSPOTS:                      |
i | - health_beauty (8,803 orders, 4.17*)   | - bed_bath_table (9,299 orders, 3.96*)  |
g | - sports_leisure (7,685 orders, 4.16*)  | - watches_gifts (5,603 orders, 4.05*)   |
h | - housewares (5,829 orders, 4.14*)      | - computers_acc (6,661 orders, 4.01*)   |
  | - cool_stuff (3,597 orders, 4.17*)      | - furniture_decor (6,351 orders, 4.01*) |
V | - toys (3,863 orders, 4.17*)            | - telephony (4,181 orders, 4.00*)      |
o | - perfumery (3,149 orders, 4.20*)       |                                         |
l | - pet_shop (1,703 orders, 4.24*)        | SEVERE OUTLIER:                         |
u | - luggage_acc (1,028 orders, 4.33*)     | - office_furniture (1,264 orders, 3.62*)|
m |                                         |   (Freight: R$53.98, Late Rate: 9.24%)   |
e |                                         |                                         |
  +-----------------------------------------+-----------------------------------------+
L | LOGISTICS RISKS:                        | HIGH FRICTION LOGISTICS RISKS:          |
o | - food (445 orders, 10.09% late)        | - audio (348 orders, 13.01% late, 3.82*)|
w | - books_technical (259 orders, 10.98%)  | - home_confort (373 orders, 10.60% late)|
  |                                         | - electronics (2,539 orders, 9.86% late)|
  +-----------------------------------------+-----------------------------------------+
```

---

## 6. Business Recommendations

1. **Targeted Operational Overhaul for `office_furniture`**:
   - Partner with specialized heavy-item logistics providers to reduce lead times from **20.71 days** down to the platform average of **12.50 days**.
   - Subsidize or restructure freight pricing (currently **R$ 53.98** per order) to mitigate sticker shock.
2. **Quality & Expectation Audit for `bed_bath_table` and `watches_gifts`**:
   - Conduct seller catalog audits for `bed_bath_table` to address non-delivery product quality issues driving **17.08% low ratings**.
   - Enforce stricter seller listing accuracy for `watches_gifts` to align buyer expectations.
3. **Logistics SLA Enforcement for Electronics & Audio Categories**:
   - Mandate priority seller dispatch SLAs for `electronics` and `audio` categories where late rates currently exceed **9.86% - 13.01%**.
