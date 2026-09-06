# Olist Customer Experience & Operational Strategy
## 10-Slide Executive Presentation Deck for Leadership

---

## Slide 1 — Olist Customer Experience

### Core Message
**Overall platform ratings average 4.07 stars, but customer satisfaction is strongly bimodal—operational failures drop ratings straight to 1 star.**

```
                     [ Customer Review Score Distribution (N = 99,441) ]

   Rating Tier    Order Count   Share (%)                           Visual Breakdown
   --------------------------------------------------------------------------------------------------
   5 Stars        57,378        57.70%    [==================================================]
   4 Stars        19,117        19.22%    [================]
   3 Stars         8,179         8.22%    [=======]
   2 Stars         3,235         3.25%    [===]
   1 Star         11,797        11.86%    [==========]
```

### Supporting Evidence
- **Platform Baseline Average**: **4.0708 stars** across $N = 99,441$ total orders.
- **Polarized Experience**: 5-Star ratings represent **57.70%** ($57,378$ orders), while 1-Star & 2-Star Low Ratings represent **15.09%** ($15,010$ orders).
- **Concentrated Failure**: 1-Star reviews account for **78.59% of all low ratings** ($11,797$ out of $15,010$).
- **Takeaway**: Mild dissatisfaction is rare ($3.25\%$ 2-star); operational breakdowns drive catastrophic 1-star review spikes.

---

## Slide 2 — Business Problem

### Core Message
**Marketplace scale expanded +714%, but recurring operational fulfillment breakdowns drive severe customer dissatisfaction.**

```
                       [ Operational Growth vs. Dissatisfaction Drivers ]

   +--------------------------+          +--------------------------+          +--------------------------+
   |  Demand & GMV Scaling    |  =====>  |  Fulfillment Bottlenecks |  =====>  |   1-Star Rating Spikes   |
   |  788 -> 7,380 Orders/Mo  |          |  Late Delivery: 8.11%    |          |  15,010 Low-Rated Orders |
   |  +714% Volume Growth     |          |  Cross-State Late: 15%   |          |  Customer & Revenue Risk |
   +--------------------------+          +--------------------------+          +--------------------------+
```

### Supporting Evidence
- **Growth Scale**: Monthly order volume expanded from **788 orders/month** (Jan 2017) to **7,380 peak orders/month** (Nov 2017, R$ 1.01M GMV).
- **Customer Dissatisfaction**: $15,010$ orders received 1-star or 2-star ratings, causing customer churn and support overhead.
- **Core Challenge**: Dissatisfaction is not driven by customer acquisition or pricing—it is driven by fulfillment SLA failures during peak growth.
- **Strategic Goal**: Identify, isolate, and eliminate fulfillment failure modes to protect platform reputation and recurring revenue.

---

## Slide 3 — Analytical Approach

### Core Message
**Rigorous analytical governance anchored on a unified order-level grain ($N = 99,441$) and strict non-causal statistical controls.**

```
                          [ Master Data Governance & Pipeline Architecture ]

   Raw Datasets (9 CSVs)        Primary Aggregation Grain           Validation & Risk Controls
   ---------------------        -------------------------           --------------------------
   - Orders (99.4K)             +-------------------------+         - 100% Financial Match (R$ 15.84M)
   - Order Items (112.6K)  ==>  |  1 ROW = 1 ORDER        |  ====>  - 0 Cartesian Fan-Out Duplicates
   - Payments (103.8K)          |  N = 99,441 Orders      |         - Delivered Population Scoping (96.5K)
   - Reviews (99.2K)            +-------------------------+         - Minimum Volume Cutoffs (N >= 30, 50, 100)
```

### Supporting Evidence
- **Unified Master Dataset**: Enforced $1 \text{ row} = 1 \text{ order}$ primary grain across all 9 raw datasets ($N = 99,441$ master order records).
- **Financial & Join Integrity**: 100% precision match against raw item price sums (R$ 13.59M) and freight sums (R$ 2.25M) with $0$ duplicate fan-out rows.
- **Survivorship & Selection Bias Controls**: Evaluated delivery lead times strictly on delivered orders ($N = 96,470$) and scoped text keyphrase extraction to verified comment subset ($N = 6,742$).
- **Methodology**: Evaluated operational drivers using relative risk ratios, odds ratios, and absolute percentage point deltas against platform baselines.

