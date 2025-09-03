import streamlit as st
import plotly.express as px
from wordcloud import WordCloud
from ..config import COLOR_MAP, PIE_ORDER, STOPWORDS_PT
from ..processing.text import clean_text

def render_sentiment_pie(df):
    st.header("Distribuição de Sentimentos")

    counts = (
        df["sentimento"]
          .value_counts()
          .reindex(PIE_ORDER)
          .dropna()
          .reset_index()
    )
    counts.columns = ["Sentimento", "Quantidade"]

    fig = px.pie(
        counts,
        names="Sentimento",
        values="Quantidade",
        title="Sentimentos nas Notícias",
        color="Sentimento",
        color_discrete_map=COLOR_MAP,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig, use_container_width=True)

def render_wordcloud(df):
    st.header("Nuvem de Palavras (Títulos + Descrições)")
    all_text = " ".join((clean_text(t) for t in (df["title"].fillna("") + " " + df["description"].fillna(""))))
    wc = WordCloud(width=1000, height=400, background_color="white", stopwords=STOPWORDS_PT).generate(
        all_text or "ia piaui tecnologia dados governo pesquisa projetos sia"
    )
    st.image(wc.to_array(), caption="Termos mais frequentes", use_container_width=True)
