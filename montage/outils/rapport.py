"""Measure a rendered montage, since nobody watches or listens before delivery.

    python montage/outils/rapport.py montage/projets/<name> VIDEO.mp4 OUT_DIR

Writes OUT_DIR/rapport.json, contact sheets (2 frames per second, 8 x 3 per sheet, so frame k of
sheet n shows second (n * 24 + k) / 2) and son.png. Gates, each one a FAILED line and a non-zero exit:
  size and frame rate equal montage.json "format"; picture length inside "attendu.secondes"
  [min, max] (the same number twice = that length to the frame);
  a sound track when the project has sound; loudness -15 to -13 LUFS (the master step, master.py, brings
  every film to -14, short-video practice; the fourth test was delivered at -16.1 and earshot's critique
  asked for +2.1 dB) and true peak <= -1 dBTP;
  no blank: the sound never stays under -35 dB for "attendu.blanc_max_s" (0.4 s) or more (the
  owner: « des gros blancs où pendant 1 à 2 secondes il n'y avait plus aucun bruit, j'en veux pas »);
  the voice stands clear of the music, and the music is there: in every spoken group (mots.json),
  between 300 Hz and 4 kHz, the voice sits "attendu.voix_sur_musique_db" (9 dB) or more over the
  music (a voice-led practice of https://prompt-motion.com/rossaxbt-3085b7), and the median of
  those groups is "attendu.lit_sous_voix_max_db" (14 dB) at most; in every pause of
  "attendu.souffle_min_s" (0.6 s) or more the film's sound is "attendu.souffle_sous_voix_max_db" (10 dB)
  or less under the voice (shorter breaths are not lifted: the music stays level through a sentence,
  and a 0.2 s breath at 11 dB under the voice is no blank), and
  before the first word and after the last "attendu.sans_voix_sous_voix_max_db" (8 dB) or less (the
  owner wants the music in every breath). Voice and music are measured on the project's own clips
  (<audio id="voix">, ids starting with "musique") at the levels the engine plays them; the breaths
  on the film itself. Calibrated 2026-11-14 on the two delivered narrated films the owner found
  too faint: essai-triola-3 (median 22.1 dB, breaths to 24.5, end card 25.2) and essai-orvane-4
  (median 18.9, breaths 9.2 to 17.4, end 9.4): both fail; scripts/lit_musique.py aims at 11, 7
  and 5;
  the music never pumps: its volume (data-volume x its lane, fades aside) never moves more than
  "attendu.pompe_max_db" (4 dB) within 0.2 s. The fifth test lifted it +7 to +11 dB in 57-80 ms in
  every breath and opened it at full for 0.17 s before a -13 dB drop: heard, and seen by earshot as a
  "short swell" in each breath (ecoute.json, 2026-11-14). The lane is read, not the sound: a piano
  note's own attack is music, not pumping;
  the music never stops mid-phrase: the clip that plays to the film's end fades out over
  "attendu.fondu_fin_min_s" (0.8 s) or more (the fifth test cut its rising strings in 0.25 s);
  a hook: inside the first "attendu.accroche_s" (2 s) the picture changes for good: at least
  "attendu.accroche_images" (8) frames well above the film's own floor (twice its median change:
  grain alone is the floor), or a change spread over more frames whose sum above the floor reaches
  "attendu.accroche_energie" (15): a room that lights up in half a second is a hook too, and a
  count of strong frames alone refused it (fourth test, 2026-11-14);
  a first frame that is not empty (it is the thumbnail on social players);
  rhythm, read in the picture itself (lively, never frantic):
    nothing still for "attendu.gel_max_s" (1 s) or more before the last "attendu.fin_calme_s" (3 s,
    the end card's hold); no two hard cuts less than "attendu.coupes_min_s" (0.4 s) apart; strong
    motion on "attendu.mouvement_fort_max" (0.4) of the frames at most; no flicker
    (brightness going back and forth twice or more in one second: this one has no setting);
  no single frame that jumps: a frame unlike both its neighbours while they are alike (its change
    in and out both over SAUT times the change between the frames around it) is a glitch, unless
    its time is listed in "attendu.sauts_voulus" (the bulb that flickers on, effets.md recipe 2).
    Calibrated 2026-11-14 on three delivered films: the two designed flickers measured 2.2 and 2.4,
    every other frame 1.3 at most.
  The numbers in "attendu" are where a narrated film starts, not walls: a fast edit cut on the
  music sets its own, and says why in its review.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

IMMOBILE = 0.2   # mean change of a frame (0-255, grey copy 320 px high) under which only grain moves
FORT = 8.0       # mean change of a frame inside a transition or a fast move
COUPE = 12.0     # a hard cut: one frame at this change or more, 3 times its neighbours
BASCULE = 25.0   # a brightness swing: 10 % of the scale, the flash threshold of WCAG 2.3.1
SAUT = 2.0       # a single frame that jumps: its change in and out over this many times the change across it
HAUT = 320       # the measured picture's height
SR = 48000


def run(*args):
    return subprocess.run(args, capture_output=True, text=True)


def gris(video, largeur, hauteur):
    """Every frame as a grey picture HAUT px high (the same copy for every measure of the picture)."""
    l = max(2, round(largeur * HAUT / hauteur / 2) * 2)
    p = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(video), "-map", "0:v:0",
                        "-vf", f"scale={l}:{HAUT},format=gray", "-f", "rawvideo", "-"], capture_output=True)
    return np.frombuffer(p.stdout, np.uint8).reshape(-1, HAUT, l).astype(np.float32)


def changes(images):
    """Per frame: mean change from the frame before (0 for the first), and from the frame two before."""
    m, d2 = np.zeros(len(images)), np.zeros(len(images))
    if len(images) > 1:
        m[1:] = np.abs(images[1:] - images[:-1]).mean(axis=(1, 2))
    if len(images) > 2:
        d2[1:-1] = np.abs(images[2:] - images[:-2]).mean(axis=(1, 2))
    return m, d2


def accroche(debut, plancher, attendu):
    """The hook, from the changes of the first frames against the film's floor: (measures, failure or None)."""
    voulu, fenetre = attendu.get("accroche_images", 8), attendu.get("accroche_s", 2.0)
    fortes = sum(1 for m in debut if m > max(2 * plancher, plancher + 1.0))
    energie = sum(max(0.0, m - plancher) for m in debut)
    r = {"images_fortes": fortes, "energie": round(float(energie), 1), "plancher": round(float(plancher), 2)}
    if fortes < voulu and energie < attendu.get("accroche_energie", 15):
        return r, (f"no hook: in the first {fenetre} s, {fortes} frames of clear change ({voulu} wanted) and a change of "
                   f"{round(float(energie), 1)} above the film's floor ({attendu.get('accroche_energie', 15)} wanted): the strong "
                   "move, the change or the result comes inside the first 2 s (a switch-on in 6 frames or fewer, a push front-loaded "
                   "on its first 3 frames)")
    return r, None


