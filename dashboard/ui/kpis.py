import streamlit as st

def render_kpis(df, shown_terms):
    st.subheader("Visão geral")

    total = len(df)
    fontes = df["source"].nunique()

    pos = (df["sentimento"] == "Positivo").sum()
    neg = (df["sentimento"] == "Negativo").sum()
    neu = (df["sentimento"] == "Neutro").sum()

    pct = lambda x: (x / total * 100) if total else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📰 Notícias", total)
    with col2:
        st.metric("🗞️ Fontes únicas", fontes)
    with col3:
        st.metric("✅ Positivas", f"{pos} ({pct(pos):.0f}%)")
    with col4:
        st.metric("❗ Negativas", f"{neg} ({pct(neg):.0f}%)")

    colA, colB = st.columns(2)
    with colA:
        st.metric("🟦 Neutras", f"{neu} ({pct(neu):.0f}%)")
    with colB:
        st.metric("🔎 Consultas usadas", len(shown_terms))

    st.divider()
