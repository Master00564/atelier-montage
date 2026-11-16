"""Time every word of a voice take against the text it reads.

    python montage/outils/mots.py montage/projets/<name> OUT_DIR [VOICE_FILE]

VOICE_FILE: a take that is not in the project yet (the one montage/outils/voix.py just made).

Reads montage.json: {"voix": {"fichier": "assets/voix.mp3", "texte": "texte.txt"}}. The text is known
(it is what the voice was asked to say), so Whisper is only the ear: faster-whisper medium hears the
words with their times, voix/alignement.py matches them to the script's own tokens, and the pauses
are measured in the sound itself (FFmpeg silencedetect with a threshold taken from the take's own
level), because Whisper's word edges can be 0.1-0.2 s late. A word that follows a measured pause
starts where the pause ends.

Writes OUT_DIR/mots.json:
  duree_s, wer, fautes        the take's length and how far what was heard is from the script
  entendu                     what Whisper wrote, as it wrote it (to read when a take is refused)
  mots[]    {"mot", "debut", "fin"}   one per display token of the script, punctuation attached
  pauses[]  {"debut", "fin"}          silences of 0.15 s and more
  phrases[] {"texte", "debut", "fin", "mots": [first, last]}   sentences of the script
  cadence   {"debit_habituel", "presses", "groupes"}   pace in syllables a second, breath group by
            breath group (cadence.py); "presses" lists the groups over 1.15 times the usual pace
            or over "voix.debit_max" (5.5) by more than 5 %
"""
import json
import re
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "voix"))
from alignement import caler_texte, parle  # noqa: E402
from cadence import ECART, PLAFOND, SYLLABES_MIN, debits, reference  # noqa: E402


def echec(message):
    print(f"::error::FAILED: {message}")
    sys.exit(1)


def pcm(chemin):
    import numpy as np
    p = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(chemin), "-ac", "1",
                        "-ar", "16000", "-f", "f32le", "-"], capture_output=True, check=True)
    return np.frombuffer(p.stdout, dtype=np.float32)


def pauses(chemin, duree):
    """Silences measured in the sound: threshold = the take's own gate level, as loudnorm reports it."""
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(chemin), "-af",
                        "loudnorm=print_format=json", "-f", "null", "-"], capture_output=True, text=True)
    m = re.search(r"\{[^{}]*\"input_thresh\"[^{}]*\}", p.stderr, re.S)
    seuil = float(json.loads(m[0])["input_thresh"]) if m else -40.0
    seuil = max(-55.0, min(-28.0, seuil))
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(chemin), "-af",
                        f"silencedetect=noise={seuil}dB:d=0.15", "-f", "null", "-"], capture_output=True, text=True)
    debuts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", p.stderr)]
    fins = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", p.stderr)]
    fins += [duree] * (len(debuts) - len(fins))
    return seuil, [{"debut": round(max(0.0, d), 3), "fin": round(f, 3)} for d, f in zip(debuts, fins)]