def sauts(m, d2, plancher, ips, voulus):
    """Single frames unlike both neighbours while those are alike (a glitch, or a flicker nobody declared)."""
    trouves = []
    for i in range(1, len(m) - 1):
        entree, sortie = m[i], m[i + 1]
        if min(entree, sortie) > plancher + 1.0 and min(entree, sortie) >= SAUT * max(d2[i], 0.3):
            t = round(i / ips, 3)
            trouves.append({"t": t, "rapport": round(float(min(entree, sortie) / max(d2[i], 0.3)), 1),
                            "voulu": any(abs(t - v) <= 0.1 for v in voulus)})
    return trouves


def rythme(m, d2, lumiere, ips, attendu):
    """What the motion of the picture says, and what breaks « lively, never frantic »."""
    echecs, n, pas = [], len(m), max(1, round(ips))
    total = n / ips
    mouvement = [float(x) for x in m]
    r = {"par_seconde": [round(sum(mouvement[i:i + pas]) / len(mouvement[i:i + pas]), 2) for i in range(0, n, pas)]}

    immobiles, debut = [], None
    for i, x in enumerate(mouvement + [IMMOBILE]):
        if x < IMMOBILE and debut is None:
            debut = i
        elif x >= IMMOBILE and debut is not None:
            if (i - debut) / ips >= 1.0:
                immobiles.append({"debut": round(debut / ips, 2), "duree": round((i - debut) / ips, 2)})
            debut = None
    r["immobiles"] = immobiles
    limite, corps = attendu.get("gel_max_s", 1.0), total - attendu.get("fin_calme_s", 3.0)
    for g in immobiles:
        avant_la_fin = min(g["debut"] + g["duree"], corps) - g["debut"]
        if avant_la_fin >= limite:
            echecs.append(f"nothing moves for {round(avant_la_fin, 2)} s from {g['debut']} s (limit {limite} s): "
                          "give the scene a slow move or a second state")

    plancher = float(np.median(m)) if n else 0.0
    r["accroche"], faute = accroche(mouvement[:round(attendu.get("accroche_s", 2.0) * ips)], plancher, attendu)
    echecs += [faute] if faute else []

    coupes = [round(i / ips, 2) for i in range(1, n - 1)
              if mouvement[i] >= COUPE and mouvement[i] > 3 * max(mouvement[i - 1], mouvement[i + 1], 0.5)]
    r["coupes_franches"] = coupes
    ecart = attendu.get("coupes_min_s", 0.4)
    for a, b in zip(coupes, coupes[1:]):
        if b - a < ecart:
            echecs.append(f"two hard cuts {round(b - a, 2)} s apart, at {a} s and {b} s ({ecart} s at least)")

    r["part_mouvement_fort"] = round(sum(1 for x in mouvement if x >= FORT) / max(n, 1), 3)
    plafond = attendu.get("mouvement_fort_max", 0.4)
    if r["part_mouvement_fort"] > plafond:
        echecs.append(f"strong motion on {r['part_mouvement_fort']:.0%} of the frames ({plafond:.0%} at most): fewer or shorter moves")

    r["sauts"] = sauts(m, d2, plancher, ips, attendu.get("sauts_voulus", []))
    for s in r["sauts"]:
        if not s["voulu"]:
            echecs.append(f"a single frame jumps at {s['t']} s (unlike both neighbours, {s['rapport']} times the change across it): "
                          "a glitch to find on the frames around it, or a designed flicker to list in attendu.sauts_voulus")

    # A swing: the brightness leaves its last extreme by BASCULE or more, in the other direction.
    bascules, repere, sens = [], lumiere[0] if len(lumiere) else 0.0, 0
    for i, v in enumerate(lumiere):
        if sens != 0 and (v - repere) * sens > 0:
            repere = v
        elif abs(v - repere) >= BASCULE:
            sens, repere = (1 if v > repere else -1), v
            bascules.append(i / ips)
    r["bascules_de_lumiere"] = [round(b, 2) for b in bascules]
    for i, b in enumerate(bascules):
        dans_la_seconde = [x for x in bascules[i:] if x - b < 1.0]
        if len(dans_la_seconde) >= 4:
            echecs.append(f"flicker: brightness swings {len(dans_la_seconde)} times in the second from {round(b, 2)} s")
            break
    return r, echecs


