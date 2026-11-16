"""Pick the best voices of a multi-speaker engine from its measured first take.

    python voix/choisir.py DIR ENGINE [--hommes 3] [--femmes 1]

Prints the chosen voice names, one per line. Score = UTMOS x (1 - WER) on the
"lettres" take. Gender: the one stated by the voice's source when there is one (GENRES),
else the pitch median (below 165 Hz = man). Voices with a missing measure are skipped.
"""
import argparse
import json
from pathlib import Path

SEUIL_HOMME_HZ = 165
_F, _M = "femme", "homme"
# Gender stated by each voice's source: preset ids (Supertonic M/F, Kokoro ff_), Suno's
# Bark speaker list, voice names (Pocket TTS uses female and male names), our own text
# descriptions. Voices not listed (Piper MLS, CML-TTS, MeloTTS) fall back on pitch.
GENRES = {
    **{f"M{i}": _M for i in range(1, 6)}, **{f"F{i}": _F for i in range(1, 6)},
    "ff_siwis": _F, "tom": _M, "css10": _M,
    **{v: _F for v in ("estelle", "alba", "anna", "azelma", "eponine", "eve", "fantine", "jane", "mary",
                       "vera", "caro_davy", "lola", "Christine", "femme-decrit",
                       "unmute-prod-website/developpeuse-3.wav")},
    **{v: _M for v in ("charles", "george", "michael", "paul", "bill_boerst", "peter_yearsley", "stuart_bell",
                       "javert", "marius", "giovanni", "Daniel", "homme-decrit", "Ryan", "Aiden",
                       "unmute-prod-website/fabieng-enhanced-v2.wav", "voice-donations/Hugo_the_frenchie_enhanced.wav")},
    **{f"v2/fr_speaker_{i}": (_F if i in (1, 2, 5) else _M) for i in range(10)},
}


def score(r):
    return r["utmos"] * (1 - min(r["wer"], 1))


def genre(r):
    return GENRES.get(r["voix"]) or (_M if r["f0_median_hz"] < SEUIL_HOMME_HZ else _F)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("dossier", type=Path)
    ap.add_argument("moteur")
    ap.add_argument("--hommes", type=int, default=3)
    ap.add_argument("--femmes", type=int, default=1)
    a = ap.parse_args()
    mesures = json.loads((a.dossier / "mesures.json").read_text(encoding="utf-8")).values()
    prets = [r for r in mesures if r["moteur"] == a.moteur and r["prise"] == "lettres"
             and r.get("utmos") is not None and r.get("wer") is not None and r.get("f0_median_hz")]
    prets.sort(key=score, reverse=True)
    for g, n in (("homme", a.hommes), ("femme", a.femmes)):
        for r in [r for r in prets if genre(r) == g][:n]:
            print(r["voix"])


if __name__ == "__main__":
    main()
