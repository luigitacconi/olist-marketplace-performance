# Missing values — reproduces section 3 of docs/data_quality.md

import pandas as pd

from files import load


orders = load("olist_orders_dataset.csv")
products = load("olist_products_dataset.csv")
order_reviews = load("olist_order_reviews_dataset.csv")


def check_delivery_dates(orders):
    without_date = orders["order_delivered_customer_date"].isna()
    print(f"deliveries without date: {without_date.sum()}")
    print(f"  of which not delivered: "
          f"{(without_date & (orders['order_status'] != 'delivered')).sum()}")
    print(f"  of which delivered: "
          f"{(without_date & (orders['order_status'] == 'delivered')).sum()}")


def check_approvals(orders):
    without_approval = orders["order_approved_at"].isna()
    print(f"missing approvals: {without_approval.sum()}")
    for status in ["canceled", "delivered", "created"]:
        print(f"  of which {status}: "
              f"{(without_approval & (orders['order_status'] == status)).sum()}")


def check_categories(products):
    print(f"missing product categories: "
          f"{products['product_category_name'].isna().sum()}")


def check_scores(order_reviews):
    print(f"reviews without score: {order_reviews['review_score'].isna().sum()}")
    print(f"minimum score: {order_reviews['review_score'].min()}")
    print(f"maximum score: {order_reviews['review_score'].max()}")


check_delivery_dates(orders)
check_approvals(orders)
check_categories(products)
check_scores(order_reviews)
