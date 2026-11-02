# Temporal coverage — reproduces section 5 of docs/data_quality.md

import pandas as pd

from files import load
from convert_dates import convert_dates


orders = load("olist_orders_dataset.csv")

orders = convert_dates(orders)
orders["month"] = orders["order_purchase_timestamp"].dt.strftime("%Y-%m")


def check_temporal_coverage(orders):
    orders_per_month = orders.groupby("month")["order_id"].count()

    print(f"orders 2016-09: {orders_per_month.get('2016-09', 0)}")
    print(f"orders 2016-10: {orders_per_month.get('2016-10', 0)}")
    print(f"orders 2016-11: {orders_per_month.get('2016-11', 0)}")
    print(f"orders 2016-12: {orders_per_month.get('2016-12', 0)}")

    period = orders[(orders["month"] >= "2017-01")
                    & (orders["month"] <= "2018-08")]
    print(f"orders in the main period: {len(period)}")

    delivered_per_month = period[period["order_status"] == "delivered"].groupby(
        "month")["order_id"].count()
    orders_period = period.groupby("month")["order_id"].count()
    share = (delivered_per_month / orders_period * 100).round(2)
    print(f"minimum delivered share in the period: {share.min()}")
    print(f"maximum delivered share in the period: {share.max()}")

    print(
        f"orders November 2017: {orders_per_month.get('2017-11', 0)}")

    tail = orders[orders["month"] >= "2018-09"]
    print(f"tail orders 2018-09/10: {len(tail)}")
    print(
        f"  of which delivered: {(tail['order_status'] == 'delivered').sum()}")
    print(
        f"  with missing delivery date: "
        f"{tail['order_delivered_customer_date'].isna().sum()}")


check_temporal_coverage(orders)
