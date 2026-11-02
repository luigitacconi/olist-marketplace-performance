# Olist Marketplace Performance

Independent e-commerce analytics project on the Olist Brazilian E-Commerce public dataset.

**Business questions**

1. **Sales** — How do order volume and merchandise value vary over time, across product categories and destination states?
2. **Service** — Where do late deliveries and long delivery times concentrate?
3. **Experience** — What relationship can we observe between delivery punctuality and review scores, and what checks are needed before acting?

**Data source:** [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) — CC BY-NC-SA 4.0.
Raw files are not included in this repository; see [`data/README.txt`](data/README.txt) for download instructions.

**Stack:** Python/pandas.

## Repository structure

```
Pandas_Analysis/     Python verification scripts and the three analyses (sales, service, experience)
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

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Status

Data quality verified; the three analyses are available in `Pandas_Analysis/`.
