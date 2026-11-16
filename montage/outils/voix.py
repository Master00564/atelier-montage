"""Say a project's text with the voice its manifest names, in one call.

    GEMINI_API_KEY=... python montage/outils/voix.py montage/projets/<name> OUT_DIR

montage.json: {"voix": {"texte": "texte.txt", "moteur": "gemini-3.8-flash-tts", "voix": "Algieba",
"style": "calm, warm French narrator…", "vitesse": 1.2, "segments": [...]}}. Writes OUT_DIR/voix-brute.wav,
the take at the voice's own pace, and OUT_DIR/voix-bilan.json (seconds of the call, seconds of sound, the
API's usage figures, the parts sent). The workflow then times it (mots.py), gives it one even pace at
"vitesse" (cadence.py, which writes voix.mp3), times the result and measures its intonation
(intonation.py). One call a take: the free tier allows about ten a day, and a refusal for quota
(HTTP 429) is said as such. The key comes from the environment and is never printed.

How the voice is directed (Gemini 3.8 TTS documentation, aistudio.google.com/docs/speech-generation,
read 2026-11-17): the text is said word for word; delivery goes in a SHORT "style" (a few words: long
director's notes make the voice drift); momentary events go inline in English between angle brackets
(<short pause>, <long pause>, <breath>, <sigh>, <chuckle>, <whispering>…), a stressed word in CAPITALS,
hesitation with commas, dashes and « … ».
"segments" (optional): [{"texte": "…", "style": "…", "intonation": "montante"|"vive"|"posee"}], the
script cut where the delivery changes; each part goes as its own text item with its own style, in the
same single call. Their words, without the tags and whatever their case, must be exactly the words
of texte.txt (which stays plain: it is what the timing reads). Everything is checked BEFORE the call,
so a mistake never costs a take. Several styled parts for ONE voice is not shown in the documentation
(only for two speakers): voix-bilan.json says how many parts went, and a refusal says so plainly.
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import wave
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "voix"))
import gemini  # noqa: E402

# The inline tags the documentation names (human sounds and pauses; no sound effects).
BALISES = {"argh", "breath", "heavy breath", "exhales", "cackle", "cheer", "chuckle", "chuckles", "cough", "cry",
           "gasp", "giggle", "groan", "growl", "grunt", "grr", "hiss", "laugh", "laughter", "moan", "pant", "pff",
           "phew", "scream", "shout", "shriek", "sigh", "sighs", "sneeze", "snicker", "snort", "sob",
           "throat-clearing", "tsk", "whimper", "whispers", "whispering", "yawn", "short pause", "long pause"}
STYLE_MOTS_MAX = 14


def echec(message):
    print(f"::error::FAILED: {message}")
    sys.exit(1)


def mots_simples(texte):
    """The words a text makes heard: tags out, case and spacing ignored."""
    return re.sub(r"<[^<>]+>", " ", texte).lower().split()


def parties(voix, texte):
    """The text items of the call, checked. Without segments: the whole text with the manifest's style."""
    segs = voix.get("segments")
    if not segs:
        return [{"texte": texte, "style": voix.get("style", "")}]
    for i, s in enumerate(segs, 1):
        if not s.get("texte", "").strip():
            echec(f"segment {i} has no texte")
        for b in re.findall(r"<([^<>]+)>", s["texte"]):
            if b.strip().lower() not in BALISES:
                echec(f"segment {i}: tag <{b}> is not one the voice documentation names ({', '.join(sorted(BALISES))})")
        if len((s.get("style") or "").split()) > STYLE_MOTS_MAX:
            echec(f"segment {i}: style of {len(s['style'].split())} words; keep it under {STYLE_MOTS_MAX} (long styles make the voice drift)")
    dits, script = [m for s in segs for m in mots_simples(s["texte"])], mots_simples(texte)
    if dits != script:
        k = next((j for j, (a, b) in enumerate(zip(dits, script)) if a != b), min(len(dits), len(script)))
        echec(f"the segments do not say texte.txt word for word: from word {k + 1}, segments « {' '.join(dits[k:k + 6])} » "
              f"against texte.txt « {' '.join(script[k:k + 6])} »")
    return [{"texte": " ".join(s["texte"].split()), "style": s.get("style") or voix.get("style", "")} for s in segs]


def dire(cle, modele, nom_voix, items):
    contenu = []
    for it in items:
        bloc = {"type": "text", "text": it["texte"]}
        if it["style"]:
            bloc["annotations"] = [{"type": "speech_metadata", "style": it["style"]}]
        contenu.append(bloc)
    corps = {"model": modele, "input": [{"type": "user_input", "content": contenu}],
             "response_format": {"type": "audio"}, "generation_config": {"speech_config": [{"voice": nom_voix}]}}
    requete = urllib.request.Request(gemini.URL, data=json.dumps(corps).encode("utf-8"), method="POST",
                                     headers={"x-goog-api-key": cle, "Content-Type": "application/json"})
    with urllib.request.urlopen(requete, timeout=240) as reponse:
        return json.loads(reponse.read().decode("utf-8"))


def main():
    projet, sortie = Path(sys.argv[1]), Path(sys.argv[2])
    voix = json.loads((projet / "montage.json").read_text(encoding="utf-8")).get("voix") or echec("montage.json has no voix")
    if not voix.get("voix"):
        echec("montage.json voix.voix is empty: name the voice (the shop profile gives it)")
    texte = " ".join((projet / voix["texte"]).read_text(encoding="utf-8").split())
    if re.search(r"<[^<>]+>", texte):
        echec("texte.txt holds tags: keep it plain (the timing reads it) and put the tags in voix.segments")
    items = parties(voix, texte)
    cle = os.environ.get("GEMINI_API_KEY", "").strip() or echec("the GEMINI_API_KEY secret is not set in the repo")
    modele = voix.get("moteur", "gemini-3.8-flash-tts")
    sortie.mkdir(parents=True, exist_ok=True)
    debut = time.time()
    try:
        reponse = dire(cle, modele, voix["voix"], items)
    except urllib.error.HTTPError as e:
        corps = e.read().decode("utf-8", "replace")[:300]
        if e.code == 429:
            echec("the voice quota of the day is used up (HTTP 429); it comes back at 09:00 Paris time")
        if e.code == 400 and len(items) > 1:
            echec(f"the voice API refused {len(items)} styled parts in one call (HTTP 400: {corps}); "
                  "send the text as one segment with one style")
        echec(f"voice API answered HTTP {e.code}: {corps}")
    octets, genre = gemini.son(reponse)
    if not octets:
        echec("the voice API answered without sound")
    wav = sortie / "voix-brute.wav"
    gemini.en_wav(octets, wav)
    with wave.open(str(wav)) as w:
        secondes = round(w.getnframes() / w.getframerate(), 2)
    bilan = {"voix": voix["voix"], "moteur": modele, "mots_du_texte": len(texte.split()), "parties": len(items),
             "styles": [it["style"] for it in items], "secondes_appel": round(time.time() - debut, 1),
             "secondes_son_brut": secondes, "type": genre, "usage": reponse.get("usage")}
    (sortie / "voix-bilan.json").write_text(json.dumps(bilan, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(bilan, ensure_ascii=False))


if __name__ == "__main__":
    main()
