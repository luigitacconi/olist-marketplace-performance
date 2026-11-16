-- create_tables.sql — analytical tables for the Olist project (DuckDB)
-- Grain: clean_orders = one row per order; clean_items = one row per item.

-- Items aggregated per order (temporary)
CREATE OR REPLACE TABLE temp_items_per_order AS
select
	order_id,
	COUNT(*) AS items_count,
	SUM(price) AS item_value_sum,
	SUM(freight_value) AS freight_sum,
	COUNT(*) FILTER (WHERE price IS NULL OR price < 0) AS invalid_price_count
from raw_order_items
group by order_id;

-- Payments aggregated per order (temporary)
CREATE OR REPLACE TABLE temp_payments_per_order AS
select
	order_id,
	COUNT(*) AS payments_count,
	SUM(payment_value) AS payment_value_sum
from raw_order_payments
group by order_id;

-- One review per order: most recent answer, then creation, then review_id (temporary)
CREATE OR REPLACE TABLE temp_review_per_order AS
select
	order_id,
	review_score,
	review_creation_date,
	review_answer_timestamp,
	reviews_count
from (
	select
		r.order_id,
		r.review_score,
		r.review_creation_date,
		r.review_answer_timestamp,
		COUNT(*) OVER (PARTITION BY r.order_id) AS reviews_count,
		ROW_NUMBER() OVER (
			PARTITION BY r.order_id
			ORDER BY r.review_answer_timestamp DESC NULLS LAST,
			         r.review_creation_date DESC NULLS LAST,
			         r.review_id DESC
		) AS position
	from raw_order_reviews as r
) as ranked
where position = 1;

-- One row per order: base order, customer state, aggregates, review, delivery indicators
CREATE OR REPLACE TABLE clean_orders AS
select
	o.order_id,
	o.customer_id,
	o.order_status,
	o.order_purchase_timestamp AS purchase_timestamp,
	o.order_estimated_delivery_date AS estimated_delivery_date,
	o.order_delivered_customer_date AS delivered_customer_date,
	c.customer_state,
	a.items_count,
	a.item_value_sum,
	a.freight_sum,
	a.invalid_price_count,
	p.payments_count,
	p.payment_value_sum,
	r.review_score,
	r.review_creation_date,
	r.review_answer_timestamp,
	r.reviews_count,
	DATE_SUB('day', o.order_purchase_timestamp, o.order_delivered_customer_date) AS delivery_days,
	CASE WHEN o.order_delivered_customer_date IS NULL OR o.order_estimated_delivery_date IS NULL THEN NULL
	     WHEN CAST(o.order_delivered_customer_date AS DATE) > CAST(o.order_estimated_delivery_date AS DATE) THEN TRUE
	     ELSE FALSE END AS is_late
from raw_orders as o
LEFT JOIN raw_customers as c ON c.customer_id = o.customer_id
LEFT JOIN temp_items_per_order as a ON a.order_id = o.order_id
LEFT JOIN temp_payments_per_order as p ON p.order_id = o.order_id
LEFT JOIN temp_review_per_order as r ON r.order_id = o.order_id;

-- One row per item: product category and destination state
CREATE OR REPLACE TABLE clean_items AS
select
	oi.order_id,
	oi.order_item_id,
	oi.product_id,
	oi.seller_id,
	oi.shipping_limit_date,
	oi.price,
	oi.freight_value,
	o.order_purchase_timestamp AS purchase_timestamp,
	o.order_status,
	c.customer_state,
	COALESCE(t.product_category_name_english, pr.product_category_name, 'Unknown') AS category
from raw_order_items as oi
LEFT JOIN raw_orders as o ON o.order_id = oi.order_id
LEFT JOIN raw_customers as c ON c.customer_id = o.customer_id
LEFT JOIN raw_products as pr ON pr.product_id = oi.product_id
LEFT JOIN raw_category_translation as t ON t.product_category_name = pr.product_category_name;

-- Verification: orders (one row per order)
SELECT
	COUNT(*) AS orders,
	COUNT(*) FILTER (WHERE order_status = 'delivered') AS delivered_orders,
	COUNT(*) FILTER (WHERE reviews_count IS NOT NULL) AS orders_with_review,
	ROUND(SUM(item_value_sum), 2) AS item_value,
	ROUND(SUM(freight_sum), 2) AS freight,
	ROUND(SUM(payment_value_sum), 2) AS payments
FROM clean_orders;

-- Verification: delivered orders in the main period
SELECT
	COUNT(*) AS delivered_orders,
	ROUND(SUM(item_value_sum), 2) AS delivered_value,
	COUNT(*) FILTER (WHERE is_late) AS late_deliveries
FROM clean_orders
WHERE order_status = 'delivered'
  AND STRFTIME(purchase_timestamp, '%Y-%m') BETWEEN '2017-01' AND '2018-08';

-- Verification: items (one row per item)
SELECT
	COUNT(*) AS items,
	COUNT(DISTINCT category) AS categories,
	ROUND(SUM(price), 2) AS item_value,
	ROUND(SUM(freight_value), 2) AS freight
FROM clean_items;

-- Temporary tables no longer needed
DROP TABLE IF EXISTS temp_items_per_order;
DROP TABLE IF EXISTS temp_payments_per_order;
DROP TABLE IF EXISTS temp_review_per_order;
