import pandas as pd

from files import load
from convert_dates import convert_dates


def evaluable_deliveries(orders):
    return orders[(orders["order_status"] == "delivered")
                  & orders["order_delivered_customer_date"].notna()
                  & (orders["month"] >= "2017-01")
                  & (orders["month"] <= "2018-08")]


def add_delay(table):
    delivery = table["order_delivered_customer_date"].dt.date
    estimated = table["order_estimated_delivery_date"].dt.date
    table["late"] = delivery > estimated
    table["delivery_days"] = (
        table["order_delivered_customer_date"]
        - table["order_purchase_timestamp"]).dt.days
    return table


def summarize_deliveries(table):
    print(f"evaluable deliveries: {len(table)}")
    print(f"late deliveries: {table['late'].sum()} "
          f"({table['late'].mean() * 100:.1f} %)")
    print(f"delivery days: median {table['delivery_days'].median():.0f} "
          f"| 90th percentile {table['delivery_days'].quantile(0.9):.0f}")


def deliveries_by_state(table, customers):
    data = table.merge(
        customers[["customer_id", "customer_state"]], on="customer_id", how="left")
    deliveries = data.groupby("customer_state")["order_id"].count()
    delays = data.groupby("customer_state")["late"].sum()
    median_days = data.groupby("customer_state")["delivery_days"].median()
    p90_days = data.groupby("customer_state")["delivery_days"].quantile(0.9)
    state_table = pd.DataFrame({
        "deliveries": deliveries,
        "delays": delays,
        "median_days": median_days,
        "p90_days": p90_days,
    })
    state_table["delay_rate_%"] = (
        state_table["delays"] / state_table["deliveries"] * 100).round(1)
    state_table = state_table.sort_values("deliveries", ascending=False)
    few_deliveries = state_table[state_table["deliveries"] < 100]
    if len(few_deliveries):
        print(f"states with fewer than 100 deliveries: {len(few_deliveries)} "
              f"({', '.join(few_deliveries.index)})")
    else:
        print("no state below 100 deliveries")
    print()
    print(state_table.to_string())


def deliveries_by_month(table):
    deliveries = table.groupby("month")["order_id"].count()
    delays = table.groupby("month")["late"].sum()
    median_days = table.groupby("month")["delivery_days"].median()
    month_table = pd.DataFrame({
        "deliveries": deliveries,
        "delays": delays,
        "median_days": median_days,
    })
    month_table["delay_rate_%"] = (
        month_table["delays"] / month_table["deliveries"] * 100).round(1)
    print()
    print(month_table.to_string())


def main():
    orders = load("olist_orders_dataset.csv")
    customers = load("olist_customers_dataset.csv")

    orders = convert_dates(orders)
    orders["month"] = orders["order_purchase_timestamp"].dt.strftime("%Y-%m")

    table_to_evaluate = add_delay(evaluable_deliveries(orders))
    summarize_deliveries(table_to_evaluate)
    deliveries_by_state(table_to_evaluate, customers)
    deliveries_by_month(table_to_evaluate)


if __name__ == "__main__":
    main()
