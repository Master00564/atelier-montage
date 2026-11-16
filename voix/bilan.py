"""Rank the measured voices and write one MP3 per voice plus the ranked rows (JSON).

    python voix/bilan.py OUT_DIR RESULT_DIR [RESULT_DIR ...] --json ROWS.json [--pc PC_DIR]

RESULT_DIR: folders holding WAVs + mesures.json (one per GitHub artifact).
PC_DIR: folder with generation.jsonl from the owner's PC (speed probe only).
A voice is delivered when both takes were generated and measured. One MP3 per voice:
take "lettres", 1 s of silence, take "chiffres", at -16 LUFS +/- 0.3 (peaks under
-1.5 dBFS), 44.1 kHz mono.
Rank: voices whose "lettres" take has a phoneme error rate (PER) of at most 5 % and that
Whisper, left free, hears as French with a probability of at least 0.97 come first, then
the others; inside each group, the higher UTMOS (naturalness) first. Calibration of 0.97
(2026-11-09): native French engines measured 0.982 to 0.9998, Pocket TTS voices made from
English speakers 0.73 to 0.95.
Pronunciation errors listed = Whisper word differences that also differ in sound.
"""
import argparse
import json
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

from choisir import SEUIL_HOMME_HZ, genre as genre_de
from mesurer import ffmpeg, lufs
from phonetique import contient, per, phonemes
from textes import DIT, POINTS

SEUIL_PER = 0.05
SEUIL_FRANCAIS = 0.97


def bon_francais(r):
    return r["per"] <= SEUIL_PER and r["proba_francais"] >= SEUIL_FRANCAIS

# Licence facts checked on 2026-11-08 (sources in the report).
MOTEURS = {
    "supertonic": ("Supertonic 3", "code MIT, modèle OpenRAIL-M : dire que la voix est générée par IA (obligatoire) ; origine des voix non publiée"),
    "kokoro": ("Kokoro", "Apache-2.0 ; voix apprise sur SIWIS (CC BY 4.0) : créditer SIWIS"),
    "piper-mls": ("Piper MLS", "modèle MIT, voix tirées de MLS (CC BY 4.0) : créditer MLS ; logiciel Piper GPL, sans effet sur le son produit"),
    "piper-tom": ("Piper Tom", "À CONFIRMER : enregistrements de Tom sous AGPL, modèle de départ non indiqué"),
    "coqui-css10": ("Coqui CSS10", "modèle BSD-3 ; voix d'un livre audio LibriVox (domaine public)"),
    "pocket": ("Pocket TTS", "code MIT, modèle CC BY 4.0 : créditer « Pocket TTS, Kyutai »"),
    "melo": ("MeloTTS", "MIT ; données d'apprentissage non publiées"),
    "parler": ("Parler-TTS", "Apache-2.0 ; données CML-TTS et MLS (CC BY 4.0) : les créditer"),
    "qwen3-design": ("Qwen3-TTS voix décrite", "Apache-2.0 ; données non publiées"),
    "qwen3-preset": ("Qwen3-TTS voix prête", "Apache-2.0 ; données non publiées ; voix anglaise qui parle français"),
    "voxcpm2": ("VoxCPM2", "Apache-2.0 ; données non publiées"),
    "kyutai": ("Kyutai TTS 1.6B", "code Apache-2.0, modèle CC BY 4.0 : créditer Kyutai ; voix sous CC0"),
    "kyutai-cml": ("Kyutai TTS 1.6B", "code Apache-2.0, modèle CC BY 4.0 : créditer Kyutai ; voix CML-TTS (CC BY 4.0) : créditer CML-TTS"),
    "bark": ("Bark", "MIT ; origine des voix non publiée"),
}
VCTK = {"anna", "azelma", "charles", "eponine", "eve", "fantine", "george", "jane", "mary", "michael", "paul", "vera"}


def licence(moteur, voix):
    texte = MOTEURS[moteur][1]
    if moteur == "pocket":
        texte += " ; voix " + ("VCTK (CC BY 4.0) : créditer VCTK" if voix in VCTK
                               else "Alba McKenna (CC BY 4.0) : la créditer" if voix == "alba" else "CC0")
    return texte


