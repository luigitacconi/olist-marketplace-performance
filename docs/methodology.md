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
