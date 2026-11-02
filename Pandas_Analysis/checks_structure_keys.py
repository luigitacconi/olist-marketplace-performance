# Structure and keys — reproduces section 1 of docs/data_quality.md

import pandas as pd

from files import load


orders = load("olist_orders_dataset.csv")
customers = load("olist_customers_dataset.csv")
order_items = load("olist_order_items_dataset.csv")
order_payments = load("olist_order_payments_dataset.csv")
order_reviews = load("olist_order_reviews_dataset.csv")
products = load("olist_products_dataset.csv")
sellers = load("olist_sellers_dataset.csv")
translation = load("product_category_name_translation.csv")


TABLES = {
    "orders": orders,
    "customers": customers,
    "order_items": order_items,
    "order_payments": order_payments,
    "order_reviews": order_reviews,
    "products": products,
    "sellers": sellers,
    "translation": translation
}


def check_duplicate_rows(tables):
    for table_name, table in tables.items():
        duplicate_rows = table.duplicated().sum()
        print(f"{table_name}: {duplicate_rows} duplicate rows")


def explore_columns(tables):
    keys_to_check = [
        "product_category_name", "customer_id", "customer_unique_id",
        "order_id", "product_id", "seller_id", "review_id"
    ]

    for table_name, table in tables.items():
        for column_name in table.columns:
            if column_name in keys_to_check:
                duplicate_keys = table[column_name].duplicated().sum()
                print(
                    f" {table_name}= Column '{column_name}': {duplicate_keys} duplicates")


def check_unique_keys(tables):
    keys = {
        "orders": "order_id",
        "customers": "customer_id",
        "products": "product_id",
        "translation": "product_category_name",
    }

    for table_name, column_name in keys.items():
        duplicates = tables[table_name][column_name].duplicated().sum()
        print(f"{table_name}.{column_name}: duplicate count= {duplicates}")


def check_remaining_keys(tables):
    order_items = tables["order_items"]
    order_payments = tables["order_payments"]
    order_reviews = tables["order_reviews"]

    pairs = [
        ("order_items", ["order_id", "order_item_id"]),
        ("order_payments", ["order_id", "payment_sequential"]),
    ]
    for table_name, columns in pairs:
        duplicates = tables[table_name].duplicated(subset=columns).sum()
        print(
            f"{table_name} pair {columns}: duplicate rows: {duplicates}")

    extra_rows = len(tables["customers"]) - \
        tables["customers"]["customer_unique_id"].nunique()
    print(
        f"customer_unique_id: {extra_rows} extra rows")

    sizes = order_reviews.groupby("review_id").size()
    involved_ids = (sizes > 1).sum()
    involved_rows = sizes[sizes > 1].sum()
    print(f"review_id: {involved_ids} ids involved "
          f"across {involved_rows} rows")

    duplicated_ids = sizes[sizes > 1].index
    duplicated_reviews = order_reviews[order_reviews["review_id"].isin(duplicated_ids)]
    same_order = duplicated_reviews.groupby("review_id")["order_id"].nunique()
    repeated = (same_order < sizes.loc[same_order.index]).sum()
    print(f"  review_id groups with the same order repeated: {repeated}")


def check_cross_table_links(tables):
    links = [
        ("order_items", "order_id", "orders", "order_id"),
        ("order_items", "product_id", "products", "product_id"),
        ("order_items", "seller_id", "sellers", "seller_id"),
        ("order_payments", "order_id", "orders", "order_id"),
        ("order_reviews", "order_id", "orders", "order_id"),
        ("orders", "customer_id", "customers", "customer_id"),
    ]

    for source_table, source_column, reference_table, reference_column in links:
        source_values = tables[source_table][source_column]
        reference_values = tables[reference_table][reference_column]
        orphans = (~source_values.isin(reference_values)).sum()
        print(f"{source_table}.{source_column} -> "
              f"{reference_table}.{reference_column}: {orphans} values with no match")


def check_orders_data(tables):
    order_items = tables["order_items"]
    order_payments = tables["order_payments"]
    order_reviews = tables["order_reviews"]
    orders_set = set(tables["orders"]["order_id"])
    without_items = len(orders_set - set(order_items["order_id"]))
    without_payments = len(orders_set - set(order_payments["order_id"]))
    without_reviews = len(orders_set - set(order_reviews["order_id"]))
    print(f"orders without items: {without_items}")
    print(f"orders without payments: {without_payments}")
    print(f"orders without reviews: {without_reviews}")


# explore_columns(TABLES)
check_duplicate_rows(TABLES)
check_unique_keys(TABLES)
check_remaining_keys(TABLES)
check_cross_table_links(TABLES)
check_orders_data(TABLES)