def pcm(fichier):
    p = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(fichier), "-map", "0:a:0", "-ac", "1",
                        "-ar", str(SR), "-f", "f32le", "-"], capture_output=True)
    return np.frombuffer(p.stdout, np.float32).astype(np.float64)


def attribut(balise, nom):
    m = re.search(rf'\s{nom}="([^"]*)"', balise) or re.search(rf"\s{nom}='([^']*)'", balise)
    return m[1] if m else None


def piste(projet, balise, n):
    """One <audio> clip as the engine plays it: placed at data-start, cut to data-duration, at its volume lane."""
    x = pcm(projet / attribut(balise, "src"))
    debut, duree = float(attribut(balise, "data-start") or 0), float(attribut(balise, "data-duration") or len(x) / SR)
    x = x[round(float(attribut(balise, "data-media-start") or 0) * SR):][:round(duree * SR)]
    y = np.zeros(n)
    a = min(n, round(debut * SR))
    y[a:a + len(x)] = x[:max(0, n - a)]
    t = np.arange(n) / SR - debut
    gain = np.full(n, float(attribut(balise, "data-volume") or 1))
    voie = attribut(balise, "data-automation")
    if voie:
        points = next((l["points"] for l in json.loads(voie).get("lanes", []) if l.get("target") == "volume"), None)
        if points:
            gain *= np.interp(t, [p["t"] for p in points], [p["v"] for p in points])
    return y * gain


def bande(x, bas=300.0, haut=4000.0):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X[(f < bas) | (f > haut)] = 0
    return np.fft.irfft(X, len(x))


def db(x):
    return float(10 * np.log10(np.mean(x ** 2) + 1e-20))


