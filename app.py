import streamlit as st
import pandas as pd
from dashboard.ui.sidebar import sidebar_params
from dashboard.services.news import fetch_news_multi
from dashboard.processing.sentiment import classify_sentiment
from dashboard.ui.kpis import render_kpis
from dashboard.ui.charts import render_sentiment_pie, render_wordcloud
from dashboard.ui.table import render_table_with_exports

st.set_page_config(page_title="Monitoramento IA no Piauí", page_icon="🤖", layout="wide")
st.title("Painel de Monitoramento de Percepção Pública sobre IA no Piauí")

# Sidebar (consultas + total)
shown_terms, total_n = sidebar_params()

with st.expander("Consultas enviadas ao Google News (RSS)"):
    st.code("\n".join(f'- "{t}"' for t in shown_terms))

# Coleta (mescla consultas; total limitado pelo slider)
@st.cache_data(ttl=900)
def cached_fetch(terms, total):
    return fetch_news_multi(terms, max_per_query=total, total_limit=total)

with st.spinner("Buscando notícias (múltiplas consultas)..."):
    news_items = cached_fetch(shown_terms, total_n)

if not news_items:
    st.error("Nenhuma notícia encontrada ou ocorreu um erro na coleta de dados.")
    st.stop()

df = pd.DataFrame(news_items)

if len(df) < total_n:
    st.info(f"Foram encontradas apenas **{len(df)}** notícias para as consultas informadas (de **{total_n}** solicitadas).")

# Sentimento por regras
df["sentimento"] = df.apply(lambda r: classify_sentiment(r.get("title", ""), r.get("description", "")), axis=1)

# KPIs
render_kpis(df, shown_terms)

# Gráficos
render_sentiment_pie(df)   # pizza com cores personalizadas
render_wordcloud(df)       # nuvem de palavras

# Tabela + exportação
render_table_with_exports(df)

st.markdown("---")
st.caption(
    "Esta análise de sentimento é baseada em regras simples e pode não capturar sarcasmo ou contextos complexos. "
    "Partes do código foram desenvolvidas com o auxílio de um modelo de IA e validados por um profissional."
)
