"""Say a project's text with the voice its manifest names, in one call.

    GEMINI_API_KEY=... python montage/outils/voix.py montage/projets/<name> OUT_DIR

montage.json: {"voix": {"texte": "texte.txt", "moteur": "gemini-3.8-flash-tts", "voix": "Algieba",
"style": "calm, warm French narrator…", "vitesse": 1.2}}. Writes OUT_DIR/voix-brute.wav, the take at
the voice's own pace, and OUT_DIR/voix-bilan.json (seconds of the call, seconds of sound, the API's
usage figures). The workflow then times it (mots.py), gives it one even pace at "vitesse"
(cadence.py, which writes voix.mp3) and times the result. One call a take: the free tier
allows few calls a day, and a refusal for quota (HTTP 429) is said as such. The key comes from the
environment and is never printed.
"""
import json
import os
import subprocess
import sys
import time
import urllib.error
import wave
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "voix"))
import gemini  # noqa: E402


def echec(message):
    print(f"::error::FAILED: {message}")
    sys.exit(1)


def main():
    projet, sortie = Path(sys.argv[1]), Path(sys.argv[2])
    voix = json.loads((projet / "montage.json").read_text(encoding="utf-8")).get("voix") or echec("montage.json has no voix")
    if not voix.get("voix"):
        echec("montage.json voix.voix is empty: name the voice (the shop profile gives it)")
    cle = os.environ.get("GEMINI_API_KEY", "").strip() or echec("the GEMINI_API_KEY secret is not set in the repo")
    texte = " ".join((projet / voix["texte"]).read_text(encoding="utf-8").split())
    if voix.get("style"):
        gemini.STYLE = voix["style"]
    sortie.mkdir(parents=True, exist_ok=True)
    debut = time.time()
    try:
        reponse = gemini.dire(cle, voix.get("moteur", "gemini-3.8-flash-tts"), voix["voix"], texte)
    except urllib.error.HTTPError as e:
        corps = e.read().decode("utf-8", "replace")[:300]
        echec("the voice quota of the day is used up (HTTP 429); it comes back at 09:00 Paris time" if e.code == 429
              else f"voice API answered HTTP {e.code}: {corps}")
    octets, genre = gemini.son(reponse)
    if not octets:
        echec("the voice API answered without sound")
    wav = sortie / "voix-brute.wav"
    gemini.en_wav(octets, wav)
    with wave.open(str(wav)) as w:
        secondes = round(w.getnframes() / w.getframerate(), 2)
    bilan = {"voix": voix["voix"], "moteur": voix.get("moteur", "gemini-3.8-flash-tts"), "mots_du_texte": len(texte.split()),
             "secondes_appel": round(time.time() - debut, 1), "secondes_son_brut": secondes, "type": genre,
             "usage": reponse.get("usage")}
    (sortie / "voix-bilan.json").write_text(json.dumps(bilan, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(bilan, ensure_ascii=False))


if __name__ == "__main__":
    main()
