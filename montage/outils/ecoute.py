"""Listen to a rendered film with earshot (MIT, https://github.com/Leonxlnx/earshot), models loaded once.

    python montage/outils/ecoute.py FILM.mp4 OUT_DIR [--projet montage/projets/<name>] [--detail low] [--moities]
    python montage/outils/ecoute.py FILM.mp4 OUT_DIR --projet montage/projets/<name> --portes

Nobody can hear the film before it is delivered, and level gates alone passed films the owner still
heard wrong (2026-11-14). earshot listens: CLAP (laion/larger_clap_general, Apache-2.0) and the
AudioSet tagger AST (MIT/ast-finetuned-audioset, BSD-3), both on the CPU, at earshot's pinned revisions.

Cues come from structure.json next to the film (written by structure.py at render time): every scene
start ("scene") and every effect peak ("sfx"). With --projet, the voice's words (assets/mots.json,
shifted by the voice clip's data-start in index.html) give its spoken groups and its breaths.

Writes in OUT_DIR:
  ecoute.json   everything, machine-readable: timeline (events with times, levels and tags, sections,
                loudness curve, beat grid, picture cuts, sync of every cut and cue), measure, critique,
                a description of every effect, breath and voiceless stretch, the voice's groups, the
                versions and the time of each step
  ecoute.png    earshot's annotated sheet of the whole film; with --moities, ecoute-1.png and ecoute-2.png its halves
  ecoute.txt    the short summary: meters, critique verdict and rows, the segments, the transcript
critique's scorecard compares with 7 launch films (kinetic type, UI demos), not a narrated product
film: read its rows as hints, never as gates, except the one below.

With --portes (the render job, before the copies: no model is loaded, about half a minute; the
listening above runs in a parallel job of the same run, ecoute.yml), two gates, each one a FAILED
line and a non-zero exit, writing portes.json; each caught a
defect heard in a delivered film (fifth test, 2026-11-14, research ECOUTE-SONS-2026-11-14.md):
  effects   every effect clip of the project passes earshot's model-free take audit (no click at the
            edges, no clipping, no metallic comb ring, no cut tail): the code-made pops of the fifth
            test clicked (pop-1: edge -34 dB, ring z 192, tail cut at -36 dB; pop-2, impact-1);
  sibilance the presence band (4-8 kHz) holds no larger share of the film than in any of earshot's
            reference films (critique row "presence 4-8 kHz share" not "high"): the fifth test's
            share was -11.0 dB (references -31.8 to -11.6) and its loudest accent was the "s" of
            « s'allume » (+44 dB, 6.9 kHz); the voice chain now de-esses (cadence.py).
Everything else is reported: sync of the effects to their cues against chance, cuts with no sound,
the critique's other rows, the descriptions.
"""
import argparse
import importlib.metadata as meta
import json
import re
import sys
import time
from pathlib import Path

SOUFFLE_MIN = 0.08   # a gap between two words this long or longer is a breath: the music rises in it (lit_musique.py)


def attribut(balise, nom):
    m = re.search(rf'{nom}="([^"]*)"', balise)
    return m[1] if m else None


def reperes(structure):
    """earshot cues from structure.json: scene starts (the first one is the film's start, not a cut) and effect peaks."""
    if not structure.exists():
        return []
    s = json.loads(structure.read_text(encoding="utf-8"))
    cues = [{"t": x["debut"], "kind": "scene", "id": x["id"]} for x in s.get("scenes", []) if x["debut"] > 0]
    cues += [{"t": x["t"], "kind": "sfx", "id": x["id"]} for x in s.get("effets", [])]
    return sorted(cues, key=lambda c: c["t"])


