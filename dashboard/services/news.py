import requests
import xml.etree.ElementTree as ET
import html
import re
from urllib.parse import quote_plus
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
from typing import Optional

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search"

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

def fetch_news_multi(queries,
                     country_code: str = "BR",
                     language_code: str = "pt-BR",
                     max_per_query: int = 10,
                     total_limit: Optional[int] = 15):
    seen = set()
    combined = []

    for q in queries:
        q = (q or "").strip()
        if not q:
            continue
        # cada consulta isolada; aspas para frase exata
        if q.startswith('"') and q.endswith('"') and len(q) >= 2:
            q_inner = q[1:-1]
        else:
            q_inner = q
        q_expr = f'"{q_inner}"'

        items = fetch_news(query=q_expr,
                           country_code=country_code,
                           language_code=language_code,
                           max_results=max_per_query)
        for it in items:
            key = (it.get("title", "").strip().lower(), it.get("source", "").strip().lower())
            if key in seen:
                continue
            seen.add(key)
            it["_dt"] = _parse_pubdate(it.get("pubDate", ""))
            combined.append(it)

    # ordenar do mais recente; sem data vão para o fim
    def _sort_key(x):
        dt = x["_dt"] or datetime.min.replace(tzinfo=timezone.utc)
        return dt
    combined.sort(key=_sort_key, reverse=True)

    if total_limit is None:
        total_limit = 15
    combined = combined[:total_limit]

    for it in combined:
        it.pop("_dt", None)

    return combined
