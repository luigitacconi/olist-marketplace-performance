-- analysis.sql — analysis queries for the Olist project (DuckDB)
-- All analyses use delivered orders in the main period 2017-01..2018-08.

-- 1. Orders and item value per month
SELECT
	STRFTIME(purchase_timestamp, '%Y-%m') AS month,
	COUNT(*) AS orders,
	ROUND(SUM(item_value_sum), 2) AS item_value,
	ROUND(SUM(freight_sum), 2) AS freight,
	ROUND(SUM(item_value_sum) + SUM(freight_sum), 2) AS total_value
FROM clean_orders
WHERE order_status = 'delivered'
  AND STRFTIME(purchase_timestamp, '%Y-%m') BETWEEN '2017-01' AND '2018-08'
GROUP BY month
ORDER BY month;

-- 2. Categories by item value
SELECT
	category,
	ROUND(SUM(price), 2) AS item_value,
	ROUND(SUM(freight_value), 2) AS freight,
	ROUND(SUM(price) + SUM(freight_value), 2) AS total_value
FROM clean_items
WHERE order_status = 'delivered'
  AND STRFTIME(purchase_timestamp, '%Y-%m') BETWEEN '2017-01' AND '2018-08'
GROUP BY category
ORDER BY item_value DESC;

-- 3. States by volume and value
WITH state_values AS (
	SELECT
		customer_state,
		COUNT(*) AS orders,
		ROUND(SUM(item_value_sum), 2) AS item_value,
		ROUND(SUM(freight_sum), 2) AS freight,
		ROUND(SUM(item_value_sum) + SUM(freight_sum), 2) AS total_value
	FROM clean_orders
	WHERE order_status = 'delivered'
	  AND STRFTIME(purchase_timestamp, '%Y-%m') BETWEEN '2017-01' AND '2018-08'
	GROUP BY customer_state
)
SELECT
	customer_state,
	orders,
	item_value,
	freight,
	total_value,
	ROUND(orders * 100.0 / SUM(orders) OVER (), 2) AS orders_pct,
	ROUND(item_value * 100.0 / SUM(item_value) OVER (), 2) AS item_value_pct,
	ROUND(freight * 100.0 / SUM(freight) OVER (), 2) AS freight_pct
FROM state_values
ORDER BY item_value DESC;

-- 4. Delivery time and delay
WITH delivery_times AS (
	SELECT
		delivery_days,
		CAST(delivered_customer_date AS DATE) - CAST(estimated_delivery_date AS DATE) AS delay_days
	FROM clean_orders
	WHERE order_status = 'delivered'
	  AND delivered_customer_date IS NOT NULL
	  AND estimated_delivery_date IS NOT NULL
	  AND STRFTIME(purchase_timestamp, '%Y-%m') BETWEEN '2017-01' AND '2018-08'
)
SELECT
	COUNT(*) AS deliveries,
	ROUND(QUANTILE_CONT(delivery_days, 0.5), 2) AS median_delivery_days,
	ROUND(QUANTILE_CONT(delivery_days, 0.9), 2) AS p90_delivery_days,
	COUNT(*) FILTER (WHERE delay_days > 0) AS late_deliveries,
	ROUND(COUNT(*) FILTER (WHERE delay_days > 0) * 100.0 / COUNT(*), 2) AS late_pct,
	ROUND(QUANTILE_CONT(delay_days, 0.5), 2) AS median_days_vs_promised,
	ROUND(QUANTILE_CONT(delay_days, 0.9), 2) AS p90_days_vs_promised
FROM delivery_times;

-- 5. Review scores by punctuality and when the answer was sent
WITH reviewed AS (
    SELECT
        is_late,
        review_score,
        CASE
            WHEN review_answer_timestamp IS NULL THEN 'unknown_timing'
            WHEN review_answer_timestamp < delivered_customer_date THEN 'before_delivery'
            ELSE 'at_or_after_delivery'
        END AS answer_timing
    FROM clean_orders
    WHERE order_status = 'delivered'
      AND is_late IS NOT NULL
      AND review_score IS NOT NULL
      AND STRFTIME(purchase_timestamp, '%Y-%m') BETWEEN '2017-01' AND '2018-08'
),
review_counts AS (
    SELECT
        is_late,
        answer_timing,
        COUNT(*) AS reviews,
        COUNT(*) FILTER (WHERE review_score IN (1, 2)) AS low_scores
    FROM reviewed
    GROUP BY GROUPING SETS ((is_late), (is_late, answer_timing))
)
SELECT
    COALESCE(answer_timing, 'all') AS review_timing,
    CASE WHEN is_late THEN 'late' ELSE 'on_time' END AS punctuality,
    reviews,
    low_scores,
    ROUND(low_scores * 100.0 / reviews, 2) AS low_score_pct
FROM review_counts
ORDER BY review_timing, is_late;

