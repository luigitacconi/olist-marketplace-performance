from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).absolute().parent.parent
PANDAS_DIR = REPO_ROOT / "Pandas_Analysis"
if str(PANDAS_DIR) not in sys.path:
    sys.path.insert(0, str(PANDAS_DIR))

from convert_dates import convert_dates
from experience_analysis import one_review_per_order
from files import load
from sales_analysis import orders_by_state, sales_by_category, sales_by_month
from service_analysis import add_delay, evaluable_deliveries

OUTPUT_DIR = Path(__file__).absolute().parent / "images"

BLUE = "#2563EB"
LIGHT_BLUE = "#60A5FA"
TEAL = "#0D9488"
AMBER = "#F59E0B"
ORANGE = "#EA580C"
SLATE = "#64748B"
GRID = "#E2E8F0"
TEXT = "#1E293B"
SUBTEXT = "#475569"


def configure_style():
    plt.rcParams.update({
        "figure.facecolor": "#FFFFFF",
        "axes.facecolor": "#FFFFFF",
        "axes.edgecolor": "#CBD5E1",
        "axes.linewidth": 0.8,
        "axes.labelsize": 10,
        "axes.labelcolor": TEXT,
        "xtick.color": TEXT,
        "ytick.color": TEXT,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
        "text.color": TEXT,
    })


def style_chart(ax, grid_axis="y"):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis=grid_axis, color=GRID, linewidth=0.7, zorder=0)
    ax.set_axisbelow(True)


def add_titles(fig, title, subtitle, footnote):
    fig.text(0.04, 0.96, title, fontsize=13.5, fontweight="bold", ha="left", va="top", color="#0F172A")
    fig.text(0.04, 0.905, subtitle, fontsize=10, ha="left", va="top", color=SUBTEXT)
    fig.text(0.04, 0.02, footnote, fontsize=8.5, ha="left", va="bottom", color=SLATE)


def save_chart(fig, filename):
    out_path = OUTPUT_DIR / filename
    fig.savefig(out_path, dpi=200, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    return out_path


def format_month(month_str):
    return pd.to_datetime(month_str + "-01").strftime("%b %y")


def format_category(name):
    if name == "Unknown":
        return "Unknown"
    return name.replace("_", " ").title()


def plot_monthly_sales(orders, order_items):
    monthly = sales_by_month(orders, order_items)
    months = list(monthly.index)
    values_k = monthly["order_value"] / 1000.0
    x = np.arange(len(months))

    colors = []
    for month in months:
        if month == "2017-11":
            colors.append(ORANGE)
        elif month >= "2018-01":
            colors.append(TEAL)
        else:
            colors.append(BLUE)

    fig, ax = plt.subplots(figsize=(12, 5.6))
    fig.subplots_adjust(left=0.07, right=0.97, top=0.80, bottom=0.19)
    style_chart(ax, "y")

    bars = ax.bar(x, values_k, width=0.68, color=colors, zorder=3)
    for bar, val in zip(bars, values_k):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 18, f"{val:.0f}k",
                ha="center", va="bottom", fontsize=7.8, color=TEXT)

    ax.set_xticks(x)
    ax.set_xticklabels([format_month(m) for m in months], rotation=35, ha="right")
    ax.set_ylabel("Merchandise value (BRL thousands)")
    ax.set_ylim(0, 1180)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}k" if v > 0 else "0"))

    legend_items = [
        Patch(color=BLUE, label="2017 growth"),
        Patch(color=ORANGE, label="Nov 2017 peak"),
        Patch(color=TEAL, label="2018 plateau"),
    ]
    ax.legend(handles=legend_items, loc="upper left", ncol=3, frameon=True,
              facecolor="#FFFFFF", edgecolor="#CBD5E1", fontsize=9)

    total_orders = int(monthly["order_count"].sum())
    total_val_m = monthly["order_value"].sum() / 1e6
    add_titles(
        fig,
        "Monthly Merchandise Value Grew Rapidly in 2017, Then Stabilized in 2018",
        f"Delivered item value in BRL thousands across 20 full months (Jan 2017 – Aug 2018; {total_orders:,} orders, BRL {total_val_m:.2f}M total)",
        "Source: Olist dataset. Item prices only (shipping excluded). Excludes 2016 ramp-up and Sep–Oct 2018 tail.",
    )
    return save_chart(fig, "01_monthly_sales.png"), total_orders, total_val_m


