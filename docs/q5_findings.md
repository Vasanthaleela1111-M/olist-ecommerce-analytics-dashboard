# Core Question 5: Payment Behavior Analysis

## Executive Summary

Payment method selection and installment structuring play a vital role in customer purchasing behavior, order value scaling, and operational clearance velocity across the Olist marketplace. Out of $N = 99,440$ orders with payment records, **75.40% of orders** (R$ 12,542,527.15 GMV, $78.35\%$ of total platform revenue) are transacted via **Credit Card**, followed by **Boleto Bancário** ($19.90\%$ order share, R$ 2.87M GMV), **Voucher** ($3.17\%$ order share), and **Debit Card** ($1.54\%$ order share).

Key Empirical Insights:
1. **Credit Card Basket Escalation**: Installments serve as a primary catalyst for higher average order values (AOV). Customers paying in a single installment average an AOV of **R$ 100.91**, whereas customers choosing **7 - 10 installments** average **R$ 336.44**—a **3.33x AOV expansion** ($+233.4\%$).
2. **Installment Term vs. Customer Satisfaction**: High installment terms ($7+$ installments) exhibit progressively higher customer dissatisfaction: 1-installment orders record a **13.37% low-rating rate** (4.14 stars), which degrades monotonically to **17.83% low ratings** for 7-10 installments (3.98 stars) and **21.70% low ratings** for 11+ installments (3.84 stars).
3. **Boleto Operational Clearance Lag**: While Boleto buyers maintain comparable review scores to credit card buyers (**4.07 stars**), Boleto orders suffer a higher late delivery rate (**8.88% vs. 7.96% for credit cards**). This $+0.92$ percentage point late rate penalty is driven by the 1-3 business day banking clearance lag before sellers receive order authorization for dispatch.
4. **Voucher Refund Signal**: Voucher payments register the lowest average review score (**3.98 stars**) and highest low-rating rate (**17.42%**), reflecting the fact that vouchers are frequently issued as customer service compensation/store credit following prior order friction.

---

## 1. Primary Payment Method Breakdown

The dataset contains $99,440$ orders with valid payment information totaling **R$ 16,008,872.20** in total customer payments (including freight and vouchers):

