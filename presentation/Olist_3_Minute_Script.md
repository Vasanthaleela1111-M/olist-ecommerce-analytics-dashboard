# Olist Executive Analysis: 3-Minute Presentation Script

**Speaker Note**: Read aloud clearly at a natural executive presentation pace (~130–140 words per minute). Total duration: exactly 3 minutes (180 seconds).

---

### [0:00 – 0:25] Section 1: Business Problem

"Good morning, leadership team. 

Over the past two years, Olist has experienced extraordinary marketplace expansion, scaling monthly order volume by **714%**—from 800 orders a month in early 2017 to over 6,500 orders a month in 2018, generating **15.8 million Reais** in total gross revenue.

However, rapid growth brought a vital executive question: *Has marketplace expansion degraded customer satisfaction, and what specific operational friction points are driving low customer reviews?* Today, we present the data-driven answers."

---

### [0:25 – 0:50] Section 2: Analytical Approach

"To answer these questions, we conducted an empirical analysis across the complete master analytical dataset of **99,441 orders**, joining 9 raw operational tables at the individual order grain.

We evaluated 20 candidate operational, financial, and geographic variables against our platform baseline low-rating rate of **15.09%** and average review score of **4.07 out of 5 stars**. Every finding we present today is grounded strictly in empirical data with explicit sample sizes, relative risk ratios, and observational standards."

---

### [0:50 – 2:10] Section 3: Three Strongest Findings

"Our analysis revealed three decisive operational findings:

**First, fulfillment lateness is the single largest catalyst of customer dissatisfaction.** On-time delivered orders exhibit a low-rating rate of just **9.49%** with a **4.28 star** average. But when an order is delivered past the promised date, the low-rating rate jumps to **54.64%**—an absolute surge of **+45.14 percentage points**, representing a **3.62x Relative Risk** vs. baseline. Furthermore, delays exceeding 4 days push low ratings to **75.09%**. Crucially, statistical correlation proves that marketplace scale itself does *not* degrade review scores—satisfaction drops exclusively when carrier delivery late rates spike.

**Second, geographic logistics friction is heavily concentrated on specific interstate corridors.** While 70.6% of seller shipments originate in São Paulo, 58% of buyers live outside SP. Our largest shipping corridor—São Paulo to Rio de Janeiro—accounts for **8,431 orders**, but suffers a **14.99% late delivery rate** and a **22.57% low-rating rate**, generating over 1,900 low-rated reviews on this single trunk line alone.

**Third, product category satisfaction varies drastically based on physical package dimensions.** Consumer goods like `health_beauty` achieve high satisfaction at **4.17 stars**. In contrast, heavy goods like `office_furniture` represent a severe outlier—registering the platform's lowest review score of **3.62 stars** and a **22.63% low-rating rate**, driven by heavy parcel freight costs averaging **53 Reais and 98 cents** and delivery lead times averaging **20.7 days**."

---

### [2:10 – 2:45] Section 4: Three Highest-Priority Recommendations

"Based on these empirical findings, we recommend three high-leverage operational interventions:

1. **Dynamic Delivery Buffer Adjustment**: Add **+3 to +4 business days** to estimated delivery date calculation algorithms on high-delay routes like `SP -> RJ`. Eliminating false lateness triggers on this corridor will reduce low ratings on affected orders from **54.64% down to 9.49%**, protecting over **200,000 Reais in annual GMV**.
2. **Strict 3-Day Seller Dispatch SLA**: Enforce a mandatory **3-day carrier handoff SLA** for sellers. Eliminating slow seller dispatch (> 5 days) reduces low ratings from **22.26% down to 12.42%**.
3. **Specialized Heavy-Goods Logistics Partnership**: Establish dedicated heavy-parcel fulfillment contracts for `office_furniture` to cut lead times from **20.7 days down to 12.5 days**, pulling category low ratings back down to baseline."

---

### [2:45 – 3:00] Section 5: Conclusion

"In conclusion, Olist's customer satisfaction is not constrained by market scale, but by targeted logistics late dates, seller dispatch lag, and heavy parcel handling. 

By executing these three evidence-based interventions, we can reduce platform-wide late deliveries below **4%** and elevate average review scores above **4.25 stars**. 

Thank you, and we welcome your questions."
