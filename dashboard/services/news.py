import requests
import xml.etree.ElementTree as ET
import html
import re
import unicodedata
from urllib.parse import quote_plus
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
from typing import Optional, List

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search"

def _deaccent(s: str) -> str:
    return "".join(
        ch for ch in unicodedata.normalize("NFD", s or "")
        if unicodedata.category(ch)[0] != "M"
    )

def _clean_html_snippet(desc_html: str, source: str = "") -> str:
    if not desc_html:
        return ""
    m = re.search(r"<p>(.*?)</p>", desc_html, flags=re.DOTALL)
    if m:
        snippet_html = m.group(1)
        text = re.sub(r"<[^>]+>", " ", snippet_html)
    else:
        text = re.sub(r"<[^>]+>", " ", desc_html)
    text = html.unescape(text).replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    if source:
        text = text.replace(source, "").strip()
    return text

def fetch_news(query: str = '"Inteligência Artificial Piauí" OR "SIA Piauí"',
               country_code: str = "BR",
               language_code: str = "pt-BR",
               max_results: int = 15):
    q = quote_plus(query)
    feed_url = f"{GOOGLE_NEWS_RSS}?q={q}&hl={language_code}&gl={country_code}&ceid={country_code}:{language_code}"
    try:
        resp = requests.get(feed_url, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"Erro ao buscar RSS: {e}")
        return []

    try:
        root = ET.fromstring(resp.content)
    except ET.ParseError as e:
        print(f"Erro ao parsear XML: {e}")
        return []

    channel = root.find("channel")
    if channel is None:
        print("Estrutura RSS inesperada: <channel> ausente.")
        return []

    items = channel.findall("item")
    out = []
    for item in items[:max_results]:
        title = (item.findtext("title") or "").strip()
        link  = (item.findtext("link") or "").strip()
        pub   = (item.findtext("pubDate") or "").strip()

        # fonte
        source = ""
        ns_source = item.find("{http://news.google.com}source")
        if ns_source is not None and ns_source.text:
            source = ns_source.text.strip()
        else:
            src = item.find("source")
            if src is not None and src.text:
                source = src.text.strip()

        if source and f" - {source}" in title:
            title = title.replace(f" - {source}", "").strip()

        desc_html = item.findtext("description") or ""
        description = _clean_html_snippet(desc_html, source)

        out.append({
            "title": title,
            "link": link,
            "description": description,
            "source": source,
            "pubDate": pub
        })
    return out

def _parse_pubdate(dt: str):
    try:
        return parsedate_to_datetime(dt)
    except Exception:
        return None

def _generate_variations(base_query: str) -> List[str]:
    """
    Gera variações para Google News:
      - com/sem aspas
      - com/sem acentos
      - se contiver 'SIA', expande para formas canônicas da Secretaria + recortes regionais.
      - se NÃO contiver 'SIA', mantém a lógica leve: frase base (+ deaccent)
        e, se faltar recorte, adiciona Piauí/Piaui/PI.
    """
    base_query = (base_query or "").strip()
    if not base_query:
        return []

    # remove aspas externas para manipular
    if base_query.startswith('"') and base_query.endswith('"') and len(base_query) >= 2:
        bare = base_query[1:-1].strip()
    else:
        bare = base_query

    def add_unique(seq, v):
        v = (v or "").strip()
        if v and v not in seq:
            seq.append(v)

    variants: List[str] = []

    # Se contiver 'SIA' (sigla da Secretaria)
    if re.search(r"\bSIA\b", bare, flags=re.IGNORECASE):
        remainder = re.sub(r"\bSIA\b", "", bare, flags=re.IGNORECASE).strip()

        org_forms = [
            "SIA",
            "Secretaria da Inteligência Artificial",
            "Secretaria de Inteligência Artificial",
        ]
        region_forms = [
            "Piauí",
            "Piaui",
            "PI",
            "Governo do Piauí",
            "Governo do Estado do Piauí",
        ]

        region_present = any(r.lower() in bare.lower() for r in ["piauí", "piaui", " pi ", "governo do piauí"])

        base_phrases = []
        for org in org_forms:
            phrase = f"{org} {remainder}".strip() if remainder else org
            add_unique(base_phrases, phrase)

        if not region_present:
            for b in list(base_phrases):
                for reg in region_forms:
                    add_unique(base_phrases, f"{b} {reg}")

        for p in base_phrases:
            add_unique(variants, f'"{p}"')
            add_unique(variants, p)
            dac = _deaccent(p)
            if dac != p:
                add_unique(variants, f'"{dac}"')
                add_unique(variants, dac)

        return variants

    # ---- consultas sem 'SIA' (genérico) ----
    add_unique(variants, f'"{bare}"')
    add_unique(variants, bare)
    dac = _deaccent(bare)
    if dac != bare:
        add_unique(variants, f'"{dac}"')
        add_unique(variants, dac)

    # Se faltar recorte regional, adiciona Piauí/Piaui/PI
    if not any(p in bare for p in ["Piauí", "Piaui", " PI"]):
        for p in ["Piauí", "Piaui", "PI"]:
            add_unique(variants, f'"{bare} {p}"')
            add_unique(variants, f'{bare} {p}')
            if dac != bare:
                add_unique(variants, f'"{dac} {p}"')
                add_unique(variants, f'{dac} {p}')

    return variants

def fetch_news_multi(queries,
                     country_code: str = "BR",
                     language_code: str = "pt-BR",
                     max_per_query: int = 10,
                     total_limit: Optional[int] = 15,
                     auto_expand: bool = True):
    
    target_total = 15 if total_limit is None else total_limit
    qlist = [ (q or "").strip() for q in queries if (q or "").strip() ]
    if not qlist:
        return []

    # Preparar variações por consulta
    var_by_q = [ _generate_variations(q) if auto_expand else [q] for q in qlist ]

    quotas = [0] * len(qlist)
    for i in range(target_total):
        quotas[i % len(qlist)] += 1

    seen = set()
    combined: List[dict] = []

    def collect_from_variations(variations: List[str], per_query_cap: int):
        """Adiciona itens únicos respeitando a cota local e o limite global."""
        added = 0
        for v in variations:
            if len(combined) >= target_total or added >= per_query_cap:
                break
            items = fetch_news(
                query=v,
                country_code=country_code,
                language_code=language_code,
                max_results=max_per_query,
            )
            for it in items:
                if len(combined) >= target_total or added >= per_query_cap:
                    break
                key = (it.get("title", "").strip().lower(), it.get("source", "").strip().lower())
                if key in seen:
                    continue
                seen.add(key)
                it["_dt"] = _parse_pubdate(it.get("pubDate", ""))
                combined.append(it)
                added += 1

    # PASSO 1 — coletar até a cota de cada consulta
    for variations, cap in zip(var_by_q, quotas):
        if cap > 0:
            collect_from_variations(variations, cap)
        if len(combined) >= target_total:
            break

    # PASSO 2 — se ainda não atingiu o total, completa sem cotas
    if len(combined) < target_total:
        for variations in var_by_q:
            collect_from_variations(variations, per_query_cap=(target_total - len(combined)))
            if len(combined) >= target_total:
                break

    def _sort_key(x):
        dt = x["_dt"] or datetime.min.replace(tzinfo=timezone.utc)
        return dt
    combined.sort(key=_sort_key, reverse=True)

    combined = combined[:target_total]
    for it in combined:
        it.pop("_dt", None)

    return combined