NOMS = {"homme-decrit": "voix d'homme décrite", "femme-decrit": "voix de femme décrite", "FR": "voix française",
        "css10": "Gilles", "tom": "Tom", "ff_siwis": "Siwis", "fabieng-enhanced-v2": "Fabien",
        "Hugo_the_frenchie_enhanced": "Hugo", "developpeuse-3": "Estelle"}


def nom_voix(moteur, voix):
    """Short readable voice name for file names and the table."""
    if moteur == "piper-mls":
        return f"lecteur {voix}"
    if moteur == "kyutai-cml":
        return f"lecteur {Path(voix).stem.split('_')[0]}"
    if moteur == "bark":
        return voix.replace("v2/fr_speaker_", "voix ")
    v = Path(voix).stem if moteur == "kyutai" else voix
    return NOMS.get(v, v.replace("_", " ").title() if moteur == "pocket" else v)


def analyse(r):
    """Phoneme error rate, checked points and real pronunciation errors of one take."""
    h = r["transcription"]
    points = {nom: contient(h, a[r["prise"]] if isinstance(a, dict) else a) for nom, a in POINTS.items()}
    fautes = []
    for f in r["fautes"]:
        ref, hyp = (x.strip() for x in f.split("->"))
        if phonemes(ref.replace("-", "")) != phonemes(hyp.replace("-", "")):
            fautes.append(f"« {hyp} » en trop" if ref == "-" else f"« {ref} » manquant" if hyp == "-"
                          else f"« {ref} » entendu « {hyp} »")
    return per(DIT[r["prise"]], h), points, fautes


CIBLE_LUFS, ECART_LUFS = -16.0, 0.3


def mp3(lettres, chiffres, sortie):
    """Both takes, 1 s apart, at -16 LUFS (+/- 0.3) with peaks held under -1.5 dBFS.
    FFmpeg's loudnorm left some files 1 to 2.6 LU low (it gives way to the peak limit), so the
    gain is set from the measured loudness and corrected until the MP3 itself measures right."""
    a, sr = sf.read(lettres, dtype="float32")
    b, sr2 = sf.read(chiffres, dtype="float32")
    assert sr == sr2
    with tempfile.TemporaryDirectory() as t:
        wav = Path(t) / "x.wav"
        sf.write(wav, np.concatenate([a, np.zeros(sr, np.float32), b]), sr, subtype="PCM_16")
        gain = CIBLE_LUFS - lufs(wav)
        for _ in range(8):
            filtre = f"volume={gain:.2f}dB,alimiter=limit=0.84:level=0,aresample=44100"
            subprocess.run([ffmpeg(), "-hide_banner", "-loglevel", "error", "-y", "-i", str(wav), "-af", filtre,
                            "-ac", "1", "-c:a", "libmp3lame", "-b:a", "160k", str(sortie)], check=True)
            mesure = lufs(sortie)
            if abs(mesure - CIBLE_LUFS) <= ECART_LUFS:
                break
            gain += CIBLE_LUFS - mesure
    return mesure


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("sortie", type=Path)
    ap.add_argument("dossiers", type=Path, nargs="+")
    ap.add_argument("--pc", type=Path)
    ap.add_argument("--json", type=Path, required=True, help="where to write the ranked rows")
    a = ap.parse_args()

    mesures, ou = {}, {}
    for d in a.dossiers:
        for f, r in json.loads((d / "mesures.json").read_text(encoding="utf-8")).items():
            mesures[f], ou[f] = r, d
    pc = {}
    if a.pc and (a.pc / "generation.jsonl").exists():
        for l in (a.pc / "generation.jsonl").read_text(encoding="utf-8").splitlines():
            g = json.loads(l)
            pc[g["moteur"]] = min(g["rtf"], pc.get(g["moteur"], 1e9))

    voix = {}
    for f, r in mesures.items():
        requis = ("transcription", "proba_francais", "f0_median_hz") + (("utmos",) if r.get("prise") == "lettres" else ())
        if (ou[f] / f).exists() and all(r.get(k) is not None for k in requis):  # the rank uses the "lettres" take
            r["per"], r["points_son"], r["fautes_son"] = analyse(r)
            voix.setdefault((r["moteur"], r["voix"]), {})[r["prise"]] = r
    complets = [(k, v) for k, v in voix.items() if {"lettres", "chiffres"} <= set(v)]
    complets.sort(key=lambda kv: (not bon_francais(kv[1]["lettres"]), -kv[1]["lettres"]["utmos"]))

    a.sortie.mkdir(parents=True, exist_ok=True)
    lignes = []
    for n, ((moteur, v), p) in enumerate(complets, 1):
        l, c = p["lettres"], p["chiffres"]
        genre = genre_de(l)
        nom = f"{n:02d} - {MOTEURS[moteur][0]} - {nom_voix(moteur, v)} ({genre}).mp3"
        lignes.append({
            "n": n, "fichier": nom, "moteur": moteur, "moteur_nom": MOTEURS[moteur][0],
            "voix": nom_voix(moteur, v), "genre": genre, "licence": licence(moteur, v),
            "utmos": l["utmos"], "per_lettres": round(l["per"], 3), "bon_francais": bon_francais(l),
            "proba_francais": l["proba_francais"], "proba_francais_chiffres": c["proba_francais"], "per_chiffres": round(c["per"], 3),
            "wer_lettres": l["wer"], "wer_chiffres": c["wer"],
            "chiffres_ok": c["points_son"]["saillie"] and c["points_son"]["largeur"],
            "points_lettres": l["points_son"], "fautes": l["fautes_son"], "fautes_chiffres": c["fautes_son"],
            "transcription_chiffres": c["transcription"],
            "rtf": l["rtf"], "machine": l["machine"], "ram_pic_mo": l["ram_pic_mo"], "rtf_pc": pc.get(moteur),
            "f0": l["f0_median_hz"], "voix_grave_ou_aigue": (l["f0_median_hz"] < SEUIL_HOMME_HZ) != (genre == "homme"), "ecart_demitons": l["f0_ecart_demitons"], "mots_min": l["mots_par_minute"],
            "lufs_final": round(mp3(ou[l["fichier"]] / l["fichier"], ou[c["fichier"]] / c["fichier"], a.sortie / nom), 1),
        })
        print(n, nom, lignes[-1]["per_lettres"], l["utmos"], flush=True)
    a.json.write_text(json.dumps(lignes, ensure_ascii=False, indent=1), encoding="utf-8")
    a.json.with_suffix(".md").write_text(tableau(lignes), encoding="utf-8")