def voix(projet):
    """The voice's spoken groups and breaths in film time, from the project's mots.json and index.html."""
    if not projet:
        return None
    mots_f, index_f = projet / "assets" / "mots.json", projet / "index.html"
    if not (mots_f.exists() and index_f.exists()):
        return None
    clip = re.search(r'<audio\b[^>]*id="voix"[^>]*>', index_f.read_text(encoding="utf-8"), re.S)
    decalage = float(attribut(clip[0], "data-start") or 0) if clip else 0.0
    mots = [{"mot": m["mot"], "debut": round(m["debut"] + decalage, 3), "fin": round(m["fin"] + decalage, 3)}
            for m in json.loads(mots_f.read_text(encoding="utf-8")).get("mots", [])]
    groupes, souffles = [], []
    for m in mots:
        if groupes and m["debut"] - groupes[-1]["fin"] < SOUFFLE_MIN:
            groupes[-1]["fin"], groupes[-1]["texte"] = m["fin"], groupes[-1]["texte"] + " " + m["mot"]
        else:
            if groupes:
                souffles.append({"debut": groupes[-1]["fin"], "fin": m["debut"]})
            groupes.append({"debut": m["debut"], "fin": m["fin"], "texte": m["mot"]})
    return {"decalage": decalage, "mots": mots, "groupes": groupes, "souffles": souffles}


def segments(cues, v, duree):
    """The stretches to describe one by one: each effect, each breath, the stretch after the last word."""
    out = [{"genre": "sfx", "id": c["id"], "debut": round(max(0.0, c["t"] - 0.15), 3), "fin": round(min(duree, c["t"] + 0.35), 3)}
           for c in cues if c["kind"] == "sfx"]
    if v:
        out += [{"genre": "souffle", "id": f"souffle-{i + 1}", "debut": round(max(0.0, s["debut"] - 0.05), 3),
                 "fin": round(min(duree, s["fin"] + 0.05), 3)} for i, s in enumerate(v["souffles"])]
        if v["groupes"] and duree - v["groupes"][-1]["fin"] >= 0.3:
            out.append({"genre": "sans voix", "id": "apres-la-voix", "debut": v["groupes"][-1]["fin"], "fin": duree})
        if v["groupes"] and v["groupes"][0]["debut"] >= 0.3:
            out.append({"genre": "sans voix", "id": "avant-la-voix", "debut": 0.0, "fin": v["groupes"][0]["debut"]})
    return sorted(out, key=lambda s: s["debut"])


def mot_sous(t, v):
    if not v:
        return None
    return next((m["mot"] for m in v["mots"] if m["debut"] <= t <= m["fin"]), None)


AUDIT_BLOQUANT = ("clicks", "edge", "clipping", "ring", "truncated", "silent")


def effets_du_projet(projet):
    """The effect files the project plays: every <audio> but the voice and the music, as staged in assets/."""
    index = (projet / "index.html").read_text(encoding="utf-8")
    out = []
    for balise in re.findall(r"<audio\b[^>]*>", index, re.S):
        ident, src = attribut(balise, "id") or "", attribut(balise, "src") or ""
        if ident == "voix" or ident.startswith("musique") or not src:
            continue
        out.append((ident, projet / src))
    return out


def portes(api, crit, projet):
    echecs, effets = [], []
    for ident, f in effets_du_projet(projet) if projet else []:
        if not f.exists():
            echecs.append(f"effect {ident}: {f.name} is not in the project's assets")
            continue
        a = api.sfx_check(str(f))
        bloque = [w for w in a["warnings"] if w["code"] in AUDIT_BLOQUANT]
        effets.append({"id": ident, "fichier": f.name, "audit": a["summary"], "bloque": [w["code"] for w in bloque]})
        if bloque:
            echecs.append(f"effect {ident} ({f.name}) fails earshot's take audit: " + "; ".join(w["msg"] for w in bloque)
                          + ": take a bank sound (scripts/place_effets.py)")
    presence = next((m for m in crit.get("metrics", []) if m.get("metric") == "band_presence"), None)
    if presence and presence.get("status") == "high":
        echecs.append(f"sibilant voice: the 4-8 kHz share is {presence['value']} dB, over every reference film "
                      f"({presence['range'][0]} to {presence['range'][1]} dB): the take was not de-essed (cadence.py)")
    return echecs, effets


