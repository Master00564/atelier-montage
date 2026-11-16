"""Give a generated take one constant pace, at the speed the manifest asks, with short breaths.

    python montage/outils/cadence.py montage/projets/<name> OUT_DIR [RAW_TAKE] [WORDS.json]

A text-to-speech voice does not keep its pace: it hurries some groups of words (third test: « Vous
allumez, » and « Soixante-dix centimètres, » at 9 syllables a second in a take that runs at 5.4) and
it breathes too long between sentences (up to 1.4 s of nothing). The owner hears both: « parfois on
dirait qu'elle est beaucoup trop rapide. Faut bien qu'elle reste à 1,2 constamment […] pas
d'accélération, de sursaut », and « des gros blancs […] j'en veux pas ».

So the take is rebuilt breath group by breath group (a group = the sound between two measured
silences; its length is read in the sound, not in the word times, which run late on short groups):
  - the take's usual pace is the median rate of its groups; played at "voix.vitesse" it is the
    target, never above "voix.debit_max" (5.5 syllables a second by default);
  - every group of three syllables or more gets what brings it to the target, exactly: a hurried
    group is slowed (0.6 at the least: under that the voice drags), a slow one is sped up, but by
    "voix.accelere_max" (1.35) at the most, whatever "voix.vitesse" is under it. No group ends
    faster than the target: that is the constant pace. Why the cap: the counter of syllables merges
    a hiatus (« nuage » counts one), so a short group can read up to a fifth slower than it is said,
    and a stretched voice past 1.35 is heard. Measured on five raw takes (2026-11-14): the slow
    groups are the opening line (2.5 to 3.2 syllables a second) and one held sentence a take, at
    0.57 to 0.70 of the target with the old rule (1.2 for them); with the cap at 1.35 they reach
    0.64 to 0.79, the others the target;
  - a group of one or two syllables is measured coarsely: it is held back only when it is clearly
    rushed (1.25 times the target), and never under 0.75;
  - every silence is cut by what ends the group before it, counted in the result: 0.30 s after a
    full stop ("voix.pause_max"), 0.20 s after a comma, 0.45 s after a question or an exclamation
    (short-video editors keep 0.2 to 0.3 s; research of 2026-11-13, recherche/web/TIKTOK-ET-IA);
    half before the cut, half after, taken from the take's own silence, each stretch faded 4 ms.
The pitch is kept (FFmpeg atempo), the sibilants are tamed (DESSIFLE) and the whole is brought to -16 LUFS.

Reads OUT_DIR/voix-brute.wav and OUT_DIR/brut/mots.json unless other files are given.
Writes OUT_DIR/voix.mp3 (160 kb/s, 44.1 kHz) and OUT_DIR/cadence.json. The words of the result are
timed afterwards by mots.py, which reuses debits() to report the pace of any take.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

VOYELLES = "aeiouyàâäéèêëîïôöùûüœ"
SYLLABES_MIN = 3    # under this a group's rate cannot be measured (a name, two words)
ECART = 1.15        # a group faster than this times the usual pace is reported as hurried
PLAFOND = 5.5       # syllables a second no group should pass once played ("voix.debit_max" overrides it)
RALENTI_MIN = 0.6   # a group is never slowed under this
ACCELERE_MAX = 1.35  # a slow group is never sped up past this ("voix.accelere_max")
COURT = 1.25        # a group of one or two syllables is held back only past this times the target...
COURT_MIN = 0.75    # ...and never slowed under this
PAUSE_MAX = 0.30    # seconds of silence left after a full stop, in the result ("voix.pause_max")
PAUSE_VIRGULE = 0.20  # after a comma, a semicolon, a colon, or no punctuation at all
PAUSE_QUESTION = 0.45  # after a question or an exclamation: the beat before the answer
FONDU = 0.004       # each stretch fades in and out: a cut in a silence must not click
AMORCE = 0.25       # silence kept before the first word, and after the last one
# The generated voice hisses: in the fifth test the "s" of « s'allume » was the film's loudest accent
# (earshot: +44 dB over the bed, 6.9 kHz) and the 4-8 kHz share of the film (-11.0 dB) sat over all of
# earshot's reference films (-31.8 to -11.6). FFmpeg's de-esser, measured on that take (2026-11-14):
# intensity 0.3 cuts the sibilant peaks 6 dB (presence share of the voice -10.2 -> -12.3 dB), 0.4 cuts
# them 9.5 dB (-16.9) and takes 1.5 dB off the 1-4 kHz share that earshot also read high, 0.5 dulls the
# voice (mid share -12.9, presence -20.3). Kept: 0.4.
DESSIFLE = "deesser=i=0.4:m=0.5:f=0.5"


def echec(message):
    print(f"::error::FAILED: {message}")
    sys.exit(1)


def syllabes(mot):
    """Spoken syllables of a French word, counted as groups of vowels (a mute final e is not one)."""
    m = re.sub(r"[^a-zàâäéèêëîïôöùûüœç]", "", re.split(r"['’]", mot.lower())[-1])
    if len(m) > 2 and not m.endswith(("ée", "ées")):
        m = re.sub(r"es?$", "", m) or m
    return max(1, len(re.findall(f"[{VOYELLES}]+", m)))


def debits(mots, pauses):
    """Breath groups of a timed take: words between two measured silences, with their rate.

    A group's sound runs from the end of the silence before it to the start of the silence after
    it; the word times only say which words it holds (and bound a group no silence touches)."""
    limites = set()
    for p in pauses:
        i = next((k for k, m in enumerate(mots) if m["debut"] >= p["fin"] - 0.05), None)
        if i:
            limites.add(i)
    groupes, bornes = [], sorted(limites) + [len(mots)]
    for debut, fin in zip([0] + bornes[:-1], bornes):
        g = mots[debut:fin]
        avant = next((p for p in reversed(pauses) if p["fin"] <= g[0]["debut"] + 0.15 and g[0]["debut"] - p["fin"] < 0.4), None)
        apres = next((p for p in pauses if g[-1]["debut"] < p["debut"] <= g[-1]["fin"] + 0.3), None)
        t0 = avant["fin"] if avant else g[0]["debut"]
        t1 = apres["debut"] if apres else g[-1]["fin"]
        n = sum(syllabes(m["mot"]) for m in g)
        groupes.append({"texte": " ".join(m["mot"] for m in g), "mots": [debut, fin - 1], "debut": round(t0, 3),
                        "fin": round(t1, 3), "syllabes": n, "debit": round(n / max(t1 - t0, 0.1), 2)})
    return groupes


def reference(groupes):
    """The take's usual pace: median rate of its groups, each weighted by its syllables."""
    utiles = sorted((g for g in groupes if g["syllabes"] >= SYLLABES_MIN), key=lambda g: g["debit"])
    if not utiles:
        return None
    moitie, cumul = sum(g["syllabes"] for g in utiles) / 2, 0
    for g in utiles:
        cumul += g["syllabes"]
        if cumul >= moitie:
            return g["debit"]


