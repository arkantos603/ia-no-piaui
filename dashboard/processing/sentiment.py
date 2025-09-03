import re
from .text import clean_text

# Léxico (stems) — cobre variações comuns
POS_STEMS = {
    "avanc", "melhor", "sucess", "benef", "inov", "eficien", "aprov", "parcer",
    "cresci", "record", "conquist", "vit", "liberac", "reduca", "refor", "fortalec",
    "invest", "positiv", "anunci", "apresent", "cri", "desenvolv", "plataform",
    "program", "projet", "base de dados", "ranking", "posic", "lider", "capacit",
    "formac", "curso", "universidad", "laborat", "centro", "implant", "adot",
    "lançam", "lançad", "lança", "inaugur", "parceria", "primeir", "dados abert",
}
NEG_STEMS = {
    "crime", "crim", "corrup", "escandal", "roub", "desvi", "golp", "cassac",
    "cassad", "ineleg", "pris", "pres", "conden", "denunci", "investig", "acus",
    "fraud", "lavagem", "crise", "bloque", "proib", "suspens", "cancel", "irregular",
    "ilegal", "anul", "ataque", "violenc", "multa", "sanc", "apreens", "process",
    "queda", "derrot", "trag", "dano", "perda", "piora", "risco", "amea", "escassez",
    "falh", "fracass",
}

# Padrões de frases (regex)
POS_PATTERNS = [
    r"\blanc[çc]a", r"\binaugur", r"\bautoriza? (curso|cursos) superior",
    r"\bparcer", r"\bprimeir[ao]", r"\binvest", r"\bdata lake", r"\bplataform",
    r"\bbase de dados", r"\bcapacit", r"\bchamad[ao] p[úu]blica", r"\branking",
    r"\bposi[çc][aã]o", r"\bcentro", r"\blaborat[óo]rio", r"\bprogram", r"\bprojet",
    r"\bapresenta", r"\banuncia",
]
NEG_PATTERNS = [
    r"\bpris[ãa]o|\bpres[oa]\b", r"\bcassa[çc][aã]o|\bcassad", r"\binvestig",
    r"\bden[uú]ncia", r"\bgolp", r"\bfraud", r"\bconden", r"\besc[âa]ndal",
    r"\birregular", r"\bilegal", r"\bsuspens", r"\bproibi", r"\bcancel",
    r"\bmulta", r"\bsan[çc][aã]o", r"\bapreens", r"\bcrime",
]

NEGATORS = {"nao", "sem", "nunca", "jamais"}
INTENSIFIERS = {"muito", "forte", "grave", "severo", "extremo", "extremamente", "significativ", "recorde"}

def _match_stem(word: str, stems: set[str]) -> bool:
    if " " in word:
        return False
    return any(word.startswith(s) for s in stems)

def _pattern_hits(text: str, patterns) -> int:
    txt = clean_text(text)
    return sum(1 for p in patterns if re.search(p, txt))

def classify_sentiment(title: str, description: str) -> str:
    score = 0
    # padrões (bônus/penalidade)
    pos_pat = _pattern_hits(title, POS_PATTERNS) * 3 + _pattern_hits(description, POS_PATTERNS) * 2
    neg_pat = _pattern_hits(title, NEG_PATTERNS) * 3 + _pattern_hits(description, NEG_PATTERNS) * 2
    score += pos_pat - neg_pat

    # léxico com pesos e contexto (negação/intensificador)
    for text, weight in ((title, 3), (description, 1)):
        tokens = clean_text(text).split()
        n = len(tokens)
        for i, w in enumerate(tokens):
            pol = 0
            if _match_stem(w, NEG_STEMS):
                pol -= 2
            elif _match_stem(w, POS_STEMS):
                pol += 1
            if pol:
                prev_window = tokens[max(0, i-3):i]
                near_window = tokens[max(0, i-2):min(n, i+3)]
                if any(t in NEGATORS for t in prev_window):
                    pol *= -1
                if any(t in INTENSIFIERS for t in near_window):
                    pol += 1 if pol > 0 else -1
                score += weight * pol

    if score >= 1:
        return "Positivo"
    if score <= -2:
        return "Negativo"
    if (pos_pat > 0) and (neg_pat == 0):
        return "Positivo"
    return "Neutro"
