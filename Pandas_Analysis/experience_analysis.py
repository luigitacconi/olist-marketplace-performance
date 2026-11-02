import pandas as pd

from files import load
from convert_dates import convert_dates


orders = load("olist_orders_dataset.csv")
reviews = load("olist_order_reviews_dataset.csv")
customers = load("olist_customers_dataset.csv")

orders = convert_dates(orders)
reviews = convert_dates(reviews)
orders["month"] = orders["order_purchase_timestamp"].dt.strftime("%Y-%m")


def evaluable_deliveries(orders):
    return orders[(orders["order_status"] == "delivered")
                  & orders["order_delivered_customer_date"].notna()
                  & (orders["month"] >= "2017-01")
                  & (orders["month"] <= "2018-08")]


def add_delay(table):
    delivery = table["order_delivered_customer_date"].dt.date
    estimated = table["order_estimated_delivery_date"].dt.date
    table["late"] = delivery > estimated
    return table


def one_review_per_order(reviews):
    sorted_reviews = reviews.sort_values(
        ["review_answer_timestamp", "review_creation_date", "review_id"],
        ascending=[False, False, False],
        na_position="last")
    return sorted_reviews.drop_duplicates(subset=["order_id"], keep="first")


def summarize_punctuality_scores(table, unique_reviews):
    base = table.merge(
        unique_reviews[["order_id", "review_score", "review_answer_timestamp"]],
        on="order_id", how="inner")
    base["low_score"] = base["review_score"] <= 2
    print(f"unique reviews per order: {len(unique_reviews)}")
    print(f"evaluable deliveries with a review: {len(base)} / {len(table)} "
          f"({len(base) / len(table) * 100:.1f} %)")
    reviews_per_group = base.groupby("late")["order_id"].count()
    low_scores = base.groupby("late")["low_score"].sum()
    mean_score = base.groupby("late")["review_score"].mean().round(2)
    summary = pd.DataFrame({
        "reviews": reviews_per_group,
        "low_scores": low_scores,
        "mean_score": mean_score,
    })
    summary["low_score_rate_%"] = (
        summary["low_scores"] / summary["reviews"] * 100).round(1)
    print()
    print(summary.to_string())

    base["answered_before_delivery"] = (
        base["review_answer_timestamp"] < base["order_delivered_customer_date"])
    timing_reviews = base.groupby(
        ["late", "answered_before_delivery"])["order_id"].count()
    timing_low_scores = base.groupby(
        ["late", "answered_before_delivery"])["low_score"].sum()
    timing_table = pd.DataFrame({
        "reviews": timing_reviews,
        "low_scores": timing_low_scores,
    })
    timing_table["low_score_rate_%"] = (
        timing_table["low_scores"] / timing_table["reviews"] * 100).round(1)
    print()
    print(timing_table.to_string())
    return base


def punctuality_scores_by_state(base, customers):
    data = base.merge(
        customers[["customer_id", "customer_state"]], on="customer_id", how="left")
    on_time = data[data["late"] == False]
    late = data[data["late"] == True]
    on_time_reviews = on_time.groupby("customer_state")["order_id"].count()
    late_reviews = late.groupby("customer_state")["order_id"].count()
    low_on_time = (
        on_time.groupby("customer_state")["low_score"].mean() * 100).round(1)
    low_late = (
        late.groupby("customer_state")["low_score"].mean() * 100).round(1)
    table = pd.DataFrame({
        "on_time_reviews": on_time_reviews,
        "low_score_on_time_%": low_on_time,
        "late_reviews": late_reviews,
        "low_score_late_%": low_late,
    })
    table = table[(table["on_time_reviews"] >= 100)
                  & (table["late_reviews"] >= 100)]
    table = table.sort_values("on_time_reviews", ascending=False)
    print()
    print(table.to_string())


table = add_delay(evaluable_deliveries(orders))
unique_reviews = one_review_per_order(reviews)
base = summarize_punctuality_scores(table, unique_reviews)
punctuality_scores_by_state(base, customers)
