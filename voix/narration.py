"""The narration of a theme video job (jobs/*.json with a "theme" key), in reading order.

    python voix/narration.py JOB.json --texte      text the TTS reads (one call, one take)
    python voix/narration.py JOB.json --reglage    "engine voice seed seed…" for voix/lancer.sh
    python voix/narration.py JOB.json --prise      the committed take (theme.voix.fichier) and its sample name

Each line has "dit" (what the voice says, respelled if the TTS needs it) and "ecran" (what is
printed). A looping video ("boucle": true) opens on line 0, the hook, and ends on the last line,
which leads into it ("… et c'est pour ça que"): the TTS reads lines 1…n then line 0, so the join
is spoken as one sentence; scripts/theme.py later cuts the take at that join and turns it around.
"""
import argparse
import json
import sys
from pathlib import Path


def lire(job):
    data = json.loads(Path(job).read_text(encoding="utf-8"))
    theme = data.get("theme")
    if not isinstance(theme, dict) or not theme.get("lignes"):
        sys.exit(f"{job}: no theme.lignes")
    return theme


def ordre(theme):
    """Lines in reading order (indexes into theme['lignes'])."""
    n = len(theme["lignes"])
    return list(range(1, n)) + [0] if theme.get("boucle") else list(range(n))


def texte(theme):
    return " ".join(theme["lignes"][i]["dit"].strip() for i in ordre(theme))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("job")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--texte", action="store_true")
    g.add_argument("--reglage", action="store_true")
    g.add_argument("--prise", action="store_true")
    a = ap.parse_args()
    theme = lire(a.job)
    if a.texte:
        print(texte(theme))
    elif a.prise:
        v = theme["voix"]
        print(v["fichier"], f"{v['moteur']}__{v['voix']}__narration-g{v.get('graines', [0])[0]}.wav")
    else:
        v = theme["voix"]
        print(v["moteur"], v["voix"], *[str(s) for s in v.get("graines", [0])])


if __name__ == "__main__":
    main()