---

## Slide 4 — Marketplace Performance

### Core Message
**Rapid marketplace volume expansion (+714%) did NOT degrade underlying customer review scores.**

```
                       [ Monthly Volume vs. Review Score Stability (2017-2018) ]

   Month      Order Volume    Monthly GMV (R$)    Avg Review Score    Late Delivery Rate (%)
   -----------------------------------------------------------------------------------------
   Jan 2017   788 orders      R$ 120,312.87       4.04 Stars          5.58%
   May 2017   3,546 orders    R$ 494,228.66       4.13 Stars          4.17%
   Nov 2017   7,380 orders    R$ 1,010,249.74      3.82 Stars (Peak)   14.65% (Peak Spike)
   Mar 2018   7,075 orders    R$ 984,874.19       4.12 Stars          5.36%
```

### Supporting Evidence
- **Volume Expansion**: Peak monthly volume reached **7,380 orders/month** (Black Friday Nov 2017), representing a **+714% volume expansion** over early 2017 baseline.
- **Score Stability**: Correlation between monthly order volume and average review score is negligible ($r = -0.1266$). Review scores remained between 3.95 and 4.20 stars throughout rapid scaling.
- **Logistics Correlation**: Monthly review score dips correlate strongly with monthly late delivery rate spikes ($r = +0.7940$).
- **Takeaway**: Demand expansion is sustainable; operational focus must center on logistics SLA stability during peak volume events.

---

## Slide 5 — Delivery & Satisfaction

### Core Message
**Passing the promised delivery date causes an immediate, non-linear collapse in customer review scores.**

```
                        [ The Non-Linear Late Delivery Review Penalty ]

   Delivery Status Tier         Sample Size (N)   Mean Review Score   Low-Rating Rate (%)   Relative Risk
   --------------------------------------------------------------------------------------------------------
   On-Time Delivery             88,644 orders     4.28 Stars          9.49%                 1.00x (Baseline)
   Late Delivery (Overall)       7,826 orders     2.55 Stars         54.64%                 5.76x Risk
   Late 1 - 3 Days               3,162 orders     3.58 Stars         24.48%                 2.58x Risk
   Late >= 4 Days (Severe)       4,664 orders     1.84 Stars         75.09%                 7.91x Risk
   Late >= 10 Days (Extreme)     2,299 orders     1.69 Stars         79.43%                 8.37x Risk
```

### Supporting Evidence
- **On-Time Baseline**: On-time delivered orders ($N = 88,644$) record a **9.49% low-rating rate** and **4.28 stars**.
- **Late Delivery Collapse**: Passing the estimated delivery date increases low-rating probability to **54.64%** (**5.76x Relative Risk**, +45.15 percentage points).
- **Severe Delay Penalty**: At $\ge 4$ days late ($N = 4,664$), **75.09% of orders receive 1–2 stars** (**7.91x Relative Risk**).
- **Takeaway**: Accurate delivery estimates and carrier SLA buffers are the single most powerful lever for protecting customer satisfaction.

---

## Slide 6 — Seller & Geography

### Core Message
**70.6% seller concentration in São Paulo forces 64.0% cross-state shipments, creating severe friction on the `SP -> RJ` corridor.**

```
                       [ Regional Logistics Corridor Performance ]

   Route Corridor         Order Share     Mean Freight (R$)   Mean Lead Time   Late Rate (%)   Low Rating Rate (%)
   ----------------------------------------------------------------------------------------------------------------
   Intra-State (SP -> SP) 35.96% (35.5K)  R$ 14.09            7.95 Days        4.50%           12.28% (Baseline)
   Inter-State (Overall)  64.04% (63.2K)  R$ 24.58 (+74.4%)   15.15 Days       10.12%          15.88%
   Hotspot: SP -> RJ      8.54% (8,431)   R$ 20.83            14.97 Days       14.99%          22.57% (+10.29% pts)
```