def musique_pompe(projet, attendu):
    """The music's volume lanes: the largest move within 0.2 s, and the end fade of the clip that closes the film."""
    index = (projet / "index.html").read_text(encoding="utf-8")
    racine = re.search(r'<[^>]*id="root"[^>]*>', index)
    total = float(attribut(racine[0], "data-duration")) if racine else None
    fautes, pire = [], {"db": 0.0, "t": None}
    for b in re.findall(r"<audio\b[^>]*>", index, re.S):
        if not (attribut(b, "id") or "").startswith("musique"):
            continue
        debut, duree = float(attribut(b, "data-start") or 0), float(attribut(b, "data-duration") or 0)
        voie = attribut(b, "data-automation")
        points = next((l["points"] for l in json.loads(voie).get("lanes", []) if l.get("target") == "volume"), None) if voie else None
        if points and duree:
            t = np.arange(0.0, duree, 0.01)
            g = 20 * np.log10(np.maximum(np.interp(t, [p["t"] for p in points], [p["v"] for p in points]), 1e-4))
            ecart = np.abs(g[20:] - g[:-20]) if len(g) > 20 else np.zeros(1)
            k = int(np.argmax(ecart))
            if ecart[k] > pire["db"]:
                pire = {"db": round(float(ecart[k]), 1), "t": round(debut + k * 0.01, 2), "clip": attribut(b, "id")}
        if total and duree and debut + duree >= total - 0.05:
            fondu = float(attribut(b, "data-fade-out") or 0)
            if fondu < attendu.get("fondu_fin_min_s", 0.8):
                fautes.append(f"the music is cut at the end: {attribut(b, 'id')} fades out over {fondu} s "
                              f"({attendu.get('fondu_fin_min_s', 0.8)} s at least): it resolves or fades with the film's last second")
    if pire["db"] > attendu.get("pompe_max_db", 4.0):
        fautes.append(f"the music pumps: its volume moves {pire['db']} dB within 0.2 s at {pire['t']} s ({pire['clip']}; "
                      f"{attendu.get('pompe_max_db', 4.0)} dB at most): no lift in a short breath, ramps of 0.3 s or more "
                      "(scripts/lit_musique.py)")
    return pire, fautes


