"""Measure the intonation of a voice take, sentence by sentence, and flag the flat lines.

    python montage/outils/intonation.py montage/projets/<name> OUT_DIR [VOICE_FILE]

Reads OUT_DIR/mots.json (the sentences and their times, written by mots.py for that same file) and the
voice (VOICE_FILE, else the manifest's voix.fichier). Pitch is read with Praat's autocorrelation method
through praat-parselmouth (GPL-3.0, installed as a tool, nothing copied into this repo): on the shop's
generated male voice, librosa's pyin locked on a sub-harmonic (66-76 Hz against Praat's 84-92 Hz,
measured 2026-11-17), so Praat it is. Octave jumps (a frame 8+ semitones from its neighbourhood) are
folded back by 12 semitones before anything is measured.

Per sentence, in semitones from the take's own median pitch:
  ecart_st   spread of the voiced pitch, 80th minus 20th percentile (how much the line moves)
  fin_st     last quarter of the voiced frames minus the middle half (> 0 = the end rises)
Verdicts: "peu_voisee" (a line of 0.8 s or more, under a quarter voiced: breathed or whispered),
"plate" (ecart under PLAT), "a_surveiller" (under SURVEILLER), "fin_pas_montante" (a line
that should end suspended, by its segment's "intonation": "montante" or by ending on « … » or « ? »,
whose end does not rise by FIN_MONTANTE), "pas_assez_vive" (a segment marked "vive" under VIVE).
The thresholds were set on five generated takes of 2026-11-13 to 16 (sentence spreads 2.6 to 12.4
semitones): they are the shop's own measure, not a published norm, to be tuned against the owner's ear.

Writes OUT_DIR/intonation.json and prints one line per flagged sentence. It never fails the run: it
reports, and the editor decides (one voice take spent on a flat key line, not on a small dip).
"""
import json
import re
import sys
from pathlib import Path

PLAT, SURVEILLER, VIVE, FIN_MONTANTE = 2.5, 3.5, 4.5, 1.0
MIN_VOISE = 25  # voiced frames of 10 ms below which a sentence is not judged


def segments_mots(voix):
    """For each word of the script, the index of the segment that says it (None without segments)."""
    segs = voix.get("segments") or []
    index = []
    for i, s in enumerate(segs):
        mots = re.sub(r"<[^<>]+>", " ", s.get("texte", "")).split()
        index += [i] * len(mots)
    return segs, index


def main():
    import warnings
    warnings.filterwarnings("ignore", category=RuntimeWarning)  # all-NaN windows in silences
    import numpy as np
    import parselmouth

    projet, sortie = Path(sys.argv[1]), Path(sys.argv[2])
    voix = json.loads((projet / "montage.json").read_text(encoding="utf-8")).get("voix") or {}
    son = Path(sys.argv[3]) if len(sys.argv) > 3 else projet / voix.get("fichier", "assets/voix.mp3")
    rapport_mots = json.loads((sortie / "mots.json").read_text(encoding="utf-8"))
    phrases = rapport_mots.get("phrases", [])

    sound = parselmouth.Sound(str(son))
    pitch = sound.to_pitch_ac(time_step=0.01, pitch_floor=60, pitch_ceiling=500)
    f0 = pitch.selected_array["frequency"].astype(float)
    t = np.asarray(pitch.xs())
    f0[f0 <= 0] = np.nan
    mediane = float(np.nanmedian(f0))
    st = 12 * np.log2(f0 / mediane)
    ok = ~np.isnan(st)
    bord = np.pad(np.where(ok, st, np.nan), 15, mode="edge")
    voisin = np.nan_to_num(np.nanmedian(np.lib.stride_tricks.sliding_window_view(bord, 31), axis=1))
    st = np.where(ok & (st - voisin > 8), st - 12, st)
    st = np.where(ok & (voisin - st > 8), st + 12, st)

    segs, index = segments_mots(voix)
    lignes, signalees = [], []
    for p in phrases:
        s = st[(t >= p["debut"]) & (t < p["fin"])]
        s = s[~np.isnan(s)]
        premier = p["mots"][0]
        seg = index[premier] if premier < len(index) else None
        attendu = (segs[seg].get("intonation") if seg is not None else None) or (
            "montante" if re.search(r"(…|\.\.\.|\?)[»\")]?$", p["texte"]) else None)
        trames = int(np.sum((t >= p["debut"]) & (t < p["fin"])))
        ligne = {"texte": p["texte"], "debut": p["debut"], "fin": p["fin"], "segment": seg, "attendu": attendu,
                 "trames_voisees": int(len(s)), "part_voisee": round(len(s) / trames, 2) if trames else 0.0}
        if len(s) < MIN_VOISE:
            # A line of 0.8 s or more with little voiced sound was breathed or whispered: say it, it is a delivery
            # fault for a narrator (the « suspenseful » style of 2026-11-17 did exactly that on the hand-off line).
            longue = p["fin"] - p["debut"] >= 0.8
            ligne["verdict"] = "peu_voisee" if longue and ligne["part_voisee"] < 0.25 else "trop_court"
            if len(s) >= 8:
                n = len(s)
                ligne["fin_st"] = round(float(np.median(s[n // 2:]) - np.median(s[:n // 2])), 1)
        else:
            n = len(s)
            ecart = float(np.percentile(s, 80) - np.percentile(s, 20))
            fin = float(np.median(s[int(n * 0.75):]) - np.median(s[int(n * 0.25):int(n * 0.75)]))
            ligne.update(ecart_st=round(ecart, 1), fin_st=round(fin, 1))
            verdicts = []
            if ecart < PLAT:
                verdicts.append("plate")
            elif ecart < SURVEILLER:
                verdicts.append("a_surveiller")
            if attendu == "montante" and fin < FIN_MONTANTE:
                verdicts.append("fin_pas_montante")
            if attendu == "vive" and ecart < VIVE:
                verdicts.append("pas_assez_vive")
            ligne["verdict"] = " ".join(verdicts) or "ok"
        lignes.append(ligne)
        if ligne["verdict"] not in ("ok", "trop_court"):
            signalees.append(ligne)

    voise = st[~np.isnan(st)]
    bilan = {"fichier": son.name, "mediane_hz": round(mediane, 1),
             "ecart_prise_st": round(float(np.percentile(voise, 80) - np.percentile(voise, 20)), 1) if len(voise) else None,
             "seuils": {"plat": PLAT, "a_surveiller": SURVEILLER, "vive": VIVE, "fin_montante": FIN_MONTANTE},
             "phrases": lignes, "signalees": len(signalees)}
    (sortie / "intonation.json").write_text(json.dumps(bilan, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"intonation: {len(lignes)} sentences, {len(signalees)} flagged, median {bilan['mediane_hz']} Hz, "
          f"take spread {bilan['ecart_prise_st']} st")
    for l in signalees:
        print(f"  {l['verdict']}: « {l['texte']} » (spread {l.get('ecart_st')} st, end {l.get('fin_st')} st)")


if __name__ == "__main__":
    main()
