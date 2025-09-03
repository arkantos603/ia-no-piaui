import streamlit as st

def sidebar_params():
    with st.sidebar:
        st.header("Parâmetros de Coleta")

        n_consultas = st.slider("Número de consultas", 1, 10, 2,
                                help="Quantas frases você quer somar na busca")
        defaults = ["Inteligência Artificial Piauí", "SIA Piauí"]
        termos = []
        for i in range(n_consultas):
            valor_default = defaults[i] if i < len(defaults) else ""
            termo = st.text_input(f"Consulta {i+1}", value=valor_default, key=f"q{i}")
            termos.append((termo or "").strip())

        # controla a quantidade de notícias
        total_n = st.slider("Quantidade de notícias", 10, 15, 15, 1)

    shown_terms = [t for t in termos if t]
    if not shown_terms:
        st.warning("Adicione pelo menos **1** consulta na barra lateral para iniciar a busca.")
        st.stop()

    return shown_terms, total_n