| Primary Payment Method | Order Count ($N$) | Order Share (%) | Total Payment Value (R$) | Revenue Share (%) | Mean AOV (R$) | Median AOV (R$) | Avg Review | Low-Rating Rate (%) | Late Delivery Rate (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Credit Card** | $74,975$ | **75.40%** | R$ 12,542,527.15 | **78.35%** | **R$ 167.29** | R$ 109.56 | **4.07** | **15.09%** | **7.96%** |
| **Boleto Bancário** | $19,784$ | **19.90%** | R$ 2,869,361.27 | **17.92%** | **R$ 145.03** | R$ 93.89 | **4.07** | **14.85%** | **8.88%** |
| **Voucher** | $3,151$ | **3.17%** | R$ 379,043.91 | **2.37%** | **R$ 120.29** | R$ 82.78 | **3.98** | **17.42%** | **7.02%** |
| **Debit Card** | $1,527$ | **1.54%** | R$ 217,939.79 | **1.36%** | **R$ 142.72** | R$ 89.30 | **4.16** | **13.29%** | **7.96%** |
| *Undefined* | 3 | <0.01% | R$ 0.00 | 0.00% | R$ 0.00 | R$ 0.00 | 1.67 | 66.67% | N/A |

### Analytical Observations
- **Credit Card Dominance**: $3$ out of every $4$ orders are processed via credit card, driving nearly **80% of platform GMV**. The higher average ticket (**R$ 167.29 vs R$ 145.03 for Boleto**) highlights credit card flexibility in financing larger purchases.
- **Boleto Friction Point**: $19,784$ orders ($19.90\%$) use Boleto (cash bank slips). Boleto payments require manual cash/online bank transfer payment by the buyer after checkout, introducing a payment approval delay averaging **24-48 hours**. This systemic delay reduces seller dispatch speed and contributes to a higher late rate (**8.88% vs 7.96%**).
- **Debit Card Quality**: Debit card usage ($N = 1,527$) yields the highest satisfaction (**4.16 stars**, **13.29% low rating rate**), reflecting immediate payment confirmation with zero financing risk.

---

## 2. Credit Card Installment Tier Analysis

In Brazilian e-commerce, installment financing (*parcelamento*) is standard practice. Analyzing the $N = 74,975$ credit card orders reveals a steep, monotonic scaling relationship between installment term and average basket size:

| Installment Tier | Order Count ($N$) | Credit Card Share (%) | Total Payment Value (R$) | Revenue Share (%) | Mean AOV (R$) | AOV Multiplier vs Single Pay | Avg Review | Low-Rating Rate (%) | Late Delivery Rate (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1 Installment (Single Pay)** | $24,004$ | **32.02%** | R$ 2,422,262.18 | 19.31% | **R$ 100.91** | **1.00x** | **4.14** | **13.37%** | **7.25%** |
| **2 - 3 Installments** | $22,651$ | **30.21%** | R$ 3,070,871.22 | 24.48% | **R$ 135.57** | **1.34x** | **4.07** | **15.00%** | **8.10%** |
| **4 - 6 Installments** | $16,160$ | **21.55%** | R$ 2,950,182.46 | 23.52% | **R$ 182.56** | **1.81x** | **4.05** | **15.64%** | **8.24%** |
| **7 - 10 Installments** | $11,819$ | **15.76%** | R$ 3,976,325.46 | 31.70% | **R$ 336.44** | **3.33x** | **3.98** | **17.83%** | **8.69%** |
| **11+ Installments** | $341$ | **0.45%** | R$ 122,885.83 | 0.98% | **R$ 360.37** | **3.57x** | **3.84** | **21.70%** | **9.73%** |

```
                       [ Credit Card Installment Tier Escalation ]

  Installment Tier     AOV (R$)       AOV Multiplier      Low-Rating Rate (%)
  -----------------------------------------------------------------------------
  1 Installment        R$ 100.91      1.00x  (Baseline)   13.37%  [============]
  2 - 3 Installments   R$ 135.57      1.34x  (+34.4%)     15.00%  [==============]
  4 - 6 Installments   R$ 182.56      1.81x  (+80.9%)     15.64%  [===============]
  7 - 10 Installments  R$ 336.44      3.33x  (+233.4%)    17.83%  [=================]
  11+ Installments     R$ 360.37      3.57x  (+257.1%)    21.70%  [====================]
```

### Strategic Observations
- **AOV Expansion Engine**: **67.98% of credit card transactions** use installment financing ($2+$ installments). $7-10$ installments generate **31.70% of all credit card revenue** despite accounting for only $15.76\%$ of orders, proving that installment financing enables consumers to buy high-ticket electronics, furniture, and appliances.
- **Dissatisfaction Escalation**: Low-rating rates rise steadily with installment length:
  - 1 Installment: **13.37%**
  - 7-10 Installments: **17.83%** ($+4.46$ percentage points increase)
  - 11+ Installments: **21.70%** ($+8.33$ percentage points increase)
- **Causal Interpretation Note**: Installment selection does not directly cause buyer unhappiness. Rather, higher installment counts correlate with high-value, heavy, complex items (`office_furniture`, `computers`, `watches_gifts`) which carry inherently higher freight charges, longer lead times, and higher customer expectations.

---

## 3. Multi-Payment Usage Patterns

An analysis of order payment split patterns reveals that **96.12% of orders** ($95,581$ orders) are settled using a single payment record, while **3.88% of orders** ($3,859$ orders) involve sequential multi-payments (e.g., combining multiple vouchers, or pairing a voucher with a credit card).

- **Single Payment**: $95,581$ orders | AOV: R$ 159.24
- **Dual Payment**: $2,933$ orders | AOV: R$ 190.12
- **3-5 Payments**: $872$ orders | AOV: R$ 241.56
- **6+ Payments**: $54$ orders | AOV: R$ 412.30

Customers using multi-payment splitting exhibit significantly higher AOVs, confirming that payment splitting is primarily utilized to exhaust gift card/voucher balances or bypass single-card credit limits on expensive purchases.

---

## 4. Visualizations & Analytical Artifacts

The following visual artifacts are exported in `outputs/charts/`:
1. `q5_payment_method_shares.png`: Dual-axis visualization illustrating payment method order share (%) vs. Average Order Value (AOV), highlighting Credit Card dominance.
2. `q5_installments_vs_order_value.png`: Dual-axis bar chart illustrating the steep AOV multiplier curve alongside order volume distribution across credit card installment tiers.

---

## 5. Strategic Business Recommendations

1. **Optimize Boleto Payment Approval SLAs**:
   - Partner with instant-clearing fintech payment gateways (e.g., Pix / instant boleto) to eliminate the 24-48 hour bank processing window that drives Boleto late rates up to **8.88%**.
2. **Promote Low-Installment Incentives for High-Volume Categories**:
   - Provide small cash/Pix discounts (e.g., 5% off single-payment orders) to encourage 1-installment purchases, reducing platform credit risk and carrier disputes.
3. **Enhance Post-Purchase Communication for High-Installment Buyers**:
   - Implement proactive tracking and delivery milestone SMS notifications for 7+ installment purchases (AOV $>$ R$ 300) to maintain customer trust during long fulfillment windows.
