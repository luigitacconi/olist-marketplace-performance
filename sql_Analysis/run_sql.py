from pathlib import Path

import duckdb


SQL_DIR = Path(__file__).resolve().parent
DATA_DIR = SQL_DIR.parent / "data"
RAW_DIR = DATA_DIR / "raw"

RAW_FILES = {
    "raw_orders": "olist_orders_dataset.csv",
    "raw_customers": "olist_customers_dataset.csv",
    "raw_order_items": "olist_order_items_dataset.csv",
    "raw_order_payments": "olist_order_payments_dataset.csv",
    "raw_order_reviews": "olist_order_reviews_dataset.csv",
    "raw_products": "olist_products_dataset.csv",
    "raw_category_translation": "product_category_name_translation.csv",
}


def run_sql_file(db, path):
    result_number = 0
    for statement in db.extract_statements(path.read_text(encoding="utf-8-sig")):
        result = db.execute(statement.query)
        if statement.type.name == "SELECT":
            result_number += 1
            print(f"\n{path.name} | result {result_number}")
            print(result.fetchdf().to_string(index=False))


def main():
    missing = [name for name in RAW_FILES.values() if not (RAW_DIR / name).is_file()]
    if missing:
        raise SystemExit(f"Missing CSV files in {RAW_DIR}:\n" + "\n".join(missing))

    with duckdb.connect(str(DATA_DIR / "olist.duckdb")) as db:
        db.execute("BEGIN TRANSACTION")
        for table, filename in RAW_FILES.items():
            db.execute(
                f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM read_csv_auto(?)",
                [str(RAW_DIR / filename)],
            )
        run_sql_file(db, SQL_DIR / "create_tables.sql")
        db.execute("COMMIT")

        for table in ("clean_orders", "clean_items"):
            db.execute(
                f"COPY {table} TO ? (FORMAT CSV, HEADER, DELIMITER ',')",
                [str(DATA_DIR / f"{table}.csv")],
            )

        run_sql_file(db, SQL_DIR / "analysis.sql")


if __name__ == "__main__":
    main()
