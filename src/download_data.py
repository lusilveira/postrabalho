"""
download_data.py
-----------------
Baixa o Brazilian E-Commerce Public Dataset by Olist a partir de um mirror
público no GitHub (o dataset original está hospedado no Kaggle e exige
autenticação para download via API:
https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).

Uso:
    python src/download_data.py
"""
import os
import urllib.request

REPO = "spdrio/Brazilian-E-Commerce-Public-Dataset-by-Olist"
BASE_URL = f"https://raw.githubusercontent.com/{REPO}/master/files"
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

FILES = [
    "olist_customers_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "product_category_name_translation.csv",
]


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for filename in FILES:
        url = f"{BASE_URL}/{filename}"
        dest = os.path.join(OUT_DIR, filename)
        print(f"Baixando {filename} ...")
        urllib.request.urlretrieve(url, dest)
        size_kb = os.path.getsize(dest) / 1024
        print(f"  -> salvo em {dest} ({size_kb:,.0f} KB)")
    print("\nDownload concluído. Os arquivos CSV estão em ./data")


if __name__ == "__main__":
    main()