def plot_top_categories(orders, order_items, products, translation):
    categories = sales_by_category(orders, order_items, products, translation)
    total_val = categories["order_value"].sum()
    top10 = categories.head(10).iloc[::-1]
    top10_share = top10["order_value"].sum() / total_val * 100.0

    y = np.arange(len(top10))
    values_k = top10["order_value"] / 1000.0
    colors = [LIGHT_BLUE] * 3 + [BLUE] * 4 + [TEAL] * 3

    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    fig.subplots_adjust(left=0.22, right=0.96, top=0.80, bottom=0.16)
    style_chart(ax, "x")

    ax.barh(y, values_k, height=0.66, color=colors, zorder=3)
    for idx, (_, row) in enumerate(top10.iterrows()):
        val = row["order_value"]
        share = val / total_val * 100.0
        text = f"BRL {val / 1e6:.2f}M ({share:.1f}%)" if val >= 1e6 else f"BRL {val / 1e3:,.0f}k ({share:.1f}%)"
        ax.text(val / 1e3 + 22, idx, text, va="center", ha="left", fontsize=8.8, color=TEXT)

    ax.set_yticks(y)
    ax.set_yticklabels([format_category(c) for c in top10.index], fontsize=9.5)
    ax.set_xlabel("Delivered merchandise value (BRL thousands)")
    ax.set_xlim(0, 1620)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}k" if v > 0 else "0"))

    add_titles(
        fig,
        f"Top 10 Categories Generate {top10_share:.1f}% of Total Merchandise Value",
        f"Delivered item value (BRL) and share of the {len(categories)}-category total (Jan 2017 – Aug 2018; BRL {total_val / 1e6:.2f}M)",
        "Top 8 categories reach 54.5% and top 18 reach 81.3%. Item values are additive; order counts per category are not.",
    )
    return save_chart(fig, "02_top_categories.png"), len(categories), top10_share


def plot_sales_by_state(orders, customers, order_items):
    states = orders_by_state(orders, customers, order_items)
    total_val = states["state_order_value"].sum()
    top3_share = states.head(3)["state_order_value"].sum() / total_val * 100.0
    top10 = states.head(10).iloc[::-1]
    top10_share = top10["state_order_value"].sum() / total_val * 100.0
    sp_val_share = states.loc["SP", "state_value_share_%"]
    sp_ord_share = states.loc["SP", "state_order_share_%"]

    y = np.arange(len(top10))
    values_k = top10["state_order_value"] / 1000.0
    colors = [LIGHT_BLUE] * 7 + [BLUE] * 2 + [TEAL]

    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    fig.subplots_adjust(left=0.09, right=0.96, top=0.80, bottom=0.16)
    style_chart(ax, "x")

    ax.barh(y, values_k, height=0.66, color=colors, zorder=3)
    for idx, (state, row) in enumerate(top10.iterrows()):
        val = row["state_order_value"]
        val_share = row["state_value_share_%"]
        n_ord = int(row["state_order_count"])
        val_str = f"BRL {val / 1e6:.2f}M" if val >= 1e6 else f"BRL {val / 1e3:,.0f}k"
        label = f"{val_str}  ({val_share:.1f}% | {n_ord:,} orders)"
        ax.text(val / 1e3 + 80, idx, label, va="center", ha="left", fontsize=8.8,
                fontweight="bold" if state == "SP" else "normal", color=TEXT)

    ax.set_yticks(y)
    ax.set_yticklabels(list(top10.index), fontsize=9.5, fontweight="bold")
    ax.set_xlabel("Delivered merchandise value (BRL thousands)")
    ax.set_xlim(0, 7600)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}k" if v > 0 else "0"))

    total_orders = int(states["state_order_count"].sum())
    add_titles(
        fig,
        f"São Paulo Alone Drives {sp_val_share:.1f}% of Merchandise Value and {sp_ord_share:.1f}% of Orders",
        f"Top 10 of {len(states)} destination states by delivered item value (Jan 2017 – Aug 2018; Top 3 = {top3_share:.1f}%, Top 10 = {top10_share:.1f}%)",
        f"Population: {total_orders:,} delivered orders across {len(states)} states (BRL {total_val / 1e6:.2f}M total, item prices only). Remaining {len(states) - 10} states account for {100 - top10_share:.1f}%.",
    )
    return save_chart(fig, "03_sales_by_state.png"), len(states), sp_val_share, sp_ord_share, top10_share


