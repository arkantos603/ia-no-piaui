# Monitoramento de Percepção Pública sobre IA no Piauí

Painel em **Streamlit** para monitorar menções a **Inteligência Artificial no Piauí** via RSS do Google Notícias, com **análise de sentimento baseada em regras** e identificação de termos recorrentes.

## Funcionalidades
- **Coleta (RSS Google Notícias)**: várias consultas informadas pelo usuário; resultados **mesclados** com **deduplicação**.
- **Controle de total**: o usuário escolhe **10–15 notícias** (total) para exibir.
- **Processamento/Limpeza** de textos (remoção de HTML e normalização).
- **Análise de Sentimento** por **regras** (stems, padrões, negação, intensificadores).
- **Visualização**:
  - **KPIs** (contagens e percentuais),
  - **Gráfico de pizza** (cores fixas: verde/positivo, azul/neutro, vermelho/negativo),
  - **Nuvem de palavras**,
  - **Tabela interativa** (link clicável).
- **Exportação**: **CSV** e **JSON** com os itens coletados e classificados.
- **Ética/Transparência**: aviso no rodapé sobre limitações e uso de IA no desenvolvimento.

## Requisitos
- Python 3.8+
- Acesso à Internet (para coletar as notícias)

## Instalação
```bash
pip install -r requirements.txt

depois é só rodar streamlit run app.py