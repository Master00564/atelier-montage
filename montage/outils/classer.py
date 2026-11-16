"""Rank downloaded sound candidates with earshot: which one sounds most like what the film needs.

    python montage/outils/classer.py OUT_DIR CANDIDATES

CANDIDATES: a JSON file or the JSON text itself (ecoute.yml passes its input `classer`), written by the
skill's scripts/cherche_son.py: {"requete": "a single light switch click", "candidats": [{"id", "url", "licence", "page", ...}]}.
Each url is downloaded (https, from the Openverse sources only), then earshot ranks them all against the
query (calibrated z: >= 3 strong), judges each with realness (a recording or code-made) and finds the
cleanest moment of a one-shot (find: start / end trims, head and tail cut flags).
A list of such objects ranks each one in turn (OUT_DIR/classement-<k>/).
Writes OUT_DIR/classement-<k>/classement.json and OUT_DIR/classement.txt, best first, licence and source
page beside each.
"""
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

HOTES = {"cdn.freesound.org", "freesound.org", "prod-1.storage.jamendo.com", "upload.wikimedia.org"}


def classer(api, demande, sortie):
    dossier = sortie / "candidats"
    dossier.mkdir(parents=True, exist_ok=True)
    fiches = {}
    for c in demande["candidats"]:
        u = urllib.parse.urlparse(c["url"])
        if u.scheme != "https" or u.hostname not in HOTES:
            print(f"skipped {c['url']}: not an Openverse source over https")
            continue
        ext = Path(u.path).suffix if Path(u.path).suffix in (".mp3", ".wav", ".flac", ".ogg", ".m4a") else ".mp3"
        cible = dossier / f"{c['id']}{ext}"
        requete = urllib.request.Request(c["url"], headers={"User-Agent": "atelier-video/1.0"})
        with urllib.request.urlopen(requete, timeout=60) as r:
            cible.write_bytes(r.read())
        fiches[cible.name] = c
    rang = api.rank([str(p) for p in sorted(dossier.iterdir())], demande["requete"])
    lignes = [f"{demande['requete']}: {rang['summary']}"]
    out = []
    for x in rang["results"]:
        c = fiches.get(x["name"], {})
        reel = api.realness(x["path"])
        bout = api.find(x["path"], demande["requete"], top=1)
        meilleur = (bout.get("segments") or [{}])[0]
        ligne = {**c, "fichier": x["name"], "z": x["z"], "verdict": x["verdict"], "sonne_comme": x["sounds_most_like"],
                 "p_real": round(float(reel["p_real"]), 2), "reel": reel["verdict"],
                 "extrait": {k: meilleur.get(k) for k in ("start", "end", "kind", "head_db", "tail_db", "cut") if k in meilleur}}
        out.append(ligne)
        lignes.append(f"  z {x['z']:+.2f} {x['verdict']:<9} p_real {ligne['p_real']:.2f}  {str(c.get('titre', x['name']))[:40]:40} "
                      f"{c.get('licence', '?'):<8} {c.get('page', '')}  trim {ligne['extrait']}")
    (sortie / "classement.json").write_text(json.dumps({"requete": demande["requete"], "classement": out}, ensure_ascii=False, indent=1),
                                            encoding="utf-8")
    return lignes


def main():
    sortie, source = Path(sys.argv[1]), sys.argv[2]
    demandes = json.loads(Path(source).read_text(encoding="utf-8") if Path(source).is_file() else source)
    from earshot import api
    lignes = []
    for k, d in enumerate(demandes if isinstance(demandes, list) else [demandes], 1):
        lignes += classer(api, d, sortie / f"classement-{k}")
    sortie.mkdir(parents=True, exist_ok=True)
    (sortie / "classement.txt").write_text("\n".join(lignes) + "\n", encoding="utf-8")
    print("\n".join(lignes))


if __name__ == "__main__":
    main()