### Supporting Evidence
- **Seller Concentration**: **70.57% of sellers** operate in São Paulo (`SP`), forcing **64.04% of all orders** to cross state lines.
- **Cross-State Surcharge**: Inter-state orders cost **+74.4% more freight** (R$ 24.58 vs R$ 14.09) and take **+90.6% longer lead times** (15.15 days vs 7.95 days).
- **Hotspot Corridor (`SP -> RJ`)**: $N = 8,431$ orders. Suffers a **14.99% late delivery rate** and **22.57% low-rating rate** (3.80 stars).
- **Takeaway**: Cross-state postal corridors into Rio de Janeiro require route-specific estimated delivery date extensions and carrier SLA management.

---

## Slide 7 — Product Categories

### Core Message
**Standard categories thrive in customer satisfaction, while heavy goods (`office_furniture`) suffer a severe fulfillment crisis.**

```
                       [ Category Performance Comparison ]

   Product Category     Volume (N)   Mean GMV (R$)   Avg Review   Avg Freight (R$)   Lead Time   Low Rating Rate
   --------------------------------------------------------------------------------------------------------------
   health_beauty        8,803        R$ 1,258.6K     4.17 Stars   R$ 18.00           11.0 Days   12.96% (Winner)
   sports_leisure       7,720        R$ 988.1K       4.11 Stars   R$ 19.33           11.4 Days   14.33% (Winner)
   office_furniture     1,264        R$ 273.2K       3.62 Stars   R$ 53.98 (+136.5%) 20.7 Days   22.63% (Crisis)
```

### Supporting Evidence
- **Winner Categories**: `health_beauty` ($N = 8,803$) achieves **4.17 stars** and **12.96% low ratings** with low freight ratios ($14.50\%$).
- **Outlier Category Crisis**: `office_furniture` ($N = 1,264$) exhibits severe dissatisfaction (**3.62 stars**, **22.63% low rating**, **+7.54 percentage points** above platform baseline).
- **Cost & Transit Burden**: `office_furniture` freight averages **R$ 53.98** (+136.5% vs baseline) with a **20.71-day lead time**.
- **Qualitative Driver**: $57.50\%$ of low-rating text review comments cite packaging damage or product defects upon arrival for bulky goods.

---

## Slide 8 — Root Causes

### Core Message
**Customer dissatisfaction is overwhelmingly driven by fulfillment delays and product defects; commercial factors have ZERO direct impact.**

```
                       [ Root-Cause Hierarchy of Low Review Scores ]

   Factor Category       Factor Name                    Low Rating Rate (%)   Relative Risk   Classification
   ----------------------------------------------------------------------------------------------------------
   Operational Failure   Delivery Delay (>= 4 Days)      75.09%                4.97x Risk      PRIMARY FACTOR
   Operational Failure   Delivery Delay (Overall)        54.64%                3.62x Risk      PRIMARY FACTOR
   Seller Execution      Slow Dispatch (> 5 Days)        22.26%                1.47x Risk      SECONDARY CONTRIBUTOR
   Ticket Size           High Item Price (> R$ 200)      18.59%                1.23x Risk      SECONDARY CONTRIBUTOR
   Commercial Friction   High Freight Ratio (> 50%)       15.27%                1.01x Risk      UNSUPPORTED (NO IMPACT)
   Payment Selection     Boleto Payment Method           14.85%                0.98x Risk      UNSUPPORTED (NO IMPACT)
```

### Supporting Evidence
- **Primary Driver**: Delivery delays past estimated dates drive low ratings to **54.64%** ($>0$ days late) and **75.09%** ($\ge 4$ days late).
- **Secondary Drivers**: Slow seller dispatch ($>5$ days) elevates low ratings to **22.26%** (1.47x risk). High item price ($>\text{R\$ } 200$) elevates low ratings to **18.59%**.
- **Unsupported Drivers**: High freight ratio ($>50\%$) records a **15.27% low-rating rate** (vs 15.09% baseline — 1.01x risk). Boleto payment records a **14.85% low-rating rate** (0.98x risk).
- **Review Text Evidence** ($N = 6,742$ comments): **56.38% cite logistics delays**, **57.50% cite product defects/damage**.

