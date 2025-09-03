import streamlit as st
import pandas as pd

def render_table_with_exports(df):
    st.header("Tabela de Notícias")
    df_display = df[["title", "sentimento", "source", "pubDate", "link", "description"]].copy()
    df_display.columns = ["Título", "Sentimento", "Fonte", "Data", "Link", "Descrição"]

    # índice iniciando em 1
    df_display.index = pd.RangeIndex(start=1, stop=len(df_display) + 1)
    df_display.index.name = "Nº"

    # Exportação
    st.subheader("Exportar dados (CSV/JSON)")
    csv_bytes = df_display.to_csv(index=False).encode("utf-8-sig")
    json_str = df_display.to_json(orient="records", force_ascii=False).encode("utf-8")
    colA, colB = st.columns(2)
    with colA:
        st.download_button("📄 Baixar CSV", csv_bytes, "noticias_processadas.csv", "text/csv")
    with colB:
        st.download_button("🧾 Baixar JSON", json_str, "noticias_processadas.json", "application/json")

    st.dataframe(
        df_display,
        use_container_width=True,
        column_config={
            "Link": st.column_config.LinkColumn("Link", display_text="Abrir matéria"),
            "Descrição": st.column_config.TextColumn("Descrição", width="large"),
        },
        hide_index=False,
    )