def plot_late_deliveries_by_month(orders):
    eval_df = add_delay(evaluable_deliveries(orders).copy())
    total_eval = len(eval_df)
    total_late = int(eval_df["late"].sum())
    overall_rate = total_late / total_eval * 100.0
    median_days = eval_df["delivery_days"].median()
    p90_days = eval_df["delivery_days"].quantile(0.9)

    monthly = eval_df.groupby("month").agg(deliveries=("order_id", "count"), delays=("late", "sum"))
    monthly["late_pct"] = monthly["delays"] / monthly["deliveries"] * 100.0
    months = list(monthly.index)
    x = np.arange(len(months))

    colors = []
    for rate in monthly["late_pct"]:
        if rate >= 12.0:
            colors.append(ORANGE)
        elif rate > overall_rate:
            colors.append(AMBER)
        else:
            colors.append(TEAL)

    fig, ax = plt.subplots(figsize=(12, 5.5))
    fig.subplots_adjust(left=0.07, right=0.97, top=0.80, bottom=0.19)
    style_chart(ax, "y")

    bars = ax.bar(x, monthly["late_pct"], width=0.68, color=colors, zorder=3)
    ax.axhline(overall_rate, color=SLATE, linestyle="--", linewidth=1.3, zorder=2)

    for bar, rate in zip(bars, monthly["late_pct"]):
        weight = "bold" if rate >= 12.0 else "normal"
        ax.text(bar.get_x() + bar.get_width() / 2, rate + 0.4, f"{rate:.1f}%",
                ha="center", va="bottom", fontsize=7.8, fontweight=weight, color=TEXT, zorder=5,
                bbox=dict(boxstyle="square,pad=0.06", fc="#FFFFFF", ec="none", alpha=0.9))

    ax.set_xticks(x)
    ax.set_xticklabels([format_month(m) for m in months], rotation=35, ha="right")
    ax.set_ylabel("Late deliveries (%)")
    ax.set_ylim(0, 23.5)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))

    legend_items = [
        Patch(color=TEAL, label="Below average"),
        Patch(color=AMBER, label="Above average"),
        Patch(color=ORANGE, label="Major spike (≥12%)"),
        Line2D([0], [0], color=SLATE, linestyle="--", linewidth=1.3, label=f"Overall avg ({overall_rate:.1f}%)"),
    ]
    ax.legend(handles=legend_items, loc="upper left", ncol=2, frameon=True,
              facecolor="#FFFFFF", edgecolor="#CBD5E1", fontsize=8.8)

    add_titles(
        fig,
        "Late Deliveries Spiked in Nov 2017 (12.4%) and Feb–Mar 2018 (up to 19.0%)",
        f"{total_eval:,} evaluable deliveries; {total_late:,} late ({overall_rate:.1f}%) | Delivery time: median {median_days:.0f} days, 90th percentile {p90_days:.0f} days",
        "Grouped by purchase month (Jan 2017 – Aug 2018). Punctuality compares delivered calendar date vs. estimated delivery date.",
    )
    return save_chart(fig, "04_late_deliveries_by_month.png"), total_eval, total_late, overall_rate, median_days, p90_days


