# Olist Marketplace Performance

Independent e-commerce analytics project on the Olist Brazilian E-Commerce public dataset.

**Business questions**

1. **Sales** — How do order volume and merchandise value vary over time, across product categories and destination states?
2. **Service** — Where do late deliveries and long delivery times concentrate?
3. **Experience** — What relationship can we observe between delivery punctuality and review scores, and what checks are needed before acting?

**Data source:** [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) — CC BY-NC-SA 4.0.
Raw files are not included in this repository; see [`data/README.txt`](data/README.txt) for download instructions.

**Stack:** Python/pandas and SQL (DuckDB).

## Repository structure

```
Pandas_Analysis/     Python verification scripts and the three analyses (sales, service, experience)
sql_Analysis/        SQL stage with DuckDB runner, analytical tables and queries
Excel_Analysis/      Excel check workbook (embedded data copy and formulas)
data/               Download instructions (raw files stay local)
docs/               Methodology, data quality report, data source and license
```

## Data quality checks

Every number in [`docs/data_quality.md`](docs/data_quality.md) is reproducible with the scripts in `Pandas_Analysis/`:

```powershell
python Pandas_Analysis/run_checks.py
```

The runner executes, in order:

| script | proves |
|---|---|
| `checks_structure_keys.py` | section 1 — structure and keys |
| `checks_dates_amounts.py` | section 2 — types, dates, amounts |
| `checks_missing_values.py` | section 3 — missing values |
| `checks_anomalies.py` | section 4 — anomalies |
| `checks_temporal_coverage.py` | section 5 — temporal coverage |

## Analyses

The three business questions are answered in `Pandas_Analysis/`:

| script | question |
|---|---|
| `sales_analysis.py` | Sales — monthly orders and merchandise value, product categories, destination states |
| `service_analysis.py` | Service — late deliveries and delivery times by state and month |
| `experience_analysis.py` | Experience — delivery punctuality and review scores |

Each script runs from the repository root:

```powershell
python Pandas_Analysis/sales_analysis.py
```

## SQL stage

The SQL stage shares the core order population, merchandise value, delivery and review definitions with the pandas analysis. It also reports freight, category concentration and delay distributions. The USD view and the state-level review comparison are available in the pandas scripts.

Follow [Setup](#setup) and download the Olist files into `data/raw/` as described in [data/README.txt](data/README.txt). Then run the command below from the repository root.

```powershell
python sql_Analysis/run_sql.py
```

The runner imports the source CSVs, builds `clean_orders` (one row per order) and `clean_items` (one row per item), prints the checks and ten query results, and exports the clean tables. It regenerates `data/olist.duckdb`, `data/clean_orders.csv` and `data/clean_items.csv` locally.

- `sql_Analysis/create_tables.sql` builds and checks the analytical tables.
- `sql_Analysis/analysis.sql` contains nine analysis blocks and ten queries, including the size and distribution of delivery delays.

## Excel check

`Excel_Analysis/check_Olist.xlsx` embeds a copy of the orders and items tables from the source CSVs. The items sheet adds two columns — order status and purchase date — matched by `order_id` when the file was built. The Check sheet recomputes the key numbers with Excel formulas (`COUNTIFS`, `SUMIFS`) on these internal sheets:

| check | value |
|---|---:|
| orders | 99,441 |
| items | 112,650 |
| delivered orders in the main period | 96,211 |
| merchandise value in the main period | 13,181,027.13 BRL |
| delivered orders placed in Nov 2017 | 7,289 |
| merchandise value of those orders | 987,765.37 BRL |

The workbook is a derivative of the dataset and is shared under CC BY-NC-SA 4.0; the original CSV files are downloaded from Kaggle (see [`docs/data_source_and_license.md`](docs/data_source_and_license.md)).

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Status

Data quality verified; the three analyses are available in `Pandas_Analysis/`. The SQL stage builds the analytical tables and runs ten queries across nine analysis blocks. The Excel check reproduces the key numbers from an embedded copy of the source data.