def virgule(x, d=1):
    return f"{x:.{d}f}".replace(".", ",")


def tableau(lignes):
    """French table rows, in plain words, for the owner."""
    t = ["| N° | Voix | Homme ou femme | Licence et crédit à mettre | Où ça tourne, vitesse | Prononciation (texte en lettres) | Chiffres « 23 cm », « 13,5 cm » |",
         "|---|---|---|---|---|---|---|"]
    for r in lignes:
        vitesse = f"GitHub, gratuit : {virgule(r['rtf'] * 10)} s de calcul pour 10 s de voix"
        if r["rtf_pc"]:
            vitesse += f" ; PC local : {virgule(r['rtf_pc'] * 10)} s"
        prononce = "aucune faute entendue" if not r["fautes"] else " ; ".join(r["fautes"][:3])
        if r["proba_francais"] < SEUIL_FRANCAIS:
            prononce = "accent étranger (" + virgule(r["proba_francais"] * 100, 0) + " % français pour Whisper) ; " + prononce
        prononce += f" (naturel {virgule(r['utmos'])}/5, erreurs de sons {virgule(r['per_lettres'] * 100)} %)"
        texte = r["transcription_chiffres"]
        debut = texte.lower().find("mesure")
        entendu = texte[debut:] if debut >= 0 else texte[-70:]
        chiffres = ("lus juste" if r["chiffres_ok"] else "mal lus") + f" ; entendu : « {entendu.strip()} »"
        genre = r["genre"] + ((" (voix grave)" if r["genre"] == "femme" else " (voix aiguë)") if r["voix_grave_ou_aigue"] else "")
        t.append(f"| {r['n']} | {r['voix']} ({r['moteur_nom']}) | {genre} | {r['licence']} | {vitesse} | {prononce} | {chiffres} |")
    return "\n".join(t) + "\n"


if __name__ == "__main__":
    main()