def version(dist):
    try:
        return meta.version(dist)
    except meta.PackageNotFoundError:
        return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("film")
    p.add_argument("sortie")
    p.add_argument("--projet")
    p.add_argument("--detail", default="high", choices=["low", "normal", "high"])
    p.add_argument("--portes", action="store_true",
                   help="the render job's gates only, no model: effects audit, sibilance (portes.json)")
    p.add_argument("--moities", action="store_true", help="also the two half-film sheets (ecoute-1.png, ecoute-2.png)")
    a = p.parse_args()
    film, sortie = Path(a.film), Path(a.sortie)
    projet = Path(a.projet) if a.projet else None
    sortie.mkdir(parents=True, exist_ok=True)

    from earshot import api
    from earshot.critique import critique_text
    from earshot.mcp_server import measure_summary
    from earshot.report import _clean

    temps, debut = {}, time.time()

    def top(nom):
        nonlocal debut
        temps[nom] = round(time.time() - debut, 1)
        debut = time.time()

    if a.portes:
        # Model-free (no CLAP, no AudioSet tagger): the critique's band shares and the take audit.
        crit = api.critique(str(film), use_ast=False, use_realness=False)
        echecs, effets = portes(api, crit, projet)
        top("portes")
        metrique = {m.get("metric"): m.get("value") for m in crit.get("metrics", [])}
        r = {"film": film.name, "echecs": echecs, "effets": effets, "presence_4_8k_db": metrique.get("band_presence"),
             "mid_1_4k_db": metrique.get("band_mid"), "lufs": metrique.get("lufs_i"), "temps_s": temps}
        (sortie / "portes.json").write_text(json.dumps(_clean(r), ensure_ascii=False, indent=1), encoding="utf-8")
        print(json.dumps(_clean(r), ensure_ascii=False))
        for e in echecs:
            print(f"::error::FAILED: {e}")
        sys.exit(1 if echecs else 0)

    doc = api.doctor(fetch_missing=True)
    top("modeles")
    cues = reperes(film.parent / "structure.json")
    v = voix(projet)
    tl = api.timeline(str(film), cues={"events": cues} if cues else None, detail=a.detail)
    top("timeline")
    api.sheet(str(film), str(sortie / "ecoute.png"), cues={"events": cues} if cues else None, detail=a.detail,
              width=2400, tl=tl)
    moitie = round(tl["duration"] / 2, 2)
    for n, (de, a_) in enumerate(((0, moitie), (moitie, tl["duration"])) if a.moities else (), 1):
        api.sheet(str(film), str(sortie / f"ecoute-{n}.png"), cues={"events": cues} if cues else None,
                  start=de, end=a_, detail=a.detail, width=2400)
    top("planches")
    mesure = api.measure(str(film), music=True)
    top("mesure")
    crit = api.critique(str(film))
    top("critique")
    segs = segments(cues, v, tl["duration"])
    for s in segs:
        d = api.describe(str(film), start=s["debut"], end=s["fin"])
        s["description"] = d.get("summary")
        s["tags"] = d.get("top_tags")
        s["audioset"] = d.get("audioset")
        s["mesures"] = d.get("measurements")
        c = next((c for c in cues if c.get("id") == s["id"]), None)
        if c:
            s["mot_sous_le_pic"] = mot_sous(c["t"], v)
    top("segments")

    r = {"film": film.name, "detail": a.detail, "cues": cues, "voix": v, "timeline": tl, "mesure": mesure,
         "critique": crit, "segments": segs, "temps_s": temps,
         "versions": {k: version(k) for k in ("earshot", "torch", "transformers", "numpy", "librosa")},
         "modeles": {k: doc.get(k) for k in ("models_cached", "threads", "precision", "problems")}}
    (sortie / "ecoute.json").write_text(json.dumps(_clean(r), ensure_ascii=False, indent=1), encoding="utf-8")

    lignes = [f"ECOUTE {film.name} (earshot {r['versions']['earshot']}, detail {a.detail}; temps {temps})",
              "MESURE " + measure_summary(mesure), "", "TIMELINE " + str(tl.get("summary", "")), "",
              critique_text(crit), "", "SEGMENTS (effects at their peak, breaths, voiceless stretches)"]
    for s in segs:
        mot = f" sur « {s['mot_sous_le_pic']} »" if s.get("mot_sous_le_pic") else ""
        lignes.append(f"  {s['debut']:6.2f}-{s['fin']:6.2f} {s['genre']} {s['id']}{mot}: {s['description']}")
    lignes += ["", "TRANSCRIPT", str(tl.get("text", ""))]
    (sortie / "ecoute.txt").write_text("\n".join(lignes) + "\n", encoding="utf-8")
    print("\n".join(lignes[:8]))


if __name__ == "__main__":
    main()
