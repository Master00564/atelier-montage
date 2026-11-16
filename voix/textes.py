"""Test narration read by every voice, and what a correct reading says aloud.

Two takes of the same text: numbers written in words ("lettres") and in digits
("chiffres"), to see which engines read digits correctly.
"""
import re

PRISES = {
    "lettres": (
        "L'Atelier du Lustre. Le lin naturel filtre la lumière et la rend plus douce. "
        "Associé au bois clair, il donne à la chambre une atmosphère calme, typique du "
        "style scandinave. L'applique Linoa mesure vingt-trois centimètres de saillie et "
        "treize centimètres et demi de large."
    ),
    "chiffres": (
        "L'Atelier du Lustre. Le lin naturel filtre la lumière et la rend plus douce. "
        "Associé au bois clair, il donne à la chambre une atmosphère calme, typique du "
        "style scandinave. L'applique Linoa mesure 23 cm de saillie et 13,5 cm de large."
    ),
}

# Spoken form of a correct reading, used to score the back-transcription.
DIT = {
    "lettres": PRISES["lettres"],
    "chiffres": PRISES["lettres"].replace(
        "treize centimètres et demi", "treize virgule cinq centimètres"
    ),
}

# Words whose reading is checked one by one (compared after normalisation, by spelling
# in mesurer.py and by sound in phonetique.py).
POINTS = {
    "nom de la boutique": "Atelier du Lustre",
    "nom du produit": "Linoa",
    "saillie": "vingt-trois centimètres",
    "largeur": {"lettres": "treize centimètres et demi", "chiffres": "treize virgule cinq centimètres"},
}


def phrases(texte):
    """Split a text into sentences (for engines limited to ~13 s per call)."""
    return [p for p in re.split(r"(?<=[.!?])\s+", texte.strip()) if p]
