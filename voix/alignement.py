"""Word timing shared by the voice check (voix/aligner.py) and the theme video build (scripts/theme.py).

Whisper hears "1925" where the script says "mille neuf cent vingt-cinq", "Rulmane" where the
screen says "Ruhlmann": every text is first turned into plain spoken words (digits spelled out,
accents and punctuation dropped), then the two word lists are matched in order. Each word of the
first list gets the time span of the words it matched; a word that matched nothing gets the time
between its neighbours. Pure Python + num2words.
"""
import difflib
import re
import unicodedata

from num2words import num2words

_NOMBRE = re.compile(r"\d{1,3}(?:[   ]\d{3})+|\d+(?:[,.]\d+)?")


def _nombre(m):
    t = re.sub(r"[   ]", "", m[0])
    if re.search(r"[,.]", t):
        a, b = re.split(r"[,.]", t)
        return f" {num2words(int(a), lang='fr')} virgule {num2words(int(b), lang='fr')} "
    return f" {num2words(int(t), lang='fr')} "


def parle(texte):
    """The words a reader says, normalised: 'Le 28 avril' -> ['le', 'vingt', 'huit', 'avril']."""
    t = texte.lower().replace("’", "'").replace("œ", "oe").replace("æ", "ae")
    t = _NOMBRE.sub(_nombre, t)
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.findall(r"[a-z]+", t.replace("'", " ").replace("-", " "))


def jetons(texte):
    """Display tokens (what is printed, punctuation attached) with their spoken words. Only ordinary
    spaces separate tokens: a no-break space keeps "250 000" or "New York" in one piece."""
    return [(j, parle(j)) for j in re.split(r"[ \t\r\n]+", texte.strip()) if j]


def caler(attendus, entendus):
    """attendus: list of spoken words; entendus: list of (word, start, end) already normalised.
    Returns one (start, end) per expected word, every one filled, in order."""
    a, b = list(attendus), [m for m, _, _ in entendus]
    temps = [None] * len(a)
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            for k in range(i2 - i1):
                temps[i1 + k] = (entendus[j1 + k][1], entendus[j1 + k][2])
        elif op == "replace":
            debut, fin = entendus[j1][1], entendus[j2 - 1][2]
            poids = [max(1, len(m)) for m in a[i1:i2]]
            total, t = sum(poids), debut
            for k, p in enumerate(poids):
                d = (fin - debut) * p / total
                temps[i1 + k] = (t, t + d)
                t += d
    # Words never heard: spread between the neighbours that were.
    i = 0
    while i < len(temps):
        if temps[i] is not None:
            i += 1
            continue
        j = i
        while j < len(temps) and temps[j] is None:
            j += 1
        gauche = temps[i - 1][1] if i > 0 else (temps[j][0] if j < len(temps) else 0.0)
        droite = temps[j][0] if j < len(temps) else gauche
        pas = (droite - gauche) / (j - i)
        for k in range(i, j):
            temps[k] = (gauche + pas * (k - i), gauche + pas * (k - i + 1))
        i = j
    return temps


def entendus_de(mots_whisper):
    """Whisper words [{'mot','debut','fin'}] -> normalised (word, start, end), a heard word
    that normalises to several ('1925') sharing its span."""
    sortie = []
    for m in mots_whisper:
        parts = parle(m["mot"])
        if not parts:
            continue
        pas = (m["fin"] - m["debut"]) / len(parts)
        sortie += [(p, m["debut"] + k * pas, m["debut"] + (k + 1) * pas) for k, p in enumerate(parts)]
    return sortie


def caler_texte(texte, mots_whisper):
    """Each display token of `texte` with its (start, end), from Whisper's words."""
    toks = jetons(texte)
    plats = [p for _, ps in toks for p in ps]
    t = caler(plats, entendus_de(mots_whisper))
    sortie, k = [], 0
    for j, ps in toks:
        if ps:
            sortie.append((j, t[k][0], t[k + len(ps) - 1][1]))
            k += len(ps)
        else:  # a lone sign ("…", "«"): glued to the previous word's time
            prev = sortie[-1][2] if sortie else 0.0
            sortie.append((j, prev, prev))
    return sortie
