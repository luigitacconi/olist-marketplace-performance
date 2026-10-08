# Methodology — Olist Marketplace Performance

> Status: draft (2026-10-06)

## Project overview

Independent portfolio project on the **Brazilian E-Commerce Public Dataset by Olist** (Kaggle): about 100,000 anonymized orders from 2016 to 2018, in several linked tables (orders, items, payments, reviews, products, customers). Tools: SQL, Python, Power BI.

## Simulated business brief

- **Recipient:** commercial and operations manager of a marketplace.
- **Context:** before the next planning cycle, they need a historical report to identify areas worth exploring.
- **Expected result:** a historical report that answers the three questions, with the data and steps behind every number.

### Three questions

1. **Sales** — How do order volume and merchandise value vary over time, across product categories and destination states?
2. **Service** — Where do late deliveries and long delivery times concentrate, also considering the number of orders involved?
3. **Experience** — What relationship can we observe between delivery punctuality and customer review scores, and what checks are needed before acting?

### Boundaries of the conclusions

- The value we report is the price of the items sold, not Olist's revenue: commissions and costs are not in the data.
- The shipping amount recorded on the order is not the real shipping cost.
- We do not calculate profit, ROI or savings.
- Late deliveries and low reviews may be linked, but the data cannot prove the delay is the cause.

## Data source

[Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) — CC BY-NC-SA 4.0.

## Data dictionary

Fields used in the analysis. Missing values verified on the downloaded files (2026-10-08).

| Field | Table | Meaning | Type | Missing values |
|---|---|---|---|---|
| order_id | orders | unique order identifier | text | none |
| customer_id | orders | links each order to its customer row | text | none |
| order_status | orders | order state (delivered, shipped, canceled, …) | text | none |
| order_purchase_timestamp | orders | when the customer placed the order | timestamp | none |
| order_delivered_customer_date | orders | when the order reached the customer | timestamp | 2,965 (mostly not delivered) |
| order_estimated_delivery_date | orders | delivery date promised to the customer | timestamp | none |
| customer_id | customers | order-level customer key (one per order) | text | none |
| customer_unique_id | customers | identifies the person across orders | text | none |
| customer_state | customers | destination state (two-letter code) | text | none |
| order_id | order_items | order the item belongs to | text | none |
| order_item_id | order_items | item number within the order (1, 2, 3, …) | integer | none |
| product_id | order_items | product sold | text | none |
| price | order_items | item price, shipping excluded (BRL) | decimal | none |
| freight_value | order_items | shipping amount recorded for the item (BRL) | decimal | none |
| order_id | order_payments | order that was paid | text | none |
| payment_value | order_payments | amount of this payment (BRL) | decimal | none |
| review_id | order_reviews | review identifier | text | none |
| order_id | order_reviews | order reviewed | text | none |
| review_score | order_reviews | score from 1 to 5 | integer | none |
| review_creation_date | order_reviews | date the review was created | date | none |
| review_answer_timestamp | order_reviews | when the review was answered | timestamp | none |
| product_id | products | product identifier | text | none |
| product_category_name | products | category name in Portuguese | text | 610 |
| product_category_name | translation | category key in Portuguese | text | none |
| product_category_name_english | translation | category name in English | text | none |
