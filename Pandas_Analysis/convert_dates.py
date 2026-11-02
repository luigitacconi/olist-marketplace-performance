import pandas as pd

date_columns_to_convert = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
    "shipping_limit_date",
    "review_creation_date",
    "review_answer_timestamp",
]


def convert_dates(table):
    for column in date_columns_to_convert:
        if column in table.columns:
            table[column] = pd.to_datetime(
                table[column], errors="coerce")
    return table
