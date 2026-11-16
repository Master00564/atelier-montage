"""Reads the test narration of voix/textes.py with Google's Gemini text-to-speech (free tier of the Gemini API).

    GEMINI_API_KEY=... python voix/gemini.py SORTIE [--voix Charon Orus ...] [--prises chiffres lettres]

One call per voice and take, a few seconds each, nothing to install but ffmpeg (imageio-ffmpeg). Each sample is
written as SORTIE/gemini__<voice>__<take>.mp3 at -16 LUFS, like the other engines' samples, and bilan.json says
for every call how long it took and what the API answered. The free tier's daily limit is not published: at the
first refusal for quota (HTTP 429) the run stops and keeps what it has. The key is read from the environment and
never printed.
"""
import argparse
import base64
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from textes import PRISES  # noqa: E402

URL = "https://generativelanguage.googleapis.com/v1beta/interactions"
# Prebuilt voices of the documentation (ai.google.dev, speech-generation, read on 12/11/2026). Men, then women.
VOIX = ["Charon", "Orus", "Algieba", "Sulafat", "Achernar", "Vindemiatrix"]
STYLE = "calm, warm French narrator of a short film about interior lighting, natural pace, Parisian French accent"


def dire(cle, modele, voix, texte):
    corps = {
        "model": modele,
        "input": [{"type": "user_input", "content": [{"type": "text", "text": texte,
                                                      "annotations": [{"type": "speech_metadata", "style": STYLE}]}]}],
        "response_format": {"type": "audio"},
        "generation_config": {"speech_config": [{"voice": voix}]},
    }
    requete = urllib.request.Request(URL, data=json.dumps(corps).encode("utf-8"), method="POST",
                                     headers={"x-goog-api-key": cle, "Content-Type": "application/json"})
    with urllib.request.urlopen(requete, timeout=180) as reponse:
        return json.loads(reponse.read().decode("utf-8"))


def son(reponse):
    """The last audio block of the answer, as bytes, with its declared type."""
    blocs = [c for etape in reponse.get("steps", []) if etape.get("type") == "model_output"
             for c in etape.get("content", []) if c.get("type") == "audio"]
    if not blocs:
        return None, None
    return base64.b64decode(blocs[-1]["data"]), blocs[-1].get("mime_type") or blocs[-1].get("mimeType")


def en_wav(octets, chemin):
    """The API answers a WAV file; raw 24 kHz 16-bit mono samples are wrapped into one."""
    if octets[:4] == b"RIFF":
        chemin.write_bytes(octets)
        return
    with wave.open(str(chemin), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(24000)
        w.writeframes(octets)


def en_mp3(wav, mp3):
    import imageio_ffmpeg
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-i", str(wav), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
                    "-ar", "44100", "-b:a", "160k", str(mp3)], check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("sortie", type=Path)
    ap.add_argument("--voix", nargs="*", default=VOIX)
    ap.add_argument("--prises", nargs="*", default=["chiffres", "lettres"])
    ap.add_argument("--modele", default="gemini-3.8-flash-tts")
    ap.add_argument("--pause", type=float, default=8.0, help="seconds between two calls")
    a = ap.parse_args()
    cle = os.environ.get("GEMINI_API_KEY", "").strip()
    if not cle:
        sys.exit("FAILED: GEMINI_API_KEY is not set")
    a.sortie.mkdir(parents=True, exist_ok=True)
    bilan, arret = [], None
    for prise in a.prises:
        for voix in a.voix:
            if arret:
                break
            ligne = {"voix": voix, "prise": prise, "modele": a.modele}
            debut = time.time()
            try:
                reponse = dire(cle, a.modele, voix, PRISES[prise])
                octets, genre = son(reponse)
                ligne["secondes_appel"] = round(time.time() - debut, 1)
                if not octets:
                    ligne["erreur"] = "no audio in the answer: " + json.dumps({k: v for k, v in reponse.items() if k != "steps"})[:300]
                else:
                    wav = a.sortie / f"gemini__{voix}__{prise}.wav"
                    en_wav(octets, wav)
                    with wave.open(str(wav)) as w:
                        ligne["secondes_son"] = round(w.getnframes() / w.getframerate(), 1)
                    en_mp3(wav, wav.with_suffix(".mp3"))
                    wav.unlink()
                    ligne["fichier"] = wav.with_suffix(".mp3").name
                    ligne["type"] = genre
                    ligne["usage"] = reponse.get("usage")
            except urllib.error.HTTPError as e:
                ligne["secondes_appel"] = round(time.time() - debut, 1)
                ligne["erreur"] = f"HTTP {e.code}: " + e.read().decode("utf-8", "replace")[:400]
                if e.code == 429:
                    arret = "quota"
            except Exception as e:  # network, decoding: said, and the next voice is tried
                ligne["erreur"] = type(e).__name__ + ": " + str(e)[:300]
            print(json.dumps(ligne, ensure_ascii=False), flush=True)
            bilan.append(ligne)
            time.sleep(a.pause)
    (a.sortie / "bilan.json").write_text(json.dumps({"arret": arret, "appels": bilan}, ensure_ascii=False, indent=1), encoding="utf-8")
    faits = [x for x in bilan if "fichier" in x]
    print(f"samples {len(faits)} / {len(a.voix) * len(a.prises)} | stopped: {arret}")
    sys.exit(0 if faits else 1)


if __name__ == "__main__":
    main()