def main():
    projet, sortie = Path(sys.argv[1]), Path(sys.argv[2])
    brut = Path(sys.argv[3]) if len(sys.argv) > 3 else sortie / "voix-brute.wav"
    mots_f = Path(sys.argv[4]) if len(sys.argv) > 4 else sortie / "brut" / "mots.json"
    voix = json.loads((projet / "montage.json").read_text(encoding="utf-8")).get("voix") or echec("montage.json has no voix")
    vitesse = float(voix.get("vitesse", 1))
    if not 0.8 <= vitesse <= 1.5:
        echec(f"voix.vitesse {vitesse}: between 0.8 and 1.5")
    pause_max = float(voix.get("pause_max", PAUSE_MAX))
    lu = json.loads(mots_f.read_text(encoding="utf-8"))
    groupes = debits(lu["mots"], lu["pauses"])
    ref = reference(groupes)

    plafond = float(voix.get("debit_max", PLAFOND))
    cible = min(ref * vitesse, plafond) if ref else plafond
    accelere_max = max(vitesse, float(voix.get("accelere_max", ACCELERE_MAX)))
    for g in groupes:
        g["vitesse"] = vitesse
        if g["syllabes"] >= SYLLABES_MIN:
            g["vitesse"] = round(min(max(RALENTI_MIN, cible / g["debit"]), accelere_max), 3)
        # One or two syllables: the measure is coarse, so only a clear rush is held back, and less far.
        elif g["syllabes"] < SYLLABES_MIN and g["debit"] * vitesse > COURT * cible:
            g["vitesse"] = round(max(COURT_MIN, cible / g["debit"]), 3)
    for g in groupes:
        g["debit_final"] = round(g["debit"] * g["vitesse"], 2)

    # One stretch per group: its sound, with half of the allowed silence on each side (counted in the
    # result, so it is that much longer in a take that will be played faster).
    fin_du_son = float(lu.get("duree_s") or groupes[-1]["fin"] + AMORCE)
    filtres, noms, coupes = [], [], []
    def pause_apres(groupe):
        dernier = groupe["texte"].rstrip(" »\"”)")[-1:]
        return PAUSE_QUESTION if dernier in "?!" else pause_max if dernier in ".…" else min(PAUSE_VIRGULE, pause_max)

    for i, g in enumerate(groupes):
        avant = groupes[i - 1]["fin"] if i else 0.0
        apres = groupes[i + 1]["debut"] if i + 1 < len(groupes) else fin_du_son
        marge_avant = min((g["debut"] - avant) / 2 if i else g["debut"],
                          (pause_apres(groupes[i - 1]) / 2 if i else AMORCE) * g["vitesse"])
        marge_apres = min((apres - g["fin"]) / 2 if i + 1 < len(groupes) else apres - g["fin"],
                          (pause_apres(g) / 2 if i + 1 < len(groupes) else AMORCE) * g["vitesse"])
        a, b = round(max(0.0, g["debut"] - marge_avant), 3), round(g["fin"] + max(0.0, marge_apres), 3)
        coupes.append({"debut": a, "fin": b, "vitesse": g["vitesse"]})
        duree = (b - a) / g["vitesse"]
        filtres.append(f"[0:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS,atempo={g['vitesse']},"
                       f"afade=t=in:d={FONDU},afade=t=out:st={max(0.0, duree - FONDU):.4f}:d={FONDU}[s{i}]")
        noms.append(f"[s{i}]")
    filtres.append(f"{''.join(noms)}concat=n={len(noms)}:v=0:a=1,{DESSIFLE},loudnorm=I=-16:TP=-1.5:LRA=11[voix]")
    sortie.mkdir(parents=True, exist_ok=True)
    p = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(brut), "-filter_complex", ";".join(filtres),
                        "-map", "[voix]", "-ar", "44100", "-b:a", "160k", str(sortie / "voix.mp3")], capture_output=True, text=True)
    if p.returncode:
        echec(f"FFmpeg could not even the take: {p.stderr[-300:]}")

    duree = round(sum((c["fin"] - c["debut"]) / c["vitesse"] for c in coupes), 3)
    silence_retire = round(fin_du_son - sum(c["fin"] - c["debut"] for c in coupes), 3)
    bilan = {"vitesse": vitesse, "debit_habituel": ref, "debit_vise_au_plus": round(cible, 2), "pause_max": pause_max,
             "duree_prevue_s": duree, "silence_retire_s": silence_retire, "troncons": coupes,
             "groupes": [{k: g[k] for k in ("texte", "syllabes", "debit", "vitesse", "debit_final")} for g in groupes],
             "retenus": [g["texte"] for g in groupes if g["vitesse"] < vitesse],
             "pousses": [g["texte"] for g in groupes if g["vitesse"] > vitesse]}
    (sortie / "cadence.json").write_text(json.dumps(bilan, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: bilan[k] for k in ("vitesse", "debit_habituel", "duree_prevue_s", "silence_retire_s", "retenus", "pousses")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
