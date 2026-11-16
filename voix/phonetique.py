"""Compare what was said by sound, not by spelling.

Whisper writes "saillis" for "saillie" or "applic" for "applique": same sounds, counted as
errors by the word error rate. Here both texts are turned into French phonemes (eSpeak NG,
word by word so liaisons do not differ) and compared character by character: the phoneme
error rate (PER). The checked points (names, numbers) are matched the same way.
Needs: pip install phonemizer espeakng-loader jiwer num2words
"""
import re
from functools import lru_cache

from num2words import num2words

_pret = False


def _espeak():
    global _pret
    if not _pret:
        try:  # bundled eSpeak NG library (Windows, macOS, Linux), else the system one
            import espeakng_loader
            from phonemizer.backend.espeak.wrapper import EspeakWrapper
            EspeakWrapper.set_library(espeakng_loader.get_library_path())
            EspeakWrapper.set_data_path(espeakng_loader.get_data_path())
        except ImportError:
            pass
        _pret = True


def mots(texte):
    """Lowercase words with accents kept, digits and 'cm' spelled out."""
    t = texte.lower().replace("’", "'")
    t = re.sub(r"(\d+)[,.](\d+)", lambda m: f"{num2words(int(m[1]), lang='fr')} virgule {num2words(int(m[2]), lang='fr')}", t)
    t = re.sub(r"\d+", lambda m: num2words(int(m[0]), lang="fr"), t)
    t = re.sub(r"\bcms?\b", "centimètres", t)
    return re.findall(r"[a-zàâäçéèêëîïôöùûüÿœæ']+", t.replace("-", " "))


@lru_cache(maxsize=None)
def _phon_mot(mot):
    from phonemizer import phonemize
    _espeak()
    return phonemize(mot, language="fr-fr", backend="espeak", strip=True, with_stress=False)


def phonemes(texte):
    return "".join(_phon_mot(m).replace(" ", "") for m in mots(texte))


def per(reference, hypothese):
    import jiwer
    return jiwer.cer(phonemes(reference), phonemes(hypothese))


def contient(hypothese, attendu):
    return phonemes(attendu) in phonemes(hypothese)
