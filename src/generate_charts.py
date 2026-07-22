"""
generate_charts.py
-------------------
Gera os gráficos da análise exploratória do dataset da Olist e salva como
PNG em ./results/figures. Deve ser executado depois de analyze.py (usa os
mesmos dados de ./data).

Uso:
    python src/generate_charts.py
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
FIG_DIR = os.path.join(os.path.dirname(__file__), "..", "results", "figures")

NAVY = "#1B2A4A"
TEAL = "#0F6E6A"
PINK = "#C2185B"
GRAY = "#8A94A6"

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "#D9DEE6",
    "axes.grid": True,
    "grid.color": "#EDEFF3",
    "grid.linewidth": 0.8,
    "font.size": 11,
})


def load_data():
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
    cat_translation = pd.read_csv(os.path.join(DATA_DIR, "product_category_name_translation.csv"))
    return orders, items, payments, reviews, customers, products, cat_translation


def savefig(fig, name):
    os.makedirs(FIG_DIR, exist_ok=True)
    path = os.path.join(FIG_DIR, name)
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"  -> {path}")


def chart_delivery_days(delivered):
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.hist(delivered["delivery_days"].clip(upper=60), bins=40, color=TEAL, edgecolor="white")
    ax.axvline(delivered["delivery_days"].median(), color=PINK, linestyle="--", linewidth=1.6,
               label=f"Mediana: {delivered['delivery_days'].median():.0f} dias")
    ax.set_title("Distribuição do prazo de entrega", fontsize=13, fontweight="bold", color=NAVY)
    ax.set_xlabel("Dias entre compra e entrega")
    ax.set_ylabel("Nº de pedidos")
    ax.legend(frameon=False)
    savefig(fig, "01_distribuicao_prazo_entrega.png")


def chart_review_score_dist(reviews):
    counts = reviews["review_score"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(7, 4.2))
    bars = ax.bar(counts.index.astype(str), counts.values, color=[PINK, PINK, GRAY, TEAL, TEAL])
    for b in bars:
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 800, f"{b.get_height():,}",
                ha="center", fontsize=9, color=NAVY)
    ax.set_title("Distribuição das notas de avaliação (reviews)", fontsize=13, fontweight="bold", color=NAVY)
    ax.set_xlabel("Nota (estrelas)")
    ax.set_ylabel("Nº de avaliações")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
    savefig(fig, "02_distribuicao_notas_reviews.png")


def chart_score_by_lateness(delivered, reviews):
    rev_orders = delivered.merge(reviews[["order_id", "review_score"]], on="order_id", how="inner")
    means = rev_orders.groupby("is_late")["review_score"].mean()
    labels = ["No prazo", "Atrasado"]
    values = [means.get(False, 0), means.get(True, 0)]
    fig, ax = plt.subplots(figsize=(5.5, 4.2))
    bars = ax.bar(labels, values, color=[TEAL, PINK], width=0.55)
    for b, v in zip(bars, values):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.08, f"{v:.2f}", ha="center", fontsize=12, fontweight="bold", color=NAVY)
    ax.set_ylim(0, 5.4)
    ax.set_title("Nota média: pedido no prazo vs. atrasado", fontsize=13, fontweight="bold", color=NAVY)
    ax.set_ylabel("Nota média (1-5)")
    savefig(fig, "03_nota_media_por_pontualidade.png")


def chart_repeat_purchase(orders, customers):
    orders_cust = orders.merge(customers[["customer_id", "customer_unique_id"]], on="customer_id", how="left")
    counts = orders_cust.groupby("customer_unique_id")["order_id"].nunique()
    single = (counts == 1).sum()
    repeat = (counts > 1).sum()
    fig, ax = plt.subplots(figsize=(5.5, 4.2))
    wedges, texts, autotexts = ax.pie(
        [single, repeat], labels=["Compra única", "Recompra (2+)"], colors=[GRAY, TEAL],
        autopct="%1.1f%%", startangle=90, textprops={"fontsize": 11},
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
    )
    for t in autotexts:
        t.set_color("white")
        t.set_fontweight("bold")
    ax.set_title("Clientes: compra única vs. recompra", fontsize=13, fontweight="bold", color=NAVY)
    savefig(fig, "04_taxa_recompra.png")


def chart_top_categories(items, products, cat_translation):
    top_cats = items.merge(products[["product_id", "product_category_name"]], on="product_id", how="left")
    top5 = top_cats["product_category_name"].value_counts().head(8)
    top5.index = [c.replace("_", " ").title() if isinstance(c, str) else c for c in top5.index]
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.barh(top5.index[::-1], top5.values[::-1], color=NAVY)
    ax.set_title("Top 8 categorias de produto por volume de itens vendidos", fontsize=13, fontweight="bold", color=NAVY)
    ax.set_xlabel("Nº de itens vendidos")
    savefig(fig, "05_top_categorias.png")


def chart_state_delay(delivered, customers):
    top_states = customers["customer_state"].value_counts().head(6).index.tolist()
    d_state = delivered.merge(customers[["customer_id", "customer_state"]], on="customer_id", how="left")
    late_by_state = d_state.groupby("customer_state")["is_late"].mean().mul(100).reindex(top_states)
    fig, ax = plt.subplots(figsize=(7, 4.2))
    bars = ax.bar(top_states, late_by_state.values, color=PINK)
    for b, v in zip(bars, late_by_state.values):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.2, f"{v:.1f}%", ha="center", fontsize=10, color=NAVY)
    ax.set_title("Taxa de atraso por estado (top 6 em volume de pedidos)", fontsize=13, fontweight="bold", color=NAVY)
    ax.set_ylabel("% de pedidos atrasados")
    savefig(fig, "06_atraso_por_estado.png")


def chart_payment_type(payments):
    counts = payments["payment_type"].value_counts()
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    ax.bar(counts.index, counts.values, color=TEAL)
    ax.set_title("Distribuição das formas de pagamento", fontsize=13, fontweight="bold", color=NAVY)
    ax.set_ylabel("Nº de transações")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
    savefig(fig, "07_formas_pagamento.png")


def main():
    print("Carregando dados...")
    orders, items, payments, reviews, customers, products, cat_translation = load_data()

    delivered = orders[orders["order_status"] == "delivered"].copy()
    delivered["delivery_days"] = (delivered["order_delivered_customer_date"] - delivered["order_purchase_timestamp"]).dt.days
    delivered["delay_days"] = (delivered["order_delivered_customer_date"] - delivered["order_estimated_delivery_date"]).dt.days
    delivered["is_late"] = delivered["delay_days"] > 0

    print("Gerando gráficos em ./results/figures ...")
    chart_delivery_days(delivered)
    chart_review_score_dist(reviews)
    chart_score_by_lateness(delivered, reviews)
    chart_repeat_purchase(orders, customers)
    chart_top_categories(items, products, cat_translation)
    chart_state_delay(delivered, customers)
    chart_payment_type(payments)
    print("\nConcluído.")


if __name__ == "__main__":
    main()
