import re
import unicodedata

def strip_accents(s: str) -> str:
    s = unicodedata.normalize("NFD", s or "")
    return "".join(ch for ch in s if unicodedata.category(ch)[0] != "M")

def clean_text(t: str) -> str:
    t = strip_accents((t or "").lower())
    t = re.sub(r"\W+", " ", t)
    return t.strip()
