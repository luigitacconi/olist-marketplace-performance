# Anomalies — reproduces section 4 of docs/data_quality.md

import pandas as pd

from files import load
from convert_dates import convert_dates


orders = load("olist_orders_dataset.csv")
order_items = load("olist_order_items_dataset.csv")
order_payments = load("olist_order_payments_dataset.csv")
products = load("olist_products_dataset.csv")

orders = convert_dates(orders)
order_items = convert_dates(order_items)


def check_impossible_dates(orders):
    purchase = orders["order_purchase_timestamp"]
    approval = orders["order_approved_at"]
    carrier = orders["order_delivered_carrier_date"]
    delivery = orders["order_delivered_customer_date"]

    carrier_before = carrier < purchase
    print(f"carrier before purchase: {carrier_before.sum()}")
    print(f"  same day: "
          f"{(carrier_before & (carrier.dt.date == purchase.dt.date)).sum()}")
    print(f"  days before: "
          f"{(carrier_before & (carrier.dt.date < purchase.dt.date)).sum()}")

    delivery_before = delivery < carrier
    print(f"delivery before carrier: {delivery_before.sum()}")
    print(f"  same day: "
          f"{(delivery_before & (delivery.dt.date == carrier.dt.date)).sum()}")
    print(f"  days before: "
          f"{(delivery_before & (delivery.dt.date < carrier.dt.date)).sum()}")

    print(f"approval before purchase: {(approval < purchase).sum()}")
    print(f"delivery before purchase: {(delivery < purchase).sum()}")


def check_amounts(order_items, order_payments, products):
    print(f"negative prices: {(order_items['price'] < 0).sum()}")
    print(f"negative payments: {(order_payments['payment_value'] < 0).sum()}")
    print(f"zero freight: {(order_items['freight_value'] == 0).sum()}")
    print(f"zero payments: {(order_payments['payment_value'] == 0).sum()}")

    zero_installments = order_payments["payment_installments"] == 0
    print(f"zero installments: {zero_installments.sum()}")
    print(f"  all credit_card: "
          f"{(order_payments.loc[zero_installments, 'payment_type'] == 'credit_card').all()}")

    print(f"zero product weight: {(products['product_weight_g'] == 0).sum()}")


def check_status_consistency(orders):
    delivered = orders["order_status"] == "delivered"
    print(f"delivered without delivery date: "
          f"{(delivered & orders['order_delivered_customer_date'].isna()).sum()}")
    print(f"delivered without approval: "
          f"{(delivered & orders['order_approved_at'].isna()).sum()}")
    print(f"delivery date but status not delivered: "
          f"{(orders['order_delivered_customer_date'].notna() & ~delivered).sum()}")


def check_shipping_limits(order_items):
    limit = order_items["shipping_limit_date"]
    print(f"shipping limits beyond 2018: {(limit.dt.year > 2018).sum()}")
    print(f"  maximum date: {limit.max().date()}")


check_impossible_dates(orders)
check_amounts(order_items, order_payments, products)
check_status_consistency(orders)
check_shipping_limits(order_items)
