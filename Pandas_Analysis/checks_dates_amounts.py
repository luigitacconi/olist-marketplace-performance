# Types, dates, amounts — reproduces section 2 of docs/data_quality.md

import pandas as pd

from files import load
from convert_dates import convert_dates, date_columns_to_convert


orders = load("olist_orders_dataset.csv")
order_items = load("olist_order_items_dataset.csv")
order_payments = load("olist_order_payments_dataset.csv")
order_reviews = load("olist_order_reviews_dataset.csv")


RAW_TABLES = {
    "orders": orders,
    "order_items": order_items,
    "order_payments": order_payments,
    "order_reviews": order_reviews
}


def check_date_convertibility(tables):
    total_failures = 0
    for table_name, table in tables.items():
        for column_name in date_columns_to_convert:
            if column_name in table.columns:
                original = table[column_name]
                converted = pd.to_datetime(original, errors="coerce")
                failures = original.notna().sum() - converted.notna().sum()
                total_failures += failures
                print(f"{table_name}.{column_name}: date conversion failures: {failures}")
    print(f"total date conversion failures: {total_failures}")


def check_purchase_period(orders):
    first = orders["order_purchase_timestamp"].min().date()
    last = orders["order_purchase_timestamp"].max().date()
    print(f"first purchase date: {first}")
    print(f"last purchase date: {last}")


def check_decimals(table, column_name):
    over_two = (table[column_name].round(2) != table[column_name]).sum()
    print(f"{column_name}: {over_two} values with more than 2 decimals")


def check_total(series, description):
    total = series.sum()
    print(f"total {description}: {total:.2f}")


check_date_convertibility(RAW_TABLES)

orders = convert_dates(orders)
order_items = convert_dates(order_items)
order_reviews = convert_dates(order_reviews)
orders["month"] = orders["order_purchase_timestamp"].dt.strftime("%Y-%m")

check_purchase_period(orders)
check_decimals(order_items, "price")
check_decimals(order_items, "freight_value")
check_decimals(order_payments, "payment_value")
check_total(order_items["price"], "prices")
check_total(order_items["freight_value"], "freight")
check_total(order_payments["payment_value"], "payments")
