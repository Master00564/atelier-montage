"""Read a project's shape before any picture is drawn: scene lengths, and variety against past films.

    python montage/outils/structure.py montage/projets/<name> OUT_DIR MODE

Runs in every mode and writes OUT_DIR/structure.json:
  scenes[]      {"id", "debut", "duree"} from index.html (a host as long as the film is an overlay)
  precedents[]  the signatures of the last films of the same "genre" in the repo, newest first:
                read them BEFORE writing a storyboard, so the new film differs
  fautes[]      what breaks a rule; in the "rendu" mode each one is a FAILED line and stops the run
  notes[]       what needs a reason in the storyboard

Rules checked:
  length   "attendu.secondes" with the same number twice: the root's data-duration is that number;
  pace     no scene under "attendu.scene_min_s" (1.0 s); the scene before the last one lasts
           "attendu.avant_fin_min_s" (1.5 s) at least (the end of a film lands, it never
           hurries); notes for scenes under 1.2 s or over 3.0 s. The owner, 2026-11-13: « on est
           dans la génération TikTok […] mieux vaut trop de montage que pas assez »; a film sets
           other numbers in its manifest when it has a reason;
  variety  a manifest with a "genre" carries "signature": {"date", "familles", "accroche", "angle"}
           ("familles": the scene families in order, one per scene). Against the last films of the
           genre: the hook kind differs from the last two, the angle from the last one, the first
           scene after the hook from the last two, and the middle of the film (hook and end card
           left out) shares no run of 4 families with any of the last five;
  speed    no data-motion-blur="on" in the project's pages: the engine then captures the whole
           film by screenshots (205 s against 143 s for the same 20 s film, 2026-11-13);
  text     a product film ("genre": "produit") says no characteristic: in the "voix" mode a texte.txt
           with a digit, a number word, a unit or a spec word (caracteristiques(), the lists of the
           skill's duree_texte.py) is refused before the voice is generated; in the other modes it is a note;
  effects  each effect clip (every <audio> but the voice and the music) is heard at its peak
           (data-start + the loudest 5 ms of its file, read in the sound): two peaks less than "attendu.effets_ecart_s" (0.15 s) apart are one noise
           (MengTo html-explainer-video, MIT: at most two effects within 150 ms), and no peak falls
           inside a number the voice says (mots.json): the number is the one thing heard then. Every
           strong event gets its sound (the owner: « mieux vaut trop de montage que pas assez »);
           these two are the only limits on how many.
"""
import array
import json
import re
import subprocess
import sys
from pathlib import Path

COURT, AVANT_FIN, LONG, MINI = 1.2, 1.5, 3.0, 1.0
# A product film never says a characteristic (the owner, 2026-11-14: « ne parle jamais des caractéristiques,
# de sa taille […] Faut être au-delà de ça »). These two lists mirror the skill's scripts/duree_texte.py
# (NOMBRES, SPECIFICATIONS, caracteristiques()) exactly: change both together.
PRODUIT_NOMBRES = {"deux", "trois", "quatre", "cinq", "six", "sept", "huit", "dix", "onze", "douze", "treize", "quatorze",
                   "quinze", "seize", "vingt", "vingts", "trente", "quarante", "cinquante", "soixante", "septante",
                   "huitante", "nonante", "cent", "cents", "mille", "demi", "demie", "moitié", "double", "triple"}
PRODUIT_SPECIFICATIONS = re.compile(
    r"^(centim[eè]tres?|millim[eè]tres?|m[eè]tres?|cm|mm|watts?|lumens?|kelvins?|volts?|grammes?|kilos?|"
    r"kilogrammes?|litres?|pouces?|degr[eé]s?|diam[eè]tres?|hauteurs?|largeurs?|longueurs?|profondeurs?|"
    r"dimensions?|tailles?|poids|puissance|ampoules?|culots?|douilles?|leds?|watt|ip)$")
NOMBRES = {"zéro", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf", "dix", "onze", "douze", "treize",
           "quatorze", "quinze", "seize", "vingt", "vingts", "trente", "quarante", "cinquante", "soixante", "cent", "cents",
           "mille", "million", "millions", "milliard", "milliards", "demi", "moitié", "quart", "double", "triple"}


def est_nombre(mot):
    """A spoken number ("un" and "une" are left out: they are articles far more often)."""
    propre = re.sub(r"[^\wà-ÿ-]", "", mot.lower())
    return bool(re.search(r"\d", propre)) or any(p in NOMBRES for p in propre.split("-"))