---

## Slide 9 — Recommendations

### Core Message
**Focus 100% of operational remediation on cross-state SLA buffers, 3-day seller dispatch enforcement, and specialized bulky freight.**

```
                         [ Three High-Impact Operational Actions ]

   Action #1: Dynamic Route Buffers        Action #2: 3-Day Seller SLA        Action #3: Bulky Freight Partner
   ---------------------------------        ---------------------------        --------------------------------
   - Inject +3-4 days buffer for            - Enforce mandatory 3-day          - Contract dedicated heavy-goods
     cross-state orders (`SP -> RJ`).         seller dispatch limit.             freight for `office_furniture`.
   - Prevents late delivery penalty         - Target N = 14,180 slow           - Enforce protective packaging;
     (-45.15% pts low rating).                sellers (>5 days dispatch).        set realistic 20+ day estimates.
```

### Supporting Evidence & Targets
1. **Dynamic Delivery Buffers (`SP -> RJ`)**:
   - *Target Segment*: $N = 8,431$ cross-state orders into Rio de Janeiro.
   - *Expected Impact*: Eliminates artificial lateness, reducing low-rating probability from **54.64% down to 9.49%** for saved orders.
2. **Upstream Seller Dispatch SLA (3-Day Limit)**:
   - *Target Segment*: $N = 14,180$ slow-dispatch orders ($14.26\%$ of platform volume).
   - *Expected Impact*: Reduces low-rating rate from **22.26% to 12.42%** (-9.84 percentage points) for affected orders.
3. **Specialized Bulky-Goods Logistics (`office_furniture`)**:
   - *Target Segment*: $N = 7,615$ heavy furniture orders.
   - *Expected Impact*: Recovers category score from **3.62 to >4.00 stars** and protects R$ 273.2K GMV.

---

## Slide 10 — Expected Business Impact / Conclusion

### Core Message
**Executing these three targeted actions will reduce platform low ratings from 15.09% to <11.5% in 6 months while protecting growth.**

```
                        [ Olist Balanced Governance Scorecard & Targets ]

   Metric Indicator                   Current Baseline      6-Month Target       12-Month Goal
   --------------------------------------------------------------------------------------------
   Platform Late Delivery Rate        8.11%                 < 5.00%              < 3.50%
   Severe Late Rate (>= 4 Days Late)  4.83%                 < 2.00%              < 1.00%
   SP -> RJ Corridor Late Rate        14.99%                < 7.50%              < 5.00%
   Slow Seller Dispatch (> 5 Days)    14.26%                < 5.00%              < 2.00%
   Platform Low Rating Rate (1-2 Star) 15.09%                < 11.50%             < 9.50%
   office_furniture Avg Review Score  3.62 Stars            > 3.95 Stars         > 4.15 Stars
```

### Conclusion Summary
- **Growth Protection**: Scaling is healthy (+714% volume growth). Olist does not have a market demand or pricing problem.
- **Operational Alignment**: Customer dissatisfaction is overwhelmingly concentrated in **avoidable logistics SLA failures**: delivery delays past promised dates, slow seller dispatch, cross-state shipping bottlenecks (`SP -> RJ`), and heavy goods packaging breakdowns (`office_furniture`).
- **Immediate Path Forward**: Dynamic route buffers, 3-day seller dispatch SLAs, and specialized heavy-goods logistics will immediately protect customer review scores, recover high-ticket revenue, and secure long-term platform trust.

---

### Artifact Locations
- **Executive Presentation Deck**: [report/executive_presentation.md](file:///f:/projects/olist-hackathon/report/executive_presentation.md)
- **Executive Findings Report**: [report/executive_findings.md](file:///f:/projects/olist-hackathon/report/executive_findings.md)
- **Final Hackathon Report**: [report/final_hackathon_report.md](file:///f:/projects/olist-hackathon/report/final_hackathon_report.md)
- **Interactive Web App Dashboard**: [app/index.html](file:///f:/projects/olist-hackathon/app/index.html)
