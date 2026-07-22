# Análise de Dados — Olist Intelligent Marketplace

Análise exploratória em Python do **Brazilian E-Commerce Public Dataset by Olist**,
desenvolvida para a **Fase 1** do Tech Challenge — IA para Devs.

Este repositório documenta, de forma reproduzível, como os achados apresentados no
[relatório executivo](#) foram obtidos — sem estimativas, apenas processamento real
sobre os 99.441 pedidos do dataset público da Olist (2016–2018).

## Estrutura do repositório

```
olist-ia-agentic-analysis/
├── data/                    # CSVs do dataset (baixados via download_data.py, não versionados)
├── notebooks/
│   └── analise_olist.ipynb  # notebook com o passo a passo, os resultados e os gráficos
├── results/
│   ├── analysis_results.json  # saída consolidada da análise, em JSON
│   └── figures/              # os 7 gráficos da análise, em PNG
├── src/
│   ├── download_data.py     # baixa o dataset
│   ├── analyze.py           # roda a análise completa e gera o JSON de resultados
│   └── generate_charts.py   # gera e salva os 7 gráficos em results/figures/
├── requirements.txt
└── README.md
```

## Gráficos

O notebook e `generate_charts.py` produzem 7 gráficos, salvos em `results/figures/`:

1. Distribuição do prazo de entrega
2. Distribuição das notas de avaliação (1-5 estrelas)
3. Nota média: pedido no prazo vs. atrasado
4. Taxa de recompra (compra única vs. recompra)
5. Distribuição das formas de pagamento
6. Top 8 categorias de produto por volume de itens vendidos
7. Taxa de atraso por estado (top 6 em volume de pedidos)

## Como reproduzir

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Baixar o dataset (gera os CSVs em ./data)
python src/download_data.py

# 3. Rodar a análise completa (gera ./results/analysis_results.json)
python src/analyze.py

# 4. Gerar os gráficos (salva PNGs em ./results/figures)
python src/generate_charts.py

# 5. (Opcional) Abrir o notebook para ver o passo a passo com explicações e gráficos
jupyter notebook notebooks/analise_olist.ipynb
```

## Fonte dos dados

Dataset público: [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
(Kaggle). Como o download oficial exige login no Kaggle, `download_data.py` busca os
mesmos arquivos CSV em um mirror público no GitHub. Se preferir, baixe manualmente do
Kaggle e coloque os CSVs na pasta `data/`.

## Principais achados

| Métrica | Resultado |
|---|---|
| Pedidos analisados | 99.441 (set/2016 a out/2018) |
| Clientes únicos | 96.096 |
| Prazo médio de entrega | 12,1 dias (mediana 10) |
| Pedidos atrasados | 6,8% |
| Nota média — pedido no prazo | 4,28 |
| Nota média — pedido atrasado | 2,26 |
| Avaliações 1-2 estrelas | 15,1% |
| Avaliações com comentário escrito | 41,8% |
| **Taxa de recompra** | **apenas 3,1%** dos clientes compram mais de uma vez |
| Ticket médio | R$ 154,10 |

Esses achados embasam diretamente o **Mapa de Agentes de IA** proposto (Atendimento,
Reviews, Logística e Churn) e a priorização de oportunidades descrita no relatório
executivo da Fase 1.

## Ferramentas

- Python 3
- [pandas](https://pandas.pydata.org/) para carregamento, tratamento e cruzamento dos dados
- Jupyter Notebook para documentar a análise de forma reproduzível

## Projeto

Tech Challenge — Fase 1 — Fundamentos de IA e Agentic AI
Case: Olist Intelligent Marketplace