-- 6. Month-over-month change of orders and item value
WITH monthly AS (
	SELECT
		STRFTIME(purchase_timestamp, '%Y-%m') AS month,
		COUNT(*) AS orders,
		ROUND(SUM(item_value_sum), 2) AS item_value
	FROM clean_orders
	WHERE order_status = 'delivered'
	  AND STRFTIME(purchase_timestamp, '%Y-%m') BETWEEN '2017-01' AND '2018-08'
	GROUP BY month
)
SELECT
	month,
	orders,
	orders - LAG(orders) OVER (ORDER BY month) AS orders_change,
	ROUND((orders - LAG(orders) OVER (ORDER BY month)) * 100.0
	      / NULLIF(LAG(orders) OVER (ORDER BY month), 0), 2) AS orders_change_pct,
	item_value,
	item_value - LAG(item_value) OVER (ORDER BY month) AS item_value_change,
	ROUND((item_value - LAG(item_value) OVER (ORDER BY month)) * 100.0
	      / NULLIF(LAG(item_value) OVER (ORDER BY month), 0), 2) AS item_value_change_pct
FROM monthly
ORDER BY month;

-- 7. Category ranking and cumulative share
WITH category_values AS (
	SELECT
		category,
		ROUND(SUM(price), 2) AS item_value
	FROM clean_items
	WHERE order_status = 'delivered'
	  AND STRFTIME(purchase_timestamp, '%Y-%m') BETWEEN '2017-01' AND '2018-08'
	GROUP BY category
)
SELECT
	RANK() OVER (ORDER BY item_value DESC) AS category_rank,
	category,
	item_value,
	SUM(item_value) OVER (ORDER BY item_value DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_value,
	ROUND(SUM(item_value) OVER (ORDER BY item_value DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
	      * 100.0 / SUM(item_value) OVER (), 2) AS cumulative_pct
FROM category_values
ORDER BY category_rank;

-- 8. Monthly punctuality
SELECT
	STRFTIME(purchase_timestamp, '%Y-%m') AS month,
	COUNT(*) AS deliveries,
	COUNT(is_late) AS evaluated_deliveries,
	COUNT(*) FILTER (WHERE is_late) AS late_deliveries,
	ROUND(COUNT(*) FILTER (WHERE is_late) * 100.0 / COUNT(is_late), 2) AS late_pct
FROM clean_orders
WHERE order_status = 'delivered'
  AND STRFTIME(purchase_timestamp, '%Y-%m') BETWEEN '2017-01' AND '2018-08'
GROUP BY month
ORDER BY month;

-- 9. Delay-days distribution among late deliveries
WITH late_deliveries AS (
	SELECT
		CAST(delivered_customer_date AS DATE) - CAST(estimated_delivery_date AS DATE) AS delay_days
	FROM clean_orders
	WHERE order_status = 'delivered'
	  AND delivered_customer_date IS NOT NULL
	  AND estimated_delivery_date IS NOT NULL
	  AND STRFTIME(purchase_timestamp, '%Y-%m') BETWEEN '2017-01' AND '2018-08'
)
SELECT
	COUNT(*) AS late_deliveries,
	ROUND(QUANTILE_CONT(delay_days, 0.5), 2) AS median_delay_days,
	ROUND(QUANTILE_CONT(delay_days, 0.9), 2) AS p90_delay_days,
	MAX(delay_days) AS max_delay_days
FROM late_deliveries
WHERE delay_days > 0;

-- 9b. Late deliveries by delay bucket
WITH late_deliveries AS (
	SELECT
		CAST(delivered_customer_date AS DATE) - CAST(estimated_delivery_date AS DATE) AS delay_days
	FROM clean_orders
	WHERE order_status = 'delivered'
	  AND delivered_customer_date IS NOT NULL
	  AND estimated_delivery_date IS NOT NULL
	  AND STRFTIME(purchase_timestamp, '%Y-%m') BETWEEN '2017-01' AND '2018-08'
)
SELECT
	CASE
		WHEN delay_days <= 3 THEN '1-3'
		WHEN delay_days <= 7 THEN '4-7'
		WHEN delay_days <= 15 THEN '8-15'
		WHEN delay_days <= 30 THEN '16-30'
		ELSE '31+'
	END AS delay_bucket,
	COUNT(*) AS deliveries,
	MIN(delay_days) AS min_delay
FROM late_deliveries
WHERE delay_days > 0
GROUP BY delay_bucket
ORDER BY min_delay;

-- Three observations for delivered orders placed from Jan 2017 through Aug 2018
-- 1. At least 8 of 74 categories are needed to reach 50% of merchandise value (54.52%).
--    The first 18 reach 81.29%, and the top 10 account for 62.47%.
--    Sao Paulo accounts for 38.36% of merchandise value and 42.00% of orders.
-- 2. The late share is 6.79% overall, 18.96% in Mar 2018 and 1.16% in Jun 2018.
--    Low scores are 62.42% for late orders and 9.25% for on-time orders across all reviews.
--    Within late orders, the share is 80.74% before delivery and 19.45% at or after delivery.
-- 3. Delivered orders rose from 750 in Jan 2017 to 6,099-7,069 per month in Jan-Aug 2018.
--    The Nov 2017 peak (7,289 orders, +62.77% vs Oct) was followed by a 24.37% fall in Dec.
