import pandas as pd

from files import load
from convert_dates import convert_dates
from convert_semester_currencies import semester_currency_variation, month_to_semester


def filter_valid_orders(orders):
    return orders[(orders["order_status"] == "delivered")
                  & (orders["month"] >= "2017-01")
                  & (orders["month"] <= "2018-08")]


def delivered_orders(table, show=False):
    total = table["order_id"].nunique()
    delivered = (table["order_status"] == "delivered").sum()
    if show:
        print(f"orders (full dataset): {total} | "
              f"delivered orders (full dataset): {delivered}")
    return total, delivered


def sales_by_month(orders, order_items):
    delivered = filter_valid_orders(orders)
    monthly_delivered = delivered.groupby("month")["order_id"].count()
    delivered_items = order_items[order_items["order_id"].isin(
        delivered["order_id"])]
    delivered_items = delivered_items.merge(
        delivered[["order_id", "month"]], on="order_id")
    delivered_items_value = delivered_items.groupby("month")[
        "price"].sum().round(2)
    table = pd.DataFrame({"order_count": monthly_delivered,
                          "order_value": delivered_items_value})
    table["semester"] = [month_to_semester(m) for m in table.index]
    table["exchange_rate"] = table["semester"].map(semester_currency_variation)
    table["usd_value_semester"] = (
        table["order_value"] * table["exchange_rate"]).round(2)
    table = table.drop(columns=["semester"])
    table = table.drop(columns=["exchange_rate"])
    return table


def percentage_changes(table):
    table["order_change_%"] = (
        table["order_count"].pct_change() * 100).round(2)
    table["value_change_%"] = (
        table["order_value"].pct_change() * 100).round(2)
    return table


def print_orders_sales_table(orders, order_items):
    delivered_orders(orders, show=True)
    table = sales_by_month(orders, order_items)
    table = percentage_changes(table)
    print(table.to_string())


def count_product_categories(products, translation):
    without_category = (products["product_category_name"].isna().sum())
    product_categories = set(products["product_category_name"].dropna())
    translated_categories = set(translation["product_category_name"])
    missing = sorted(product_categories - translated_categories)
    print(f"products without category: {without_category}")
    print(f"product categories: {len(product_categories)}")
    print(f"categories in the translation file: {len(translated_categories)}")
    print(f"categories without translation ({len(missing)}): {missing}")


def sales_by_category(orders, order_items, products, translation):
    delivered = filter_valid_orders(orders)
    delivered_items = order_items[order_items["order_id"].isin(
        delivered["order_id"])]
    delivered_items = delivered_items.merge(
        products[["product_id", "product_category_name"]], on="product_id")
    delivered_items = delivered_items.merge(
        translation, on="product_category_name", how="left")
    delivered_items["category"] = (
        delivered_items["product_category_name_english"]
        .fillna(delivered_items["product_category_name"])
        .fillna("Unknown"))
    table = pd.DataFrame({
        "order_value": delivered_items.groupby("category")["price"].sum().round(2),
        "order_count": delivered_items.groupby("category")["order_id"].nunique(),
    })
    table = table.sort_values("order_value", ascending=False)
    table["share_%"] = (
        table["order_value"] / table["order_value"].sum() * 100).round(2)
    return table


def orders_by_state(orders, customers, order_items):
    delivered = filter_valid_orders(orders)
    rows = delivered.merge(
        order_items[["order_id", "price"]], on="order_id", how="left")
    rows = rows.merge(
        customers[["customer_id", "customer_state"]], on="customer_id")
    table = pd.DataFrame({
        "state_order_count": rows.groupby("customer_state")["order_id"].nunique(),
        "state_order_value": rows.groupby("customer_state")["price"].sum().round(2),
    })
    table = table.sort_values("state_order_value", ascending=False)
    table["state_order_share_%"] = (
        table["state_order_count"] / table["state_order_count"].sum() * 100).round(2)
    table["state_value_share_%"] = (
        table["state_order_value"] / table["state_order_value"].sum() * 100).round(2)
    print(f"states: {len(table)} | distinct orders: {(table['state_order_count'].sum())}")
    return table


def main():
    orders = load("olist_orders_dataset.csv")
    order_items = load("olist_order_items_dataset.csv")
    products = load("olist_products_dataset.csv")
    translation = load("product_category_name_translation.csv")
    customers = load("olist_customers_dataset.csv")

    orders = convert_dates(orders)
    order_items = convert_dates(order_items)

    orders["month"] = orders["order_purchase_timestamp"].dt.strftime("%Y-%m")

    print_orders_sales_table(orders, order_items)
    print()
    count_product_categories(products, translation)
    print()
    print(sales_by_category(orders, order_items, products, translation).head(10))
    print()
    print(orders_by_state(orders, customers, order_items).to_string())


if __name__ == "__main__":
    main()
