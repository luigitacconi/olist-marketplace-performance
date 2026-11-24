# Data quality — Olist Marketplace Performance

Measured on the downloaded files (2026-10-08; see `data_source_and_license.md`). Every number in this document is reproducible with the scripts in `Pandas_Analysis/` (`checks_structure_keys.py`, `checks_dates_amounts.py`, `checks_missing_values.py`, `checks_anomalies.py`, `checks_temporal_coverage.py`; run all of them together with `run_checks.py`). 
Raw files are never modified; every anomaly is either a single-indicator exclusion or is conserved and recorded here.

## 1. Structure and keys

- Seven tables used in the base analysis (orders, customers, order_items, order_payments, order_reviews, products, category_translation). Sellers and geolocation are kept as originals but out of scope.
- No exact duplicate rows in any table.
- Unique keys verified: `orders.order_id`, `customers.customer_id`, `products.product_id`, (`order_items.order_id`, `order_item_id`), (`order_payments.order_id`, `payment_sequential`), translation key.
- `customers.customer_unique_id` repeats by design (3,345 extra rows): these are repeat buyers, not an error.
- **`order_reviews.review_id` is not unique:** 789 ids appear on 1,603 rows, always across different orders and never as identical rows. Consequence: selecting one review per order is unaffected; `review_id` must not be used as a join key.
- Referential integrity: every order-based link matches — zero orphan rows in items→orders/products/sellers, payments→orders, reviews→orders, orders→customers.
- Reverse gaps: 775 orders without items, 1 without payments, 768 without reviews. These remain in the "observed orders" population and are handled by the population definitions, not by deletions.

## 2. Types, dates, amounts

- Identifiers are kept as text (never converted to numbers).
- Date conversion: 8 date columns with **0 failures**; purchase dates range 2016-09-04 → 2018-10-17.
- Amounts (BRL): all values have at most 2 decimals; sums use decimal values and are rounded to two decimals (totals: items 13,591,643.70; freight 2,251,909.54; payments 16,008,872.12).

## 3. Missing values

- `order_delivered_customer_date`: 2,965 missing — 2,957 of them are non-delivered orders; **8 are marked `delivered`** (see §4).
- `order_approved_at`: 160 missing — 141 `canceled` (approval date absent), 14 `delivered`, 5 `created`.
- Review comments are mostly empty (not used in the analysis); review scores are always present, range 1–5.
- `product_category_name`: 610 missing → labelled **`Unknown`** in the analysis.
- Rule: a missing value stays missing — it is never replaced by zero or by another date.

## 4. Anomalies (quantified and classified)

| Finding | Qty | Class | Rule / consequence |
|---|---|---|---|
| Carrier date before purchase | 166 | conserved | 164 are same-day inversions (likely time-of-day artifacts; cause not proven) → day-level comparisons only; carrier field unused in base. 2 truly earlier: noted. |
| Delivery before carrier | 23 | conserved | 3 same-day; 20 cross-day: noted; not used in base indicators. |
| Approval before purchase / delivery before purchase | 0 | — | clean |
| Negative prices / payments | 0 | — | clean |
| Zero freight | 383 | conserved | recorded value (e.g. free shipping), not an error |
| Zero payments | 9 | conserved | negligible; kept as recorded |
| Zero installments | 2 | conserved | both `credit_card`; flagged |
| Zero-weight products | 4 | conserved | weight not used in base analysis |
| `delivered` without delivery date | 8 | exclusion | excluded from evaluable deliveries only |
| `delivered` without approval date | 14 | conserved | approval date unused in base |
| Delivery date but status ≠ `delivered` | 6 | conserved | status governs: treated as not delivered |
| Shipping limit beyond 2018 | 4 (max 2020-04-09) | conserved | field unused in base |

## 5. Temporal coverage and main analysis period

- **2016 (ramp-up):** 329 orders in total — September 4, October 324, November none, December 1. Not usable for monthly comparisons.
- **Core (2017-01 → 2018-08):** 20 full months, 99,092 orders; delivered share between 92.9% (2017-02) and 98.9% (2018-06); clear volume peak in November 2017 (7,544 orders).
- **Tail (2018-09, 2018-10):** 20 orders in total, none delivered, all delivery dates missing — the data effectively stops in late August 2018.

**Main period used for all trend comparisons: 2017-01-01 → 2018-08-31 (99,092 orders).** The 2016 ramp-up and the 2018 tail stay in the dataset but are excluded from month-over-month and trend analysis. This document is the record of that decision.

## 6. Evidence

All checks ran locally on the raw files; the scripts are in `Pandas_Analysis/` and all checks run together with `Pandas_Analysis/run_checks.py`. No row was deleted or modified: `data/raw/` is immutable.
