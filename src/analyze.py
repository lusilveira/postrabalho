"""
analyze.py
----------
Análise exploratória do Brazilian E-Commerce Public Dataset by Olist,
realizada para a Fase 1 do Tech Challenge (Postech — IA para Devs).

Objetivo: extrair achados reais sobre prazos de entrega, satisfação do
cliente (reviews), taxa de recompra e distribuição geográfica, que embasam
o relatório executivo e o Mapa de Agentes de IA propostos para a Olist.

Uso:
    python src/download_data.py   # baixa os CSVs para ./data (uma vez)
    python src/analyze.py         # roda a análise e salva ./results/analysis_results.json
"""
import json
import os

import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")


def load_data():
    """Carrega as tabelas do dataset e converte colunas de data."""
    orders = pd.read_csv(
        os.path.join(DATA_DIR, "olist_orders_dataset.csv"),
        parse_dates=[
            "order_purchase_timestamp", "order_approved_at",
            "order_delivered_carrier_date", "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ],
    )
    items = pd.read_csv(os.path.join(DATA_DIR, "olist_order_items_dataset.csv"))
    payments = pd.read_csv(os.path.join(DATA_DIR, "olist_order_payments_dataset.csv"))
    reviews = pd.read_csv(os.path.join(DATA_DIR, "olist_order_reviews_dataset.csv"))
    customers = pd.read_csv(os.path.join(DATA_DIR, "olist_customers_dataset.csv"))
    products = pd.read_csv(os.path.join(DATA_DIR, "olist_products_dataset.csv"))
    sellers = pd.read_csv(os.path.join(DATA_DIR, "olist_sellers_dataset.csv"))
    cat_translation = pd.read_csv(os.path.join(DATA_DIR, "product_category_name_translation.csv"))
    return orders, items, payments, reviews, customers, products, sellers, cat_translation


def analyze_volumetrics(orders, customers, sellers, products, result):
    """Volume geral da base: pedidos, clientes únicos, vendedores, produtos, período."""
    result["n_orders"] = int(orders["order_id"].nunique())
    result["n_customers_unique_id"] = int(customers["customer_unique_id"].nunique())
    result["n_sellers"] = int(sellers["seller_id"].nunique())
    result["n_products"] = int(products["product_id"].nunique())
    result["date_min"] = str(orders["order_purchase_timestamp"].min())
    result["date_max"] = str(orders["order_purchase_timestamp"].max())
    result["order_status_counts"] = orders["order_status"].value_counts().to_dict()
    result["pct_delivered"] = round(100 * (orders["order_status"] == "delivered").mean(), 2)


def analyze_delivery(orders, result):
    """Prazo de entrega e atraso, considerando apenas pedidos com status 'delivered'."""
    d = orders[orders["order_status"] == "delivered"].copy()
    d["delivery_days"] = (d["order_delivered_customer_date"] - d["order_purchase_timestamp"]).dt.days
    d["delay_days"] = (d["order_delivered_customer_date"] - d["order_estimated_delivery_date"]).dt.days
    d["is_late"] = d["delay_days"] > 0

    result["avg_delivery_days"] = round(d["delivery_days"].mean(), 1)
    result["median_delivery_days"] = round(d["delivery_days"].median(), 1)
    result["pct_late_orders"] = round(100 * d["is_late"].mean(), 2)
    result["avg_delay_days_when_late"] = round(d.loc[d["is_late"], "delay_days"].mean(), 1)
    return d


def analyze_reviews(reviews, d, result):
    """Nota de avaliação, distribuição de estrelas, e efeito do atraso na nota."""
    result["avg_review_score"] = round(reviews["review_score"].mean(), 2)
    result["review_score_dist"] = reviews["review_score"].value_counts().sort_index().to_dict()
    result["pct_reviews_with_comment"] = round(100 * reviews["review_comment_message"].notna().mean(), 2)
    result["pct_reviews_1_2_stars"] = round(100 * reviews["review_score"].isin([1, 2]).mean(), 2)
    result["pct_reviews_4_5_stars"] = round(100 * reviews["review_score"].isin([4, 5]).mean(), 2)

    rev_orders = d.merge(reviews[["order_id", "review_score"]], on="order_id", how="inner")
    score_by_lateness = rev_orders.groupby("is_late")["review_score"].mean().round(2).to_dict()
    result["avg_score_on_time"] = score_by_lateness.get(False)
    result["avg_score_late"] = score_by_lateness.get(True)


def analyze_repeat_purchase(orders, customers, result):
    """Taxa de recompra: usa customer_unique_id, que identifica a pessoa (não o pedido)."""
    orders_cust = orders.merge(customers[["customer_id", "customer_unique_id"]], on="customer_id", how="left")
    purchase_counts = orders_cust.groupby("customer_unique_id")["order_id"].nunique()
    result["pct_customers_single_purchase"] = round(100 * (purchase_counts == 1).mean(), 2)
    result["pct_customers_repeat_purchase"] = round(100 * (purchase_counts > 1).mean(), 2)
    result["avg_orders_per_customer"] = round(purchase_counts.mean(), 3)


def analyze_payments(payments, result):
    result["avg_payment_value"] = round(payments["payment_value"].mean(), 2)
    result["payment_type_dist"] = payments["payment_type"].value_counts().to_dict()
    result["avg_installments"] = round(payments["payment_installments"].mean(), 2)


def analyze_products(items, products, cat_translation, result):
    result["n_categories"] = int(products["product_category_name"].nunique())
    top_cats = items.merge(products[["product_id", "product_category_name"]], on="product_id", how="left")
    top_cats_count = top_cats["product_category_name"].value_counts().head(5)
    cat_map = dict(zip(cat_translation["product_category_name"], cat_translation["product_category_name_english"]))
    result["top5_categories_en"] = {cat_map.get(k, k): v for k, v in top_cats_count.to_dict().items()}


def analyze_geography(customers, d, result):
    """Distribuição por estado e cruzamento de atraso/prazo por região."""
    result["n_states"] = int(customers["customer_state"].nunique())
    top_states = customers["customer_state"].value_counts().head(5).to_dict()
    result["top5_states"] = top_states

    d_state = d.merge(customers[["customer_id", "customer_state"]], on="customer_id", how="left")
    late_by_state = d_state.groupby("customer_state")["is_late"].mean().mul(100).round(2)
    delivery_by_state = d_state.groupby("customer_state")["delivery_days"].mean().round(1)
    top_state_codes = list(top_states.keys())
    result["late_pct_by_top_state"] = {s: late_by_state.get(s) for s in top_state_codes}
    result["avg_delivery_days_by_top_state"] = {s: delivery_by_state.get(s) for s in top_state_codes}


def main():
    orders, items, payments, reviews, customers, products, sellers, cat_translation = load_data()

    result = {}
    analyze_volumetrics(orders, customers, sellers, products, result)
    delivered = analyze_delivery(orders, result)
    analyze_reviews(reviews, delivered, result)
    analyze_repeat_purchase(orders, customers, result)
    analyze_payments(payments, result)
    analyze_products(items, products, cat_translation, result)
    analyze_geography(customers, delivered, result)

    os.makedirs(RESULTS_DIR, exist_ok=True)
    out_path = os.path.join(RESULTS_DIR, "analysis_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)

    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    print(f"\nResultados salvos em {out_path}")


if __name__ == "__main__":
    main()
