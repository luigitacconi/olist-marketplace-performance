# Executive Summary — Olist Marketplace Performance

**Prepared for:** Commercial and Operations Leadership (simulated planning brief)  
**Project type:** Independent portfolio project  
**Dataset:** Brazilian E-Commerce Public Dataset by Olist (Kaggle, CC BY-NC-SA 4.0)  
**Main analysis window:** January 2017 – August 2018 (20 full months; **99,092** observed orders, **96,211** delivered orders, **BRL 13.18M** delivered merchandise value)

> The 2016 ramp-up (329 orders) and the Sep–Oct 2018 tail (20 orders, 0 delivered) remain in the raw data but are excluded from trend comparisons so every month reflects a complete, observable cohort (see [`data_quality.md`](data_quality.md)).

---

## Key Findings

### 1. Sales grew rapidly through 2017, stabilized in 2018, and concentrate heavily in top categories and states
- **Trajectory:** Delivered orders climbed from **750** in Jan 2017 (`BRL 111.8k`) to a peak of **7,289** in Nov 2017 (`BRL 987.8k`, `+62.8%` orders / `+52.4%` value MoM), dropped `-24.4%` in Dec 2017 (`5,513` orders), and then stabilized across Jan–Aug 2018 between **6,099 and 7,069 orders/month** (`BRL 826k–978k/month`).
- **Category concentration:** Out of **74** product categories, the top **8** account for **54.5%** of merchandise value, the top **10** account for **62.5%** (`BRL 8.23M`), and the top **18** reach **81.3%** (`BRL 10.72M`). `health_beauty` (`BRL 1.23M`, `9.3%`), `watches_gifts` (`BRL 1.16M`, `8.8%`), and `bed_bath_table` (`BRL 1.02M`, `7.8%`) lead the marketplace.
- **Geographic concentration:** **São Paulo (`SP`)** alone generates **38.4%** of delivered merchandise value (`BRL 5.06M`) and **42.0%** of delivered orders (`40,406`). Together, the top 3 states (`SP`, `RJ`, `MG`) generate **63.4%** of merchandise value, and the top 10 of 27 states account for **87.9%**.
- **Evidence:** [`01_monthly_sales.png`](../charts/images/01_monthly_sales.png), [`02_top_categories.png`](../charts/images/02_top_categories.png), [`03_sales_by_state.png`](../charts/images/03_sales_by_state.png), [`sales_analysis.py`](../Pandas_Analysis/sales_analysis.py), [`analysis.sql`](../sql_Analysis/analysis.sql) (queries 1, 2, 3, 6, 7).

### 2. Delivery delays average 6.8% overall, but spike sharply during peak periods and diverge across major states
- **Overall reliability & timing:** Across **96,203** evaluable deliveries (`8` delivered orders with missing delivery dates excluded), **6,531** arrived after the estimated calendar date (**6.79%**). Overall purchase-to-delivery time has a median of **10 days** and a 90th percentile of **23 days**; among late deliveries specifically, the median delay past the promised date is **7 days** (90th percentile **22 days**, with `879` delayed `16–30` days and `344` delayed `31+` days).
- **Temporal spikes:** Monthly late rates remained below `6.6%` for most of 2017, then spiked to **12.4%** in Nov 2017 (`904` late), **14.1%** in Feb 2018 (`926` late), and **19.0%** in Mar 2018 (`1,328` late), before falling to **1.2%** in Jun 2018 (`71` late).
- **State dispersion:** Among the **12 states with at least 1,000 deliveries**, late rates vary by more than 3× — from **4.1%** in `PR` (`n=4,903`), **4.5%** in `SP` (`n=40,399`), and **4.6%** in `MG` (`n=11,319`) up to **12.1%** in `RJ` (`n=12,310`, producing `1,495` late deliveries — the largest late volume outside `SP`), **12.2%** in `BA` (`n=3,253`), and **13.8%** in `CE` (`n=1,273`). Smaller states with at least `100` deliveries show even higher rates, including `AL` (`21.5%`, `n=396`) and `MA` (`17.5%`, `n=713`).
- **Evidence:** [`04_late_deliveries_by_month.png`](../charts/images/04_late_deliveries_by_month.png), [`05_late_deliveries_by_state.png`](../charts/images/05_late_deliveries_by_state.png), [`service_analysis.py`](../Pandas_Analysis/service_analysis.py) (state & monthly breakdowns), [`analysis.sql`](../sql_Analysis/analysis.sql) (queries 4, 8, 9, 10 — overall, monthly & delay buckets).