def plot_late_deliveries_by_state(orders, customers):
    eval_df = add_delay(evaluable_deliveries(orders).copy())
    overall_rate = eval_df["late"].sum() / len(eval_df) * 100.0

    merged = eval_df.merge(customers[["customer_id", "customer_state"]], on="customer_id", how="left")
    by_state = merged.groupby("customer_state").agg(deliveries=("order_id", "count"), delays=("late", "sum"))
    by_state["late_pct"] = by_state["delays"] / by_state["deliveries"] * 100.0

    top_states = by_state[by_state["deliveries"] >= 1000].sort_values("late_pct", ascending=True)
    y = np.arange(len(top_states))
    colors = [ORANGE if r > overall_rate else TEAL for r in top_states["late_pct"]]

    fig, ax = plt.subplots(figsize=(10.5, 6.0))
    fig.subplots_adjust(left=0.09, right=0.96, top=0.81, bottom=0.16)
    style_chart(ax, "x")

    ax.barh(y, top_states["late_pct"], height=0.66, color=colors, zorder=3)
    ax.axvline(overall_rate, color=SLATE, linestyle="--", linewidth=1.3, zorder=1)

    for idx, (_, row) in enumerate(top_states.iterrows()):
        rate = row["late_pct"]
        n_del = int(row["deliveries"])
        ax.text(rate + 0.35, idx, f"{rate:.1f}%  ({n_del:,} deliveries)",
                va="center", ha="left", fontsize=8.8, zorder=5,
                fontweight="bold" if rate > overall_rate else "normal", color=TEXT,
                bbox=dict(boxstyle="square,pad=0.12", fc="#FFFFFF", ec="none", alpha=0.92))

    ax.set_yticks(y)
    ax.set_yticklabels(list(top_states.index), fontsize=9.5, fontweight="bold")
    ax.set_xlabel("Late deliveries (%)")
    ax.set_xlim(0, 21)
    ax.set_xticks([0, 5, 10, 15, 20])
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))

    legend_items = [
        Patch(color=ORANGE, label=f"Above {overall_rate:.1f}% average"),
        Patch(color=TEAL, label=f"Below {overall_rate:.1f}% average"),
        Line2D([0], [0], color=SLATE, linestyle="--", linewidth=1.3, label=f"Overall avg ({overall_rate:.1f}%)"),
    ]
    ax.legend(handles=legend_items, loc="lower right", frameon=True,
              facecolor="#FFFFFF", edgecolor="#CBD5E1", fontsize=8.8)

    add_titles(
        fig,
        "Delivery Reliability Varies Widely Across Major Destination States",
        "Late delivery rate and volume for the 12 states with ≥1,000 evaluable deliveries (Jan 2017 – Aug 2018)",
        f"Overall late rate: {overall_rate:.1f}% ({int(eval_df['late'].sum()):,} / {len(eval_df):,}). Smaller states with ≥100 deliveries include AL (21.5%, n=396) and MA (17.5%, n=713).",
    )
    return save_chart(fig, "05_late_deliveries_by_state.png"), len(top_states)


