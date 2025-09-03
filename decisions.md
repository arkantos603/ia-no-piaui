# Decisões de Implementação

## 1) Por que abordagem de regras (e não ML)?
- **Simplicidade, transparência e custo**: o objetivo é um painel leve com 10–15 notícias por execução; um modelo de ML demandaria dataset rotulado, tuning e infra desproporcionais ao escopo.
- **Explicabilidade**: a regra mostra claramente o que pesou (stems/padrões positivos e negativos).
- **Trade-offs**: não captura nuances (ironia/ambiguidade). Como mitigação, ajustei pesos e padrões específicos do domínio público/educacional do Piauí.

## 2) Estratégia de busca e mesclagem
- O usuário informa **N consultas** (1–10). Cada consulta é executada **isoladamente** no RSS do Google Notícias (frase entre aspas).
- Os resultados são **mesclados** com **deduplicação por (título + fonte)**, ordenados por data e **limitados ao total solicitado** (entre 10 e 15).  
- Motivo vs. um único `OR`: maior diversidade de fontes e controle preciso do total.

## 3) Análise de sentimento (regras)
- **Ponderação**: título (peso 3) e descrição (peso 1).
- **Léxico por stems** (positivos/negativos) para cobrir variações (“lança”, “lançamento”, “lançados”…).
- **Contexto**: negação próxima inverte o sinal; intensificadores ajustam magnitude.
- **Padrões (regex)** com bônus/penalidade para frases típicas de políticas públicas (ex.: “lança”, “inaugura”, “parceria”) e de denúncia/infração (ex.: “prisão”, “cassação”, “investigado”).
- **Limiar assimétrico**: ≥ +1 → Positivo; ≤ −2 → Negativo; senão Neutro. Fallback pró-positivo quando só há padrões positivos.
- **Racional**: refletir melhor matérias de anúncio/lançamento sem superestimar negativas.

## 4) Visualização e UX
- **KPIs** (notícias, fontes, % por classe).
- **Pizza com cores fixas**: Positivo = verde, Neutro = amarelo, Negativo = vermelho.
- **Nuvem de palavras** (títulos + descrições).
- **Tabela** com índice iniciando em 1, link clicável e **botões de exportação CSV/JSON**.

## 5) Tratamento de falhas e ausência de dados
- `requests` com timeout e `ElementTree` com captura de `ParseError`.
- Em erro ou feed vazio, retorna lista vazia; o app informa ao usuário e interrompe com segurança.
- Deduplicação evita inflar o total com itens repetidos.

## 6) Arquitetura e organização
- Projeto modular em pacote `dashboard/`:
  - `services/news.py`: coleta RSS e mesclagem.
  - `processing/text.py` e `processing/sentiment.py`: limpeza e regras de sentimento.
  - `ui/…`: sidebar, KPIs, gráficos e tabela/exportação.
  - `config.py`: cores, ordem da pizza, stopwords.
- Benefícios: manutenção simples, reuso, possibilidade de novas fontes.

## 7) Performance e manutenção
- **Cache de dados** (`st.cache_data`) com TTL para reduzir requisições repetidas.
- Sem dependências pesadas (ML). Apenas `requests`, `pandas`, `plotly`, `wordcloud` e `streamlit`.

## 8) Ética e transparência
- Rodapé deixa claras as limitações e o apoio de IA na implementação.
- Reforço: não é um classificador geral de sentimento; é um **indicador heurístico** para monitoramento.