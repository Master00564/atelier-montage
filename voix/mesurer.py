"""Measure every WAV of a folder, since nobody listens during the test.

    python voix/mesurer.py DIR [--etape asr|mos|son]

Steps (each in its own process when run without --etape, so two models never share RAM):
  asr  back-transcription with faster-whisper small (French, CPU, int8), word error rate
       against what a correct reading says (textes.DIT), checked points (names, numbers);
  mos  UTMOS22 strong naturalness score (1-5; trained on English speech, indicative only);
  son  pitch median (Hz) and spread (semitones), speaking rate, loudness (LUFS);
  accent  probability that Whisper, left free, recognises French (a foreign accent lowers it).
Results are cached in DIR/mesures.json, keyed by file name: a rerun only measures new files.
"""
import argparse
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from textes import DIT, POINTS  # noqa: E402

ETAPES = {"asr": "wer", "mos": "utmos", "son": "f0_median_hz", "accent": "proba_francais"}


def sans_accents(t):
    return "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn")


def normaliser(texte):
    """Lowercase spoken form without accents or punctuation; digits and 'cm' spelled out."""
    from num2words import num2words
    t = texte.lower().replace("’", "'")
    t = re.sub(r"(\d+)[,.](\d+)", lambda m: f"{num2words(int(m[1]), lang='fr')} virgule {num2words(int(m[2]), lang='fr')}", t)
    t = re.sub(r"\d+", lambda m: num2words(int(m[0]), lang="fr"), t)
    t = re.sub(r"\bcms?\b", "centimètres", t)
    t = sans_accents(t)
    t = re.sub(r"[^a-z]+", " ", t)
    return " ".join(t.split())


def a_mesurer(dossier, mesures, cle):
    """Samples still on disk that lack this measure (screened-out WAVs are deleted)."""
    return [(w, r) for w, r in mesures.items() if cle not in r and (dossier / w).exists()]


def audio_16k(chemin):
    """Mono 16 kHz float32 samples, decoded by FFmpeg (faster-whisper's own PyAV decoding
    breaks with PyAV 15 and later)."""
    p = subprocess.run([ffmpeg(), "-hide_banner", "-loglevel", "error", "-i", str(chemin), "-ac", "1",
                        "-ar", "16000", "-f", "f32le", "-"], capture_output=True, check=True)
    return np.frombuffer(p.stdout, dtype=np.float32)


def etape_asr(dossier, mesures):
    import jiwer
    from faster_whisper import WhisperModel
    m = WhisperModel("small", device="cpu", compute_type="int8")
    for wav, r in a_mesurer(dossier, mesures, "wer"):
        segs, _ = m.transcribe(audio_16k(dossier / wav), language="fr", beam_size=5, temperature=0,
                               condition_on_previous_text=False)
        brut = " ".join(s.text.strip() for s in segs)
        ref, hyp = normaliser(DIT[r["prise"]]), normaliser(brut)
        sortie = jiwer.process_words(ref, hyp)
        rw, hw = ref.split(), hyp.split()
        fautes = []
        for c in sortie.alignments[0]:
            if c.type != "equal":
                fautes.append(f"{' '.join(rw[c.ref_start_idx:c.ref_end_idx]) or '-'} -> "
                              f"{' '.join(hw[c.hyp_start_idx:c.hyp_end_idx]) or '-'}")
        points = {}
        for nom, attendu in POINTS.items():
            attendu = attendu[r["prise"]] if isinstance(attendu, dict) else attendu
            points[nom] = f" {normaliser(attendu)} " in f" {hyp} "
        r.update(transcription=brut, wer=round(sortie.wer, 4), fautes=fautes, points=points)
        print(wav, r["wer"], fautes, flush=True)


def etape_accent(dossier, mesures):
    from faster_whisper import WhisperModel
    m = WhisperModel("small", device="cpu", compute_type="int8")
    for wav, r in a_mesurer(dossier, mesures, "proba_francais"):
        _, _, probas = m.detect_language(audio_16k(dossier / wav))
        r["proba_francais"] = round(dict(probas).get("fr", 0.0), 4)
        print(wav, r["proba_francais"], flush=True)