def plot_punctuality_vs_reviews(orders, reviews):
    eval_df = add_delay(evaluable_deliveries(orders).copy())
    unique_reviews = one_review_per_order(reviews)

    base = eval_df.merge(
        unique_reviews[["order_id", "review_score", "review_answer_timestamp"]],
        on="order_id",
        how="inner",
    )
    base["low_score"] = base["review_score"] <= 2
    base["before_delivery"] = base["review_answer_timestamp"] < base["order_delivered_customer_date"]

    groups = [
        ("All reviews", base),
        ("Reviewed at or after\ndelivery", base[~base["before_delivery"]]),
        ("Reviewed before\ndelivery", base[base["before_delivery"]]),
    ]

    on_time_rates, on_time_ns = [], []
    late_rates, late_ns = [], []
    for _, subset in groups:
        on_time = subset[~subset["late"]]
        late = subset[subset["late"]]
        on_time_rates.append(on_time["low_score"].mean() * 100.0)
        on_time_ns.append(len(on_time))
        late_rates.append(late["low_score"].mean() * 100.0)
        late_ns.append(len(late))

    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    fig.subplots_adjust(left=0.08, right=0.97, top=0.80, bottom=0.18)
    style_chart(ax, "y")

    x = np.arange(len(groups))
    width = 0.34
    offset = 0.20
    bars_on_time = ax.bar(x - offset, on_time_rates, width=width, color=TEAL, label="On time", zorder=3)
    bars_late = ax.bar(x + offset, late_rates, width=width, color=ORANGE, label="Late", zorder=3)

    for bar, rate, n_val in zip(bars_on_time, on_time_rates, on_time_ns):
        ax.text(bar.get_x() + bar.get_width() / 2, rate + 1.8, f"{rate:.1f}%\n(n={n_val:,})",
                ha="center", va="bottom", fontsize=9, fontweight="bold", color=TEAL)
    for bar, rate, n_val in zip(bars_late, late_rates, late_ns):
        ax.text(bar.get_x() + bar.get_width() / 2, rate + 1.8, f"{rate:.1f}%\n(n={n_val:,})",
                ha="center", va="bottom", fontsize=9, fontweight="bold", color=ORANGE)

    ax.set_xticks(x)
    ax.set_xticklabels([label for label, _ in groups], fontsize=10)
    ax.set_ylabel("Low review rate (scores 1–2, %)")
    ax.set_xlim(-0.55, 2.55)
    ax.set_ylim(0, 98)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    ax.legend(loc="upper left", frameon=True, facecolor="#FFFFFF", edgecolor="#CBD5E1", fontsize=9.5)

    coverage = len(base) / len(eval_df) * 100.0
    add_titles(
        fig,
        "Late Orders Receive Far More Low Scores — Especially Before Delivery",
        f"Share of 1–2 star reviews comparing on-time vs. late deliveries ({len(base):,} matched deliveries, {coverage:.1f}% coverage)",
        "One review per order (Jan 2017 – Aug 2018). Observational comparison: association does not prove causation.",
    )
    return save_chart(fig, "06_punctuality_vs_reviews.png"), len(base), on_time_rates[0], late_rates[0]


def main():
    configure_style()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    orders = load("olist_orders_dataset.csv")
    order_items = load("olist_order_items_dataset.csv")
    products = load("olist_products_dataset.csv")
    translation = load("product_category_name_translation.csv")
    customers = load("olist_customers_dataset.csv")
    reviews = load("olist_order_reviews_dataset.csv")

    orders = convert_dates(orders)
    order_items = convert_dates(order_items)
    reviews = convert_dates(reviews)
    orders["month"] = orders["order_purchase_timestamp"].dt.strftime("%Y-%m")

    p1, n_orders, val_m = plot_monthly_sales(orders, order_items)
    p2, n_cats, top10_share = plot_top_categories(orders, order_items, products, translation)
    p3, n_all_states, sp_val, sp_ord, top10_st_share = plot_sales_by_state(orders, customers, order_items)
    p4, n_eval, n_late, late_pct, med_d, p90_d = plot_late_deliveries_by_month(orders)
    p5, n_states = plot_late_deliveries_by_state(orders, customers)
    p6, n_rev, ot_low, lt_low = plot_punctuality_vs_reviews(orders, reviews)

    print(f"Saved {p1.name}: {n_orders:,} orders, BRL {val_m:.2f}M")
    print(f"Saved {p2.name}: {n_cats} categories, top 10 share={top10_share:.2f}%")
    print(f"Saved {p3.name}: {n_all_states} states, SP={sp_val:.2f}% val / {sp_ord:.2f}% ord, top 10={top10_st_share:.2f}%")
    print(f"Saved {p4.name}: {n_eval:,} evaluable deliveries, {n_late:,} late ({late_pct:.2f}%), median {med_d:.0f}d, p90 {p90_d:.0f}d")
    print(f"Saved {p5.name}: {n_states} states (>=1,000 deliveries)")
    print(f"Saved {p6.name}: {n_rev:,} reviews, on-time low={ot_low:.2f}%, late low={lt_low:.2f}%")


if __name__ == "__main__":
    main()
