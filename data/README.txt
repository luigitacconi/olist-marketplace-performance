Data — download instructions
============================

The raw dataset files are NOT included in this repository.

1) Download the dataset "Brazilian E-Commerce Public Dataset by Olist" from Kaggle:
   https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

2) Extract the archive and place these CSV files inside data/raw/ :

   - olist_orders_dataset.csv                  (99,441 rows)
   - olist_customers_dataset.csv               (99,441 rows)
   - olist_order_items_dataset.csv             (112,650 rows)
   - olist_order_payments_dataset.csv          (103,886 rows)
   - olist_order_reviews_dataset.csv           (99,224 rows)
   - olist_products_dataset.csv                (32,951 rows)
   - product_category_name_translation.csv     (71 rows)
   - olist_sellers_dataset.csv                 (3,095 rows)
   - olist_geolocation_dataset.csv             (1,000,163 rows)

   The expected row counts above let you check that the download is complete.

3) Licence: CC BY-NC-SA 4.0.
   See docs/data_source_and_license.md for conditions and notes.
   The original CSV files are not redistributed here; always download them from the official source.
   The Excel workbook in Excel_Analysis/ embeds copies of the orders and items tables
   (derivative work, CC BY-NC-SA 4.0; see docs/data_source_and_license.md).

Note: the local database file data/olist.duckdb is not committed.