def etape_mos(dossier, mesures):
    import torch
    torch.set_num_threads(max(1, (__import__("os").cpu_count() or 2)))
    try:
        import torchaudio  # noqa: F401  (SpeechMOS resamples to 16 kHz with it)
        lire = lambda chemin: sf.read(chemin, dtype="float32")  # noqa: E731
    except ImportError:
        # torchaudio stopped at 2.11 while torch goes on: resample with FFmpeg instead, so
        # SpeechMOS only ever sees 16 kHz and its resample call is a no-op.
        import importlib.machinery
        import types
        stub = types.ModuleType("torchaudio")
        stub.__spec__ = importlib.machinery.ModuleSpec("torchaudio", None)
        stub.functional = types.SimpleNamespace(resample=lambda w, orig_freq, new_freq: w)
        sys.modules["torchaudio"] = stub
        lire = lambda chemin: (audio_16k(chemin), 16000)  # noqa: E731
    # skip_validation: no call to api.github.com, whose anonymous quota runners often exhaust
    p = torch.hub.load("tarepan/SpeechMOS:v1.2.0", "utmos22_strong", trust_repo=True, skip_validation=True)
    for wav, r in a_mesurer(dossier, mesures, "utmos"):
        audio, sr = lire(dossier / wav)
        with torch.inference_mode():
            r["utmos"] = round(float(p(torch.from_numpy(audio).unsqueeze(0), sr)), 3)
        print(wav, r["utmos"], flush=True)


def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def loudnorm(chemin, cible=""):
    """Run FFmpeg's loudnorm analysis on a file and return its JSON report."""
    p = subprocess.run([ffmpeg(), "-hide_banner", "-nostats", "-i", str(chemin), "-af",
                        f"loudnorm={cible}print_format=json", "-f", "null", "-"], capture_output=True, text=True)
    debut = p.stderr.rindex("{")
    return json.loads(p.stderr[debut:p.stderr.index("}", debut) + 1])


def lufs(chemin):
    """Integrated loudness (EBU R128) of an audio file, in LUFS."""
    return float(loudnorm(chemin)["input_i"])


def etape_son(dossier, mesures):
    import parselmouth
    for wav, r in a_mesurer(dossier, mesures, "f0_median_hz"):
        audio, sr = sf.read(dossier / wav, dtype="float64")
        f0 = parselmouth.Sound(audio, sr).to_pitch(time_step=0.01, pitch_floor=60, pitch_ceiling=500)
        f0 = f0.selected_array["frequency"]
        f0 = f0[f0 > 0]
        # speaking time: from the first to the last 20 ms frame within 35 dB of the loudest one
        trame = int(0.02 * sr)
        rms = np.sqrt(np.mean(audio[: len(audio) // trame * trame].reshape(-1, trame) ** 2, axis=1)) + 1e-9
        actives = np.where(20 * np.log10(rms / rms.max()) > -35)[0]
        parole = (actives[-1] - actives[0] + 1) * 0.02 if len(actives) else len(audio) / sr
        med = float(np.median(f0)) if len(f0) else None
        r.update(f0_median_hz=round(med, 1) if med else None,
                 f0_ecart_demitons=round(float(np.std(12 * np.log2(f0 / med))), 2) if med else None,
                 mots_par_minute=round(len(normaliser(DIT[r["prise"]]).split()) / parole * 60),
                 lufs_brut=round(lufs(dossier / wav), 1))
        print(wav, r["f0_median_hz"], r["mots_par_minute"], r["lufs_brut"], flush=True)


def charger(dossier):
    fichier = dossier / "mesures.json"
    mesures = json.loads(fichier.read_text(encoding="utf-8")) if fichier.exists() else {}
    journal = dossier / "generation.jsonl"
    for ligne in journal.read_text(encoding="utf-8").splitlines() if journal.exists() else []:
        g = json.loads(ligne)
        if (dossier / g["fichier"]).exists():
            mesures.setdefault(g["fichier"], {}).update(g)
    return fichier, mesures


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("dossier", type=Path)
    ap.add_argument("--etape", choices=ETAPES)
    a = ap.parse_args()
    if a.etape is None:  # each step in a fresh process; one failing step does not stop the others
        rates = [e for e in ETAPES if subprocess.run([sys.executable, __file__, str(a.dossier), "--etape", e]).returncode]
        sys.exit(f"FAILED: measuring steps {rates}" if rates else 0)
    fichier, mesures = charger(a.dossier)
    try:
        globals()[f"etape_{a.etape}"](a.dossier, mesures)
    finally:
        fichier.write_text(json.dumps(mesures, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