def main():
    import jiwer
    from faster_whisper import WhisperModel

    projet, sortie = Path(sys.argv[1]), Path(sys.argv[2])
    manifeste = json.loads((projet / "montage.json").read_text(encoding="utf-8"))
    voix = manifeste.get("voix") or echec("montage.json has no voix")
    son = Path(sys.argv[3]) if len(sys.argv) > 3 else projet / voix.get("fichier", "assets/voix.mp3")
    texte_f = projet / voix["texte"]
    if not son.exists() or not texte_f.exists():
        echec(f"missing {son} or {texte_f}")
    texte = " ".join(texte_f.read_text(encoding="utf-8").split())
    audio = pcm(son)
    duree = len(audio) / 16000

    modele = WhisperModel("medium", device="cpu", compute_type="int8")
    segs, _ = modele.transcribe(audio, language="fr", beam_size=5, temperature=0, word_timestamps=True,
                                condition_on_previous_text=False)
    entendus = [{"mot": w.word.strip(), "debut": round(w.start, 3), "fin": round(w.end, 3)} for s in segs for w in s.words]
    # Whisper writes what it hears its own way: « 13,5 cm » for « treize centimètres et demi ». Put it back
    # in the order the words were said before comparing, or a short script fails on its numbers alone.
    brut = " ".join(x["mot"] for x in entendus)
    unite = r"(cms?|centimètres?|mètres?|m)"
    entendu = re.sub(rf"(\d+)\s*[,.]\s*5\s*{unite}\b", r"\1 \2 et demi", brut)      # « 13,5 cm », « 13 ,5 cm »
    entendu = re.sub(rf"(\d+)\s*{unite}\s*5\b", r"\1 \2 et demi", entendu)           # « 13 cm 5 »
    entendu = re.sub(r"\bcms?\b", "centimètres", entendu)
    ref, hyp = " ".join(parle(texte)), " ".join(parle(entendu))
    bilan = jiwer.process_words(ref, hyp)
    rw, hw = ref.split(), hyp.split()
    fautes = [f"{' '.join(rw[c.ref_start_idx:c.ref_end_idx]) or '-'} -> {' '.join(hw[c.hyp_start_idx:c.hyp_end_idx]) or '-'}"
              for c in bilan.alignments[0] if c.type != "equal"]

    seuil, silences = pauses(son, duree)
    mots = [{"mot": j, "debut": round(d, 3), "fin": round(f, 3)} for j, d, f in caler_texte(texte, entendus)]
    # The first word after a measured pause starts where the pause ends (one word per pause).
    for s in silences:
        suivant = next((m for m in mots if m["debut"] >= s["debut"] - 0.05), None)
        if suivant and suivant["debut"] <= s["fin"] + 0.25 and s["fin"] < suivant["fin"]:
            suivant["debut"] = s["fin"]
    # In order, never overlapping, and no word shorter than 60 ms.
    for a, b in zip(mots, mots[1:]):
        b["debut"] = round(max(b["debut"], a["debut"] + 0.06), 3)
        a["fin"] = round(min(max(a["fin"], a["debut"] + 0.06), b["debut"]), 3)

    phrases, debut = [], 0
    for i, m in enumerate(mots):
        if re.search(r"[.!?…][»\")]?$", m["mot"]) or i == len(mots) - 1:
            phrases.append({"texte": " ".join(x["mot"] for x in mots[debut:i + 1]), "debut": mots[debut]["debut"],
                            "fin": m["fin"], "mots": [debut, i]})
            debut = i + 1

    groupes = debits(mots, silences)
    habituel = reference(groupes)
    plafond = 1.05 * float(voix.get("debit_max", PLAFOND))
    presses = [g["texte"] for g in groupes if g["syllabes"] >= SYLLABES_MIN
               and (g["debit"] > plafond or (habituel and g["debit"] > ECART * habituel))]

    sortie.mkdir(parents=True, exist_ok=True)
    rapport = {"fichier": son.name, "duree_s": round(duree, 3), "wer": round(bilan.wer, 4), "fautes": fautes, "entendu": brut,
               "seuil_silence_db": seuil, "mots": mots, "pauses": silences, "phrases": phrases,
               "cadence": {"debit_habituel": habituel, "presses": presses, "groupes": groupes}}
    (sortie / "mots.json").write_text(json.dumps(rapport, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: rapport[k] for k in ("duree_s", "wer", "fautes")}, ensure_ascii=False))
    print(f"{len(mots)} words, {len(silences)} pauses, {len(phrases)} sentences, usual pace {habituel} syllables a second")
    for t in presses:
        print(f"hurried: « {t} »")
    if bilan.wer > 0.15:
        echec(f"the voice is too far from the script (word error rate {bilan.wer:.0%}): {fautes[:6]}")


if __name__ == "__main__":
    main()