def caracteristiques(texte):
    """The words of a product text that say a characteristic: any digit, a number word, a unit or a spec word."""
    refus = []
    for brut in texte.split():
        for mot in re.split(r"[-'’]", re.sub(r"[^\w'’-]", "", brut.lower())):
            if re.search(r"\d", mot) or mot in PRODUIT_NOMBRES or PRODUIT_SPECIFICATIONS.match(mot):
                refus.append(brut)
                break
    return refus


def pic(fichier):
    """Seconds from a sound file's start to its loudest 5 ms (RMS), read in the sound itself: any effect,
    from the bank or a recording, lands by its peak."""
    p = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(fichier), "-ac", "1", "-ar", "48000",
                        "-f", "s16le", "-"], capture_output=True)
    x = array.array("h", p.stdout[:len(p.stdout) // 2 * 2])
    if not x:
        return 0.0
    w, acc, meilleur, ou = 240, 0, -1, 0
    carres = [v * v for v in x]
    for i, c in enumerate(carres):
        acc += c - (carres[i - w] if i >= w else 0)
        if i >= w - 1 and acc > meilleur:
            meilleur, ou = acc, i - w + 1
    return round(ou / 48000, 3)


def effets(projet, manifeste, index):
    """The effects' peaks, and what breaks the two rules on them."""
    fautes, heures = [], []
    for balise in re.findall(r"<audio\b[^>]*>", index, re.S):
        ident, src = attribut(balise, "id") or "", attribut(balise, "src") or ""
        if ident == "voix" or ident.startswith("musique") or not src:
            continue
        debut = float(attribut(balise, "data-start") or 0)
        f = projet / src
        heures.append((round(debut + (pic(f) if f.exists() else 0.0), 3), ident))
    heures.sort()
    ecart = manifeste.get("attendu", {}).get("effets_ecart_s", 0.15)
    for (a, ia), (b, ib) in zip(heures, heures[1:]):
        if b - a < ecart:
            fautes.append(f"effects {ia} and {ib} peak {round(b - a, 3)} s apart ({ecart} s at least): one of them moves or goes")
    voix = re.search(r'<audio\b[^>]*id="voix"[^>]*>', index, re.S)
    mots_f = projet / "assets" / "mots.json"
    if voix and mots_f.exists():
        decalage = float(attribut(voix[0], "data-start") or 0)
        for m in json.loads(mots_f.read_text(encoding="utf-8")).get("mots", []):
            if not est_nombre(m["mot"]):
                continue
            for t, ident in heures:
                if m["debut"] + decalage <= t <= m["fin"] + decalage:
                    fautes.append(f"effect {ident} peaks at {t} s while the voice says « {m['mot']} »: the tick comes before, the pop after")
    return [{"t": t, "id": i} for t, i in heures], fautes


def attribut(balise, nom):
    m = re.search(rf'{nom}="([^"]*)"', balise)
    return m[1] if m else None


def scenes(index):
    racine = re.search(r'<[^>]*id="root"[^>]*>', index, re.S)
    total = float(attribut(racine[0], "data-duration")) if racine else None
    hotes = []
    for balise in re.findall(r"<[^>]*data-composition-src=[^>]*>", index, re.S):
        debut, duree = attribut(balise, "data-start"), attribut(balise, "data-duration")
        if debut is None or duree is None or (total and float(duree) >= 0.9 * total):
            continue
        hotes.append({"id": attribut(balise, "id"), "debut": float(debut)})
    hotes.sort(key=lambda h: h["debut"])
    for h, suivant in zip(hotes, hotes[1:] + [{"debut": total}]):
        h["duree"] = round((suivant["debut"] if suivant["debut"] is not None else h["debut"]) - h["debut"], 3)
    return total, hotes


def suite_commune(a, b):
    """Length of the longest run of families the two lists share, in the same order."""
    meilleur, ligne = 0, [0] * (len(b) + 1)
    for x in a:
        nouvelle = [0] * (len(b) + 1)
        for j, y in enumerate(b):
            if x == y:
                nouvelle[j + 1] = ligne[j] + 1
                meilleur = max(meilleur, nouvelle[j + 1])
        ligne = nouvelle
    return meilleur


def main():
    projet, sortie, mode = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
    manifeste = json.loads((projet / "montage.json").read_text(encoding="utf-8"))
    fautes, notes, r = [], [], {"scenes": [], "precedents": []}

    texte_f = projet / manifeste.get("voix", {}).get("texte", "texte.txt")
    if manifeste.get("genre") == "produit" and texte_f.exists():
        dits = caracteristiques(texte_f.read_text(encoding="utf-8"))
        r["caracteristiques"] = dits
        if dits:
            faute = (f"a product film says no characteristic, and {texte_f.name} says « {' '.join(dits)} »: tell what the "
                     "product gives, never its size, figures or specs (scenes.md)")
            if mode == "voix":
                print(f"::error::FAILED: {faute}")
                sys.exit(1)
            notes.append(faute)

    index = projet / "index.html"
    if index.exists():
        total, r["scenes"] = scenes(index.read_text(encoding="utf-8"))
        voulu = manifeste.get("attendu", {}).get("secondes")
        if voulu and voulu[0] == voulu[1] and total is not None and abs(total - voulu[0]) > 0.0005:
            fautes.append(f"the film must last exactly {voulu[0]} s and the root's data-duration is {total}")
        mini = manifeste.get("attendu", {}).get("scene_min_s", MINI)
        avant_fin = manifeste.get("attendu", {}).get("avant_fin_min_s", AVANT_FIN)
        for s in r["scenes"]:
            if s["duree"] < mini:
                fautes.append(f"scene {s['id']} lasts {s['duree']} s ({mini} s at least): make it a second state of its neighbour")
            elif s["duree"] < COURT:
                notes.append(f"scene {s['id']} lasts {s['duree']} s, under {COURT} s: its reason is in the storyboard")
            elif s["duree"] > LONG:
                notes.append(f"scene {s['id']} lasts {s['duree']} s, over {LONG} s: it has a second and a third state on spoken words")
        if len(r["scenes"]) >= 4 and mini <= r["scenes"][-2]["duree"] < avant_fin:
            fautes.append(f"scene {r['scenes'][-2]['id']}, the one before the last, lasts {r['scenes'][-2]['duree']} s ({avant_fin} s at least): "
                          "the end of a film slows down, it never hurries")
        r["effets"], f_effets = effets(projet, manifeste, index.read_text(encoding="utf-8"))
        fautes += f_effets

    for page in sorted(projet.rglob("*.html")):
        if re.search(r'data-motion-blur="on"', page.read_text(encoding="utf-8")):
            fautes.append(f'{page.relative_to(projet).as_posix()}: data-motion-blur="on" moves the whole render to the slow screenshot '
                          "capture; give the fast mover its own directional blur (effets.md, recipe 5)")

    genre, signature = manifeste.get("genre"), manifeste.get("signature")
    if genre:
        anciens = []
        for autre in sorted(projet.parent.iterdir()):
            f = autre / "montage.json"
            if autre.name == projet.name or not f.exists():
                continue
            m = json.loads(f.read_text(encoding="utf-8"))
            if m.get("genre") == genre and m.get("signature"):
                anciens.append({"projet": autre.name, **m["signature"]})
        anciens.sort(key=lambda s: (s.get("date", ""), s["projet"]), reverse=True)
        r["precedents"] = anciens[:5]
        if index.exists() and not signature:
            fautes.append('montage.json has a "genre" and no "signature" (date, familles, accroche, angle)')
        elif signature:
            familles = signature.get("familles", [])
            if r["scenes"] and len(familles) != len(r["scenes"]):
                fautes.append(f"signature.familles lists {len(familles)} families for {len(r['scenes'])} scenes")
            milieu = familles[1:-1]
            for rang, a in enumerate(r["precedents"]):
                autre = a.get("familles", [])[1:-1]
                if rang < 2 and str(signature.get("accroche", "")).lower() == str(a.get("accroche", "")).lower():
                    fautes.append(f"same hook kind « {a.get('accroche')} » as {a['projet']}: open another way")
                if rang < 1 and str(signature.get("angle", "")).lower() == str(a.get("angle", "")).lower():
                    fautes.append(f"same angle « {a.get('angle')} » as {a['projet']}, the film before: tell another thing about the subject")
                if rang < 2 and milieu and autre and milieu[0] == autre[0]:
                    fautes.append(f"the scene after the hook is a {milieu[0]} again, as in {a['projet']}")
                if suite_commune(milieu, autre) >= 4:
                    fautes.append(f"4 scene families or more in the same order as {a['projet']}: change the order or the families")

    r["fautes"], r["notes"] = fautes, notes
    sortie.mkdir(parents=True, exist_ok=True)
    (sortie / "structure.json").write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"scenes": len(r["scenes"]), "precedents": [a["projet"] for a in r["precedents"]], "fautes": fautes, "notes": notes},
                     ensure_ascii=False))
    if mode == "rendu":
        for f in fautes:
            print(f"::error::FAILED: {f}")
        sys.exit(1 if fautes else 0)


if __name__ == "__main__":
    main()