def voix_sur_musique(projet, manifeste, video):
    """Per spoken group: the voice's level over the music's, between 300 Hz and 4 kHz, as heard in the film.

    The voice clip is the <audio> of id "voix", the music the clips whose id starts with "musique". The
    voice's gain in the render is read from the render itself (a mono take plays 3.0 dB louder than its
    file decoded to mono: measured on two films, 2026-11-14), the music's from its volume and lane.
    """
    index = (projet / "index.html").read_text(encoding="utf-8")
    balises = re.findall(r"<audio\b[^>]*>", index, re.S)
    voix = [b for b in balises if attribut(b, "id") == "voix"]
    musiques = [b for b in balises if (attribut(b, "id") or "").startswith("musique")]
    fichier_mots = projet / Path(manifeste.get("voix", {}).get("fichier", "assets/voix.mp3")).parent / "mots.json"
    if not voix or not musiques or not fichier_mots.exists():
        return None
    groupes = json.loads(fichier_mots.read_text(encoding="utf-8")).get("cadence", {}).get("groupes", [])
    rendu = pcm(video)
    n = len(rendu)
    v = piste(projet, voix[0], n)
    m = sum(piste(projet, b, n) for b in musiques)
    # The master step (master.py) raised the whole film by one gain: the music model follows it, or the
    # voice's gain read from the render would carry it alone (first proof render: every group read 2.2 dB high).
    maitre = video.parent / "master.json"
    if maitre.exists():
        m = m * 10 ** (json.loads(maitre.read_text(encoding="utf-8")).get("gain_db", 0.0) / 20)
    decalage = float(attribut(voix[0], "data-start") or 0)
    fenetres = [(round((g["debut"] + decalage) * SR), round((g["fin"] + decalage) * SR)) for g in groupes]
    fenetres = [(a, b) for a, b in fenetres if b - a > SR // 10 and b <= n]
    if not fenetres:
        return None
    # The voice's gain in the mix: what the render holds over the music, against the take itself.
    rapports = [(np.mean(rendu[a:b] ** 2) - np.mean(m[a:b] ** 2)) / max(np.mean(v[a:b] ** 2), 1e-12) for a, b in fenetres]
    gain = float(np.sqrt(max(np.median(rapports), 1e-6)))
    vb, mb = bande(v * gain), bande(m)
    marges = [round(db(vb[a:b]) - db(mb[a:b]), 1) for a, b in fenetres]
    # The bed where the voice is silent, in the film itself: every breath between two groups and the
    # stretches before the first word and after the last, against the voice's own level.
    voix_db = db(np.concatenate([v[a:b] * gain for a, b in fenetres]))
    marge, trous = round(0.04 * SR), []
    for (a0, b0), (a1, _) in zip(fenetres, fenetres[1:]):
        if a1 - b0 >= round(manifeste.get("attendu", {}).get("souffle_min_s", 0.6) * SR):
            trous.append(("souffle", b0 + marge, a1 - marge))
    if fenetres[0][0] >= round(0.3 * SR):
        trous.append(("sans voix", 0, fenetres[0][0] - marge))
    if n - fenetres[-1][1] >= round(0.3 * SR):
        trous.append(("sans voix", fenetres[-1][1] + marge, n - round(0.3 * SR)))
    lit = [{"genre": g, "debut": round(a / SR, 2), "duree": round((b - a) / SR, 2), "sous_voix_db": round(voix_db - db(rendu[a:b]), 1)}
           for g, a, b in trous if b - a > SR // 20]
    return {"gain_voix_db": round(20 * np.log10(gain), 2), "voix_db": round(voix_db, 1), "marges_db": marges, "pire_db": min(marges),
            "pire_groupe": groupes[marges.index(min(marges))]["texte"] if len(marges) == len(groupes) else None,
            "sous_la_voix_db": round(float(np.median(marges)), 1), "lit": lit}


def main():
    projet, video, sortie = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    manifeste = json.loads((projet / "montage.json").read_text(encoding="utf-8"))
    fmt = manifeste.get("format", {"width": 1080, "height": 1920, "fps": 30})
    attendu = manifeste.get("attendu", {})
    sortie.mkdir(parents=True, exist_ok=True)
    echecs, r = [], {"fichier": video.name, "octets": video.stat().st_size if video.exists() else 0}
    if not r["octets"]:
        print("::error::FAILED: no video file")
        sys.exit(1)

    sonde = json.loads(run("ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(video)).stdout)
    v = next((s for s in sonde["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in sonde["streams"] if s["codec_type"] == "audio"), None)
    num, den = (int(x) for x in v["avg_frame_rate"].split("/"))
    images = gris(video, v["width"], v["height"])
    m, d2 = changes(images)
    lumiere = images.mean(axis=(1, 2))
    r.update(largeur=v["width"], hauteur=v["height"], ips=round(num / den, 3), images=len(images),
             secondes=round(len(images) * den / num, 3), secondes_fichier=round(float(sonde["format"]["duration"]), 3),
             codec=v["codec_name"], son=bool(a))
    if (r["largeur"], r["hauteur"]) != (fmt["width"], fmt["height"]):
        echecs.append(f"size {r['largeur']}x{r['hauteur']}, wanted {fmt['width']}x{fmt['height']}")
    if abs(r["ips"] - fmt.get("fps", 30)) > 0.01:
        echecs.append(f"{r['ips']} fps, wanted {fmt.get('fps', 30)}")
    if "secondes" in attendu and not attendu["secondes"][0] <= r["secondes"] <= attendu["secondes"][1]:
        echecs.append(f"picture length {r['secondes']} s ({r['images']} frames), wanted {attendu['secondes'][0]}-{attendu['secondes'][1]} s")

    if a:
        log = run("ffmpeg", "-hide_banner", "-nostats", "-i", str(video), "-map", "0:a:0", "-af", "ebur128=peak=true",
                  "-f", "null", "-").stderr
        fin = log[log.rfind("Summary:"):]
        i = re.search(r"I:\s+(-?[\d.]+) LUFS", fin)
        p = re.search(r"Peak:\s+(-?[\d.]+) dBFS", fin)
        r["lufs"] = float(i[1]) if i else None
        r["crete_dbtp"] = float(p[1]) if p else None
        if r["lufs"] is None or not -15.0 <= r["lufs"] <= -13.0:
            echecs.append(f"loudness {r['lufs']} LUFS, wanted -15 to -13 (master.py brings it to -14)")
        if r["crete_dbtp"] is None or r["crete_dbtp"] > -1.0:
            echecs.append(f"true peak {r['crete_dbtp']} dBTP, wanted -1 or lower")
        limite = attendu.get("blanc_max_s", 0.4)
        log = run("ffmpeg", "-hide_banner", "-nostats", "-i", str(video), "-map", "0:a:0", "-af",
                  f"silencedetect=noise=-35dB:d={limite}", "-f", "null", "-").stderr
        debuts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", log)]
        durees = [float(x) for x in re.findall(r"silence_duration: ([\d.]+)", log)]
        durees += [r["secondes_fichier"] - d for d in debuts[len(durees):]]      # a blank that runs to the end
        r["blancs"] = [{"debut": round(max(0.0, d), 2), "duree": round(x, 2)} for d, x in zip(debuts, durees)]
        for b in r["blancs"]:
            echecs.append(f"no sound for {b['duree']} s from {b['debut']} s ({limite} s at most): the music fills every "
                          "breath of the voice and plays to the last frame")
        if (projet / "index.html").exists():
            r["musique_pompe"], fautes = musique_pompe(projet, attendu)
            echecs += fautes
        vm = r["voix_sur_musique"] = voix_sur_musique(projet, manifeste, video)
        if vm:
            voulu = attendu.get("voix_sur_musique_db", 9.0)
            if vm["pire_db"] < voulu:
                echecs.append(f"the voice sits only {vm['pire_db']} dB over the music (300 Hz-4 kHz) on « {vm['pire_groupe']} » "
                              f"({voulu} dB wanted): lower the music under that group (scripts/lit_musique.py)")
            loin = attendu.get("lit_sous_voix_max_db", 14.0)
            if vm["sous_la_voix_db"] > loin:
                echecs.append(f"the music lies {vm['sous_la_voix_db']} dB under the voice while it speaks (300 Hz-4 kHz, median; "
                              f"{loin} dB at most): the bed is gone, write its level with scripts/lit_musique.py")
            for l in vm["lit"]:
                plafond = attendu.get("souffle_sous_voix_max_db" if l["genre"] == "souffle" else "sans_voix_sous_voix_max_db",
                                      10.0 if l["genre"] == "souffle" else 8.0)
                if l["sous_voix_db"] > plafond:
                    echecs.append(f"the sound falls {l['sous_voix_db']} dB under the voice at {l['debut']} s ({l['genre']}, "
                                  f"{l['duree']} s; {plafond} dB at most): the music fills every breath (scripts/lit_musique.py)")
    elif attendu.get("son", True):
        echecs.append("no sound track")

    r["rythme"], fautes = rythme(m, d2, lumiere, num / den, attendu)
    echecs += fautes

    log = run("ffmpeg", "-hide_banner", "-nostats", "-i", str(video), "-map", "0:v:0", "-frames:v", "1", "-vf",
              "signalstats,metadata=print", "-f", "null", "-").stderr
    ymin, ymax = re.search(r"YMIN=([\d.]+)", log), re.search(r"YMAX=([\d.]+)", log)
    if ymin and ymax:
        r["image0_ecart_luma"] = float(ymax[1]) - float(ymin[1])
        if r["image0_ecart_luma"] < 40:
            echecs.append(f"first frame nearly empty (luma range {r['image0_ecart_luma']})")

    run("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(video), "-vf", "fps=2,scale=270:-2,tile=8x3",
        "-q:v", "3", str(sortie / "planche-%02d.jpg"))
    r["planches"] = sorted(p.name for p in sortie.glob("planche-*.jpg"))
    if a:
        # The sound as a picture, since nobody listens before delivery: its wave (blanks and jumps are seen
        # at a glance) over its spectrum (voice, music and effects each have their band).
        run("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(video), "-filter_complex",
            "[0:a]aformat=channel_layouts=mono,asplit[x][y];[x]showwavespic=s=1600x260:colors=white[w];"
            "[y]showspectrumpic=s=1600x380:legend=0:scale=log:fscale=log[s];[w][s]vstack", "-frames:v", "1", str(sortie / "son.png"))
    r["echecs"] = echecs
    (sortie / "rapport.json").write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(r, ensure_ascii=False))
    for e in echecs:
        print(f"::error::FAILED: {e}")
    sys.exit(1 if echecs else 0)


if __name__ == "__main__":
    main()
