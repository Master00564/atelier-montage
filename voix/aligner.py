"""Check each narration take of a theme job and time its words.

    python voix/aligner.py OUT_DIR JOB.json

For every OUT_DIR/*__narration-g*.wav: Whisper (faster-whisper medium, French, no prompt, so a
mispronounced name is heard as it was said) writes the words with their times; the take is
compared with the script (word error rate on spoken words) and each name of theme.noms is
checked by sound (eSpeak phonemes, voix/phonetique.py) in the stretch where the script says it.
Writes <take>.json (words, times, checks) next to each WAV and prints one line per take.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from alignement import caler_texte, jetons, parle  # noqa: E402
from mesurer import audio_16k  # noqa: E402
from narration import lire, ordre, texte  # noqa: E402


def main():
    import jiwer
    from faster_whisper import WhisperModel
    import phonetique

    dossier, job = Path(sys.argv[1]), sys.argv[2]
    theme = lire(job)
    dit = texte(theme)
    m = WhisperModel("medium", device="cpu", compute_type="int8")
    for wav in sorted(dossier.glob("*__narration-g*.wav")):
        audio = audio_16k(wav)
        segs, _ = m.transcribe(audio, language="fr", beam_size=5, temperature=0, word_timestamps=True,
                               condition_on_previous_text=False)
        mots = [{"mot": w.word.strip(), "debut": round(w.start, 3), "fin": round(w.end, 3),
                 "p": round(w.probability, 3)} for s in segs for w in s.words]
        entendu = " ".join(x["mot"] for x in mots)
        ref, hyp = " ".join(parle(dit)), " ".join(parle(entendu))
        sortie = jiwer.process_words(ref, hyp)
        rw, hw = ref.split(), hyp.split()
        fautes = [f"{' '.join(rw[c.ref_start_idx:c.ref_end_idx]) or '-'} -> {' '.join(hw[c.hyp_start_idx:c.hyp_end_idx]) or '-'}"
                  for c in sortie.alignments[0] if c.type != "equal"]
        # Lines: start and end of each, in reading order, from the script's own words.
        cales = caler_texte(dit, mots)
        lignes, k = [], 0
        for i in ordre(theme):
            n = len(jetons(theme["lignes"][i]["dit"]))
            lignes.append({"ligne": i, "debut": round(cales[k][1], 3), "fin": round(cales[k + n - 1][2], 3)})
            k += n
        # Names: the heard words over the time the script gives the name, compared by sound.
        noms = {}
        for nom, prononce in theme.get("noms", {}).items():
            spans = [(d, f) for j, d, f in cales if nom.lower() in j.lower() or prononce.lower() in j.lower()]
            if not spans:
                noms[nom] = {"ok": False, "entendu": "", "raison": "name not in the script"}
                continue
            d, f = spans[0][0] - 0.25, spans[-1][1] + 0.25
            autour = " ".join(x["mot"] for x in mots if x["fin"] > d and x["debut"] < f)
            ok = phonetique.contient(autour, nom) or phonetique.contient(autour, prononce)
            noms[nom] = {"ok": ok, "entendu": autour}
        rapport = {"fichier": wav.name, "duree_s": round(len(audio) / 16000, 3), "wer": round(sortie.wer, 4),
                   "fautes": fautes, "noms": noms, "lignes": lignes, "transcription": entendu, "mots": mots}
        wav.with_suffix(".json").write_text(json.dumps(rapport, ensure_ascii=False, indent=1), encoding="utf-8")
        print(json.dumps({k: rapport[k] for k in ("fichier", "duree_s", "wer", "fautes")}, ensure_ascii=False))
        print("  noms:", {k: (v["ok"], v["entendu"]) for k, v in noms.items()}, flush=True)


if __name__ == "__main__":
    main()