### 3. Late deliveries show much higher low-score rates — largely concentrated in surveys answered before delivery
- **Overall association:** Across **95,560** evaluable deliveries matched to one review per order (**99.3%** coverage), low review scores (1–2 stars) occur on **62.4%** of late orders (`3,981 / 6,378`; mean `2.27`) versus **9.2%** of on-time orders (`8,247 / 89,182`; mean `4.29`).
- **Geographic consistency:** This pattern holds in every single one of the **14 states** with at least `100` reviews in both groups: on-time low-score rates stay tightly between **8.6% and 11.3%**, whereas late low-score rates stay between **52.1%** (`PR`) and **73.1%** (`RJ`).
- **Pre-delivery answer effect:** Separating reviews by whether the customer answered *before* or *at/after* recorded delivery reveals a striking split. Among late orders reviewed **before delivery** (`n=4,471` of `6,378` reviewed late orders), **80.7%** give 1–2 stars. Among late orders reviewed **at or after delivery** (`n=1,907`), the low-score rate drops to **19.5%** (still roughly double the `9.2%` on-time baseline, `n=89,005`).
- **Evidence:** [`06_punctuality_vs_reviews.png`](../charts/images/06_punctuality_vs_reviews.png), [`experience_analysis.py`](../Pandas_Analysis/experience_analysis.py), [`analysis.sql`](../sql_Analysis/analysis.sql) (query 5).

---

## Priority Recommendations for the Next Planning Cycle

### Priority 1 — Audit delivery promises and carrier SLAs in high-impact corridors (starting with RJ and Northeast hubs)
- **Evidence:** `RJ` accounts for `13.3%` of merchandise value (`12,310` deliveries) yet experiences a `12.1%` late rate (`1,495` late deliveries — nearly 3× `SP`'s `4.5%`), while `BA` (`12.2%`, `n=3,253`) and `CE` (`13.8%`, `n=1,273`) also exceed the `6.8%` marketplace average. In parallel, peak-demand and early-2018 windows drove late rates up to `19.0%`.
- **Prudent interpretation:** High late rates can stem from either transit/carrier bottlenecks or overly optimistic promised dates (or both); historical order timestamps alone cannot isolate seller dispatch vs. carrier transit causes.
- **Action to test:** Run a targeted operational audit on `RJ`, `BA`, and `CE` lanes (and peak-period capacity planning) to split total delay into seller-dispatch lag vs. carrier-transit lag, and test buffer calibration on estimated delivery dates for slower lanes.
- **Verification metric:** Monthly late delivery rate and 90th-percentile delay days in target states (`RJ`, `BA`, `CE`), tracked alongside order conversion so wider delivery estimates do not silently depress demand.

### Priority 2 — Review survey timing and proactive delay communication for overdue shipments
- **Evidence:** `4,471` of `6,378` reviewed late deliveries were answered *before* the package arrived, and `80.7%` of those pre-delivery reviews were 1–2 stars — compared with `19.5%` when late orders were reviewed at or after delivery (`n=1,907`).
- **Prudent interpretation:** Customers receiving a satisfaction survey while their order is already overdue are likely scoring the anxiety and lack of visibility during the wait, not only the final product/service. Because this is observational data, changing survey timing alone cannot be assumed to eliminate underlying dissatisfaction.
- **Action to test:** Pilot (1) proactive status notifications when an order misses its carrier milestone or promised date, and (2) triggering the main satisfaction survey after confirmed delivery (while capturing in-transit delivery issues through a dedicated support flow).
- **Verification metric:** Share of reviews submitted before delivery, low-score rate (1–2 stars) on late orders post-delivery, and support-ticket volume on delayed orders.

---

## Boundaries & Additional Data Needed

- **Analytical boundaries:**
  - Reported values are **delivered item prices in BRL** (shipping excluded), not Olist's accounting revenue; commissions, discounts, returns, and operating costs are not in the dataset.
  - `freight_value` is a recorded shipping charge, not actual carrier cost or logistics margin. No profit, ROI, or realized savings are calculated.
  - Associations between late deliveries and low review scores are **observational** and do not prove causation.
  - Findings describe Olist's historical 2017–2018 marketplace window and should not be generalized directly to current e-commerce benchmarks.
- **Data needed before committing investment:**
  1. Carrier identifiers, route handoff scans, and seller-level SLA compliance logs (to separate seller dispatch vs. carrier transit delays).
  2. Full return, refund, cancellation-reason, and customer-support ticket records (to measure financial impact and distinguish delivery vs. product defects).
  3. Marketplace take-rates, carrier costs, and seller margin structures (to prioritize interventions by economic return).

---

*Supporting documentation: [`methodology.md`](methodology.md) · [`data_quality.md`](data_quality.md) · [`data_source_and_license.md`](data_source_and_license.md)*
