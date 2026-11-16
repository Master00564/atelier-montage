#!/usr/bin/env python3
"""Theme video build step, run by render.yml between "prepare" and "render" for a job with "theme".

    python scripts/theme.py            reads out/job.json, writes the soundtrack and the props

What it does, all from the job (nothing about a shop or a theme is written here):
1. Voice: the chosen take (theme.voix.fichier, its Whisper words theme.voix.mots, from voix.yml).
   A looping video is cut at the spoken join (end of the last line, start of the hook) and turned
   around, so the last sample of the video leads straight into the first one. The silences between
   lines are then stretched or shortened (and the take sped up if it must) so the voice fills the
   video exactly (theme.duree, 60 s by default).
2. Music: an original piece synthesised here (theme.musique: style, tempo, seed), written as a
   circle: notes and reverb that ring past the end come back at the start.
3. Timeline: one shot per line (more if the line asks), cut on the music beat just before the
   line's first word; captions word by word on the voice; headlines on their spoken word.
4. Sound effects (original, synthesised): whoosh on transitions, soft hit on headlines, shimmer on
   gold reveals, riser into the loop point. Music ducked under the voice. Master at
   theme.sonie (-14 LUFS by default), true peak at most -1 dBTP.
Writes assets/job/bande.wav in the composition and out/props.json (timeline as one JSON string).
"""
import json
import math
import re
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "voix"))
from alignement import caler_texte, jetons, parle  # noqa: E402

SR = 48000
OUT = ROOT / "out"


def echec(msg):
    print(f"FAILED: {msg}")
    print(f"::error title=theme failed::{msg}")
    sys.exit(1)


# ------------------------------------------------------------------ audio helpers
def lire_audio(chemin):
    """Any audio file -> mono float32 at SR, decoded by FFmpeg."""
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", str(chemin), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                       capture_output=True, check=True)
    return np.frombuffer(p.stdout, dtype=np.float32).copy()


def tempo(x, facteur):
    """Speed a voice up or down without changing its pitch (FFmpeg atempo)."""
    p = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                        "-af", f"atempo={facteur:.5f}", "-f", "f32le", "-"], input=x.astype(np.float32).tobytes(),
                       capture_output=True, check=True)
    return np.frombuffer(p.stdout, dtype=np.float32).copy()


def ecrire_wav(chemin, x):
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(str(chemin), "wb") as w:
        w.setnchannels(x.shape[1] if x.ndim == 2 else 1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def _k(freqs):
    """K weighting of ITU-R BS.1770 at SR (shelf, then high-pass), as a frequency response."""
    def bq(gain, q, fc, shelf):
        A, w0 = 10 ** (gain / 40), 2 * np.pi * fc / SR
        al, co = np.sin(w0) / (2 * q), np.cos(w0)
        if shelf:
            r = 2 * np.sqrt(A) * al
            b = [A * ((A + 1) + (A - 1) * co + r), -2 * A * ((A - 1) + (A + 1) * co), A * ((A + 1) + (A - 1) * co - r)]
            a = [(A + 1) - (A - 1) * co + r, 2 * ((A - 1) - (A + 1) * co), (A + 1) - (A - 1) * co - r]
        else:
            b, a = [(1 + co) / 2, -(1 + co), (1 + co) / 2], [1 + al, -2 * co, 1 - al]
        z = np.exp(-2j * np.pi * freqs / SR)
        return (b[0] + b[1] * z + b[2] * z * z) / (a[0] + a[1] * z + a[2] * z * z)
    return bq(3.999843853973347, 0.7071752369554196, 1681.974450955533, True) * bq(0.0, 0.5003270373238773, 38.13547087602444, False)


def sonie(x):
    """Integrated loudness in LUFS (BS.1770-4: K weighting, 400 ms blocks, gates -70 and -10)."""
    x = x if x.ndim == 2 else x[:, None]
    n = int(2 ** np.ceil(np.log2(len(x) + SR)))
    k = _k(np.fft.rfftfreq(n, 1 / SR))
    y = np.stack([np.fft.irfft(np.fft.rfft(x[:, c], n) * k, n)[: len(x)] for c in range(x.shape[1])], 1)
    bloc, pas = int(0.4 * SR), int(0.1 * SR)
    z = np.array([(y[i:i + bloc] ** 2).mean(0).sum() for i in range(0, len(y) - bloc + 1, pas)])
    z = z[-0.691 + 10 * np.log10(z + 1e-20) > -70]
    z = z[-0.691 + 10 * np.log10(z + 1e-20) > -0.691 + 10 * np.log10(z.mean()) - 10]
    return float(-0.691 + 10 * np.log10(z.mean()))


def crete_vraie(x):
    """True peak in dBTP (4x oversampling by FFT)."""
    x = x if x.ndim == 2 else x[:, None]
    m = max(float(np.abs(np.fft.irfft(np.fft.rfft(x[:, c]), 4 * len(x))).max()) * 4 for c in range(x.shape[1]))
    return 20 * np.log10(m + 1e-12)


def lisser_circulaire(e, attaque, relache):
    """Envelope follower on a loop (the end feeds the start): fast up, slow down. e per 10 ms frame."""
    a, r = math.exp(-0.01 / attaque), math.exp(-0.01 / relache)
    v, sortie = 0.0, np.zeros_like(e)
    for _ in range(2):  # second pass starts from the loop's own end state
        for i, x in enumerate(e):
            v = a * v + (1 - a) * x if x > v else r * v + (1 - r) * x
            sortie[i] = v
    return sortie


def convoluer_circulaire(x, ir):
    n = len(x)
    h = np.zeros(n)
    h[: min(n, len(ir))] = ir[:n]
    return np.fft.irfft(np.fft.rfft(x) * np.fft.rfft(h), n)


def limiteur_circulaire(x, plafond_db):
    """Brick-wall limiter on a loop: gain from the oversampled peak, 5 ms look-ahead, 80 ms release."""
    plafond = 10 ** (plafond_db / 20)
    n = len(x)
    bloc = 48  # 1 ms blocks: the gain is computed per block, then interpolated per sample
    nb = n // bloc
    pic = np.abs(x[: nb * bloc]).max(1).reshape(nb, bloc).max(1)
    tr = 1.12  # inter-sample peaks run up to ~1 dB above the sample peak on this material
    besoin = np.minimum(1.0, plafond / np.maximum(pic * tr, 1e-9))
    g = np.minimum.reduce([np.roll(besoin, -k) for k in range(6)])  # 5 ms look-ahead
    rel = math.exp(-1 / 80)  # 80 ms release
    sortie = np.empty(nb)
    v = 1.0
    for _ in range(2):  # circular: the second pass starts from the end state
        for i in range(nb):
            v = g[i] if g[i] < v else rel * v + (1 - rel) * g[i]
            sortie[i] = v
    gain = np.interp(np.arange(n), np.arange(nb) * bloc + bloc / 2, sortie, period=n)
    return x * gain[:, None]


# ------------------------------------------------------------------ music
NOTES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def hz(n):
    k = NOTES[n[0]] + n[1:-1].count("#") - n[1:-1].count("b")
    return 440.0 * 2 ** ((k + 12 * (int(n[-1]) + 1) - 69) / 12)


def piano(f, duree, vel, rng):
    """Additive piano tone: two slightly detuned strings, stretched partials, hammer noise."""
    n = int(duree * SR)
    t = np.arange(n) / SR
    v = np.zeros(n)
    clair = 0.5 + 0.5 * vel
    for h in range(1, 9):
        fh = f * h * math.sqrt(1 + 0.00035 * h * h)
        a = (clair ** (h - 1)) / h ** 1.15
        dec = 1.1 + 0.55 * h + f / 600
        for det in (-0.0009, 0.0009):
            v += a * np.sin(2 * np.pi * fh * (1 + det) * t + rng.uniform(0, 6.28)) * np.exp(-t * dec)
    v *= (1 - np.exp(-t * 400))
    v[: int(0.012 * SR)] += rng.standard_normal(int(0.012 * SR)) * 0.08 * vel * np.exp(-np.arange(int(0.012 * SR)) / 90)
    rel = int(0.08 * SR)
    v[-rel:] *= np.linspace(1, 0, rel)
    return v * vel


def contrebasse(f, duree):
    n = int(duree * SR)
    t = np.arange(n) / SR
    v = sum(np.sin(2 * np.pi * f * h * t) * np.exp(-t * (2.2 + 1.5 * h)) / h ** 1.6 for h in range(1, 6))
    v *= 1 - np.exp(-t * 250)
    return v


def balais(duree, rng, coup):
    """Brush swish (coup=False) or a closed hi-hat 'chick' (coup=True)."""
    n = int(duree * SR)
    b = rng.standard_normal(n)
    b = np.diff(np.concatenate([[0], b]))  # brighter
    t = np.arange(n) / SR
    env = np.exp(-t * (38 if coup else 9)) * (1 - np.exp(-t * (900 if coup else 60)))
    return b * env * (0.6 if coup else 0.25)


def grosse_caisse(duree=0.35):
    n = int(duree * SR)
    t = np.arange(n) / SR
    f = 52 + 40 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)


def poser(piste, son, debut, gain=1.0, pan=0.5):
    """Add a sound on a looping track: what passes the end comes back at the start."""
    n = len(piste)
    i = int(round(debut * SR)) % n
    son = son * gain
    st = np.stack([son * math.sqrt(1 - pan), son * math.sqrt(pan)], 1) if son.ndim == 1 else son
    k = 0
    while k < len(st):
        m = min(len(st) - k, n - i)
        piste[i:i + m] += st[k:k + m]
        k += m
        i = 0


GRILLES = {
    # 1920s stride piano: ragtime circle-of-fifths changes, 8 bars per phrase, 4 phrases (32 bars).
    "stride-1925": [
        ["F6", "D7", "G7", "C7", "F6", "D7", "Gm7|C7", "F6|C7"],
        ["F6", "D7", "G7", "C7", "A7", "Dm7", "G7|C7", "F6"],
        ["Bb6", "Bdim7", "F6", "D7", "G7", "C7", "F6|D7", "Gm7|C7"],
        ["F6", "D7", "G7", "C7", "F6", "Bb6|Bdim7", "F6|D7", "Gm7|C7"],
    ],
}
ACCORDS = {  # (bass root, chord tones in the middle register)
    "F6": ("F2", ["A3", "C4", "D4", "F4"]), "D7": ("D2", ["F#3", "C4", "D4", "A4"]),
    "G7": ("G2", ["F3", "B3", "D4", "G4"]), "C7": ("C2", ["E3", "Bb3", "C4", "G4"]),
    "Gm7": ("G2", ["F3", "Bb3", "D4", "G4"]), "A7": ("A2", ["G3", "C#4", "E4", "A4"]),
    "Dm7": ("D2", ["F3", "A3", "C4", "D4"]), "Bb6": ("Bb2", ["F3", "G3", "Bb3", "D4"]),
    "Bdim7": ("B2", ["F3", "Ab3", "B3", "D4"]),
}
QUINTE = {"F2": "C2", "D2": "A2", "G2": "D2", "C2": "G2", "A2": "E2", "Bb2": "F2", "B2": "F2"}


def musique(duree, bpm, graine, style):
    if style not in GRILLES:
        echec(f'theme.musique.style "{style}" unknown (known: {", ".join(GRILLES)})')
    rng = np.random.default_rng(graine)
    n = int(round(duree * SR))
    battue = 60.0 / bpm
    mesures = round(duree / (4 * battue))
    if abs(mesures * 4 * battue - duree) > 1e-6:
        echec(f"theme.musique.tempo {bpm} does not fit {duree} s in whole bars (loop): pick a tempo giving whole bars")
    p = np.zeros((n, 2))
    grille = [c for phrase in GRILLES[style] for c in phrase]
    swing = 2 / 3  # swung eighths: the off-beat at two thirds of the beat
    for m in range(mesures):
        cases = grille[m % len(grille)].split("|")
        for b in range(4):
            accord = cases[0] if (len(cases) == 1 or b < 2) else cases[1]
            basse, voix = ACCORDS[accord]
            t = (m * 4 + b) * battue
            if b % 2 == 0:  # stride left hand: bass on 1 and 3 (root, then fifth), plucked bass under it
                note = basse if (b == 0 or len(cases) > 1) else QUINTE.get(basse, basse)
                poser(p, piano(hz(note), 1.2, 0.75, rng), t, 0.36, 0.42)
                poser(p, contrebasse(hz(note) / 2 if hz(note) > 70 else hz(note), 0.9), t, 0.30, 0.5)
                poser(p, grosse_caisse(), t, 0.10, 0.5)
            else:  # chord on 2 and 4, short
                for k, nt in enumerate(voix):
                    poser(p, piano(hz(nt), 0.45, 0.55, rng), t + 0.006 * k, 0.15, 0.58)
                poser(p, balais(0.12, rng, True), t, 0.11, 0.62)
            poser(p, balais(battue * 0.9, rng, False), t, 0.06, 0.4)
            poser(p, balais(0.1, rng, True), t + battue * swing, 0.05, 0.66)
        # Right hand: a light swung figure on the chord tones, every other bar, louder in the last phrase bar.
        if m % 2 == 1:
            _, voix = ACCORDS[cases[-1]]
            motif = [voix[-1], voix[-2], voix[-1], voix[1]]
            for k, nt in enumerate(motif):
                t = (m * 4 + 2) * battue + (k // 2) * battue + (k % 2) * battue * swing
                poser(p, piano(hz(nt) * 2, 0.7, 0.45, rng), t, 0.09, 0.7)
    # Small room, circular (the tail of bar 32 rings into bar 1).
    t = np.arange(int(1.1 * SR)) / SR
    salle = np.stack([rng.standard_normal(len(t)) * np.exp(-t * 5.5) for _ in range(2)], 1)
    salle /= np.sqrt((salle ** 2).sum(0))
    rev = np.stack([convoluer_circulaire(p[:, c], salle[:, c]) for c in range(2)], 1)
    return 0.8 * p + 0.35 * rev


# ------------------------------------------------------------------ sound effects (original)
def bruit_filtre(n, rng, f0, f1, q=0.6):
    """Noise through a resonant band-pass whose centre glides from f0 to f1 (state-variable filter)."""
    x = rng.standard_normal(n)
    f = np.geomspace(f0, f1, n)
    lp = bp = 0.0
    y = np.empty(n)
    for i in range(n):
        g = 2 * math.sin(math.pi * f[i] / SR)
        hp = x[i] - lp - q * bp
        bp += g * hp
        lp += g * bp
        y[i] = bp
    return y / (np.abs(y).max() + 1e-9)


def sfx_whoosh(rng, duree=0.55):
    n = int(duree * SR)
    t = np.linspace(0, 1, n)
    env = np.sin(np.pi * t ** 0.7) ** 2
    s = bruit_filtre(n, rng, 300, 2600) * env
    pan = 0.15 + 0.7 * t
    return np.stack([s * np.sqrt(1 - pan), s * np.sqrt(pan)], 1)


def sfx_coup(rng, duree=0.5):
    n = int(duree * SR)
    t = np.arange(n) / SR
    f = 70 + 60 * np.exp(-t * 25)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    s[: int(0.01 * SR)] += rng.standard_normal(int(0.01 * SR)) * 0.25 * np.exp(-np.arange(int(0.01 * SR)) / 60)
    return s


def sfx_clic(rng, duree=0.06):
    n = int(duree * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * 1850 * t) * np.exp(-t * 90) + rng.standard_normal(n) * 0.1 * np.exp(-t * 300)


def sfx_scintillement(rng, duree=1.4):
    n = int(duree * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for k in range(9):
        d = rng.uniform(0, 0.45)
        f = rng.choice([2093.0, 2637.0, 3136.0, 3520.0, 4186.0]) * rng.uniform(0.997, 1.003)
        tt = np.clip(t - d, 0, None)
        s += (t >= d) * np.sin(2 * np.pi * f * tt) * np.exp(-tt * rng.uniform(4, 7)) * rng.uniform(0.4, 1)
    return s * (1 - np.exp(-t * 300))


def sfx_monte(rng, duree=1.6):
    n = int(duree * SR)
    t = np.linspace(0, 1, n)
    s = bruit_filtre(n, rng, 200, 5000, q=0.4) * t ** 2.2
    s += np.sin(2 * np.pi * np.cumsum(np.geomspace(180, 900, n)) / SR) * t ** 3 * 0.35
    s[-int(0.01 * SR):] *= np.linspace(1, 0, int(0.01 * SR))
    return s


# ------------------------------------------------------------------ text helpers
def norm(m):
    return " ".join(parle(m))


def couper_lignes(mots, largeur):
    """Split a caption page into 1 or 2 balanced lines (chars per line <= largeur)."""
    texte = " ".join(mots)
    if len(texte) <= largeur:
        return [mots]
    best = None
    for k in range(1, len(mots)):
        a, b = " ".join(mots[:k]), " ".join(mots[k:])
        if max(len(a), len(b)) > largeur:
            continue
        cout = abs(len(a) - len(b)) + (6 if len(b) < 0.6 * len(a) else 0)
        if best is None or cout < best[0]:
            best = (cout, k)
    return [mots[:best[1]], mots[best[1]:]] if best else None


def pages(jetons, largeur, max_mots=7):
    """Caption pages: at most 2 balanced lines each, breaking after punctuation when possible."""
    out, cur = [], []
    for i, j in enumerate(jetons):
        cur.append(j)
        txt = [x[0] for x in cur]
        fin_phrase = re.search(r"[.,:;!?…]$", j[0]) is not None
        trop = couper_lignes(txt, largeur) is None or len(cur) > max_mots
        if trop:
            cur.pop()
            out.append(cur)
            cur = [j]
        elif fin_phrase and len(" ".join(txt)) >= largeur * 0.9:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    # Never leave a lone short word: merge it back if the lines still fit.
    i = 1
    while i < len(out):
        if len(" ".join(x[0] for x in out[i])) < largeur * 0.35 and couper_lignes([x[0] for x in out[i - 1] + out[i]], largeur):
            out[i - 1] += out.pop(i)
        else:
            i += 1
    return out


def coller(jetons):
    """French typography in captions: « sticks to the next word, » : ; ! ? to the previous one, with a
    no-break space, so a line never starts or ends on a lone sign."""
    out = []
    for j, a, b in jetons:
        if out and re.fullmatch(r"[»:;!?…]+[.,]?", j):
            pj, pa, pb = out[-1]
            out[-1] = (pj + " " + j, pa, max(pb, b))
        elif out and out[-1][0] == "«":
            out[-1] = ("« " + j, a, b)
        else:
            out.append((j, a, b))
    return out


# ------------------------------------------------------------------ main
def main():
    job = json.loads((OUT / "job.json").read_text(encoding="utf-8"))
    th = job["theme"]
    D = float(th.get("duree", 60))
    fps = int(job.get("expect", {}).get("fps", 30))
    lignes = th["lignes"]
    n = len(lignes)
    boucle = bool(th.get("boucle"))
    ordre = list(range(1, n)) + [0] if boucle else list(range(n))
    v = th.get("voix", {})
    for cle in ("fichier", "mots"):
        if not (ROOT / str(v.get(cle, ""))).is_file():
            echec(f"theme.voix.{cle} missing or not a repo file: run voix.yml with theme:<this job> and commit the chosen take")
    stage = ROOT / "hyperframes" / job["composition"] / "assets" / "job"
    stage.mkdir(parents=True, exist_ok=True)

    # 1. Voice: words of the take, matched to the script in reading order.
    rapport = json.loads((ROOT / v["mots"]).read_text(encoding="utf-8"))
    voix = lire_audio(ROOT / v["fichier"])
    dit = " ".join(lignes[i]["dit"] for i in ordre)
    cal = caler_texte(dit, rapport["mots"])
    k, spans = 0, {}
    for i in ordre:
        m = len(jetons(lignes[i]["dit"]))
        spans[i] = (cal[k][1], cal[k + m - 1][2])
        k += m

    def energie_min(a, b):
        """Quietest 10 ms point between a and b (s), snapped to a zero crossing."""
        a, b = max(0, int(a * SR)), min(len(voix) - 1, int(b * SR))
        if b - a < int(0.012 * SR):
            c = (a + b) // 2
        else:
            w = int(0.01 * SR)
            e = np.convolve(voix[a:b] ** 2, np.ones(w) / w, mode="same")
            c = a + int(np.argmin(e))
        z = np.where(np.diff(np.signbit(voix[max(0, c - 240):c + 240])))[0]
        return (max(0, c - 240) + int(z[np.argmin(np.abs(z - 240))])) if len(z) else c

    # Whisper's word edges can be 0.1-0.2 s late: borders are taken from the sound itself. The 10 ms
    # energy finds the silences (a pause, or the closure of a consonant such as the "p" of "Paris");
    # the border is the last silence before the next line's first word, so a cut never falls inside it.
    w10 = int(0.01 * SR)
    env = 20 * np.log10(np.sqrt((voix[: len(voix) // w10 * w10].reshape(-1, w10) ** 2).mean(1)) + 1e-9)
    seuil_db = float(env.max()) - 40.0

    def coupure(fin_avant, debut_apres):
        a, b = max(0, int((fin_avant - 0.30) * 100)), min(len(env), int((debut_apres + 0.06) * 100))
        bas = np.where(env[a:b] < seuil_db)[0]
        if not len(bas):
            return energie_min(fin_avant - 0.04, debut_apres + 0.04)
        runs = np.split(bas, np.where(np.diff(bas) > 1)[0] + 1)
        r = runs[-1]  # the silence nearest the next word
        k = a + int(r[np.argmin(env[a + r])])
        return energie_min((k - 1) / 100, (k + 2) / 100)

    bornes = {}
    for a_, b_ in zip(ordre, ordre[1:]):
        bornes[(a_, b_)] = coupure(spans[a_][1], spans[b_][0])
    debut = energie_min(max(0, spans[ordre[0]][0] - 0.25), spans[ordre[0]][0])
    fin = energie_min(spans[ordre[-1]][1], min(len(voix) / SR, spans[ordre[-1]][1] + 0.3))
    seg = {}
    for idx, i in enumerate(ordre):
        s0 = debut if idx == 0 else bornes[(ordre[idx - 1], i)]
        s1 = fin if idx == n - 1 else bornes[(i, ordre[idx + 1])]
        seg[i] = (s0, s1)
    # Trim each segment's silence to at most 80 ms on each side (the seam side of a loop stays untouched).
    garde = int(0.08 * SR)
    seuil = 10 ** (-42 / 20) * max(1e-6, np.abs(voix).max())
    for i in ordre:
        s0, s1 = seg[i]
        joint_debut = boucle and i == 0            # hook starts at the seam
        joint_fin = boucle and i == ordre[-2]      # line before the hook in reading order ends at the seam
        # first and last sounding 10 ms of the segment (energy, not Whisper's edges)
        fort = np.where(env[s0 // w10: s1 // w10 + 1] >= seuil_db - 5)[0]
        a_ = (s0 // w10 + int(fort[0])) * w10 - garde if len(fort) else s0
        b_ = (s0 // w10 + int(fort[-1]) + 1) * w10 + garde if len(fort) else s1
        if not joint_debut:
            s0 = max(s0, min(a_, s1))
        if not joint_fin:
            s1 = min(s1, max(b_, s0))
        seg[i] = (s0, s1)
    parole = sum(seg[i][1] - seg[i][0] for i in ordre) / SR
    # Pauses between lines (the loop join has none): a breath after a sentence, a short one after a
    # comma, a longer one where the job asks ("pause": true). The take is then sped up or slowed down
    # (at most 8 % slower, 12 % faster) so voice + pauses fill the video exactly.
    piste_ordre = [0] + list(range(1, n)) if boucle else ordre
    voulu = []
    for i in piste_ordre[:-1]:
        l = lignes[i]
        voulu.append(0.55 if l.get("pause") else (0.34 if re.search(r"[.!?…]\s*$", l["dit"]) else 0.18))
    facteur = parole / max(1e-6, D - sum(voulu))
    if facteur < 1.0:  # voice too short: natural speed and longer pauses, slowed only past 0.75 s a pause
        facteur = min(1.0, max(0.92, parole / max(1e-6, D - 0.75 * len(voulu))))
    if facteur > 1.08:  # voice too long: shorten the pauses down to 60 %, then speed up
        voulu = [x * 0.6 for x in voulu]
        facteur = parole / (D - sum(voulu))
    if facteur > 1.12:
        echec(f"the voice lasts {parole:.1f} s: too long for {D} s even sped up 12 %; shorten the lines")
    # Speed each line first, then size the pauses from the real lengths (atempo rounds every segment).
    morceaux_voix = {}
    for i in piste_ordre:
        s0, s1 = seg[i]
        morceaux_voix[i] = tempo(voix[s0:s1], facteur) if facteur != 1.0 else voix[s0:s1]
    reel = sum(len(x) for x in morceaux_voix.values()) / SR
    reste = D - reel - sum(voulu)
    if reste < -0.6 * sum(voulu):
        echec(f"the voice lasts {reel:.2f} s after speed-up: no room for pauses in {D} s")
    ajouts = [x + reste * x / sum(voulu) for x in voulu]
    if max(ajouts) > 1.2:
        print(f"note: long pauses ({max(ajouts):.2f} s): the voice is short for {D} s")
    # Assemble: hook first, then lines 1..n-1; times of every display word mapped to the new track.
    morceaux, t, offs = [], 0.0, {}
    N = int(round(D * SR))
    gaps_n = [int(round(x * SR)) for x in ajouts]
    gaps_n[-1] += N - (sum(len(x) for x in morceaux_voix.values()) + sum(gaps_n))  # exact length, to the sample
    for idx, i in enumerate(piste_ordre):
        x = morceaux_voix[i]
        offs[i] = (t, seg[i][0] / SR, facteur)
        morceaux.append(x)
        t += len(x) / SR
        if idx < len(gaps_n):
            morceaux.append(np.zeros(gaps_n[idx]))
            t += gaps_n[idx] / SR
    piste = np.concatenate(morceaux)
    if abs(len(piste) - N) > SR * 0.05:
        echec(f"voice assembly is {len(piste) / SR:.3f} s, expected {D} s")
    piste = np.pad(piste, (0, max(0, N - len(piste))))[:N]
    # Display words (ecran) timed on the new track.
    ecran_ordre = " ".join(lignes[i]["ecran"] for i in ordre)
    cal_e = caler_texte(ecran_ordre, rapport["mots"])
    mots_lignes, k = {}, 0
    for i in ordre:
        m = len(jetons(lignes[i]["ecran"]))
        o, s0, f = offs[i]
        mots_lignes[i] = coller([(j, o + (a - s0) / f, o + (b - s0) / f) for j, a, b in cal_e[k:k + m]])
        k += m
    debut_ligne = {i: max(0.0, mots_lignes[i][0][1]) for i in range(n)}

    # 2. Music
    mu = th.get("musique", {})
    bpm = float(mu.get("tempo", 128))
    zik = musique(D, bpm, int(mu.get("graine", 1)), mu.get("style", "stride-1925"))
    battue = 60 / bpm
    beats = [round(k * battue, 4) for k in range(int(round(D / battue)))]

    # 3. Timeline: shots
    def cut_avant(t):
        cands = [b for b in beats if t - 0.36 <= b <= t - 0.02]
        return max(cands) if cands else max(0.0, t - 0.08)

    def temps_mot(i, sur):
        if not sur:
            return None
        cible = norm(sur)
        for j, a, b in mots_lignes[i]:
            if cible and (f" {cible} " in f" {norm(j)} " or norm(j).startswith(cible)):
                return a
        echec(f'line {i}: word "{sur}" (sur) not found in its ecran text')

    plans = []
    for i in range(n):
        ps = lignes[i].get("plans") or [{}]
        t0 = 0.0 if (boucle and i == 0) else cut_avant(debut_ligne[i])
        for p_i, p in enumerate(ps):
            q = dict(p)
            q["ligne"] = i
            q["debut"] = round(t0 if p_i == 0 else max(t0 + 0.6, cut_avant(temps_mot(i, p.get("sur")) or t0)), 3)
            if q.get("titre"):
                ti = dict(q["titre"])
                tw = temps_mot(i, ti.get("sur")) if ti.get("sur") else q["debut"] + 0.12
                ti["t"] = round(max(q["debut"] + 0.05, tw - 0.06), 3)
                q["titre"] = ti
            if q.get("compteur"):
                c = dict(q["compteur"])
                c["t"] = round((temps_mot(i, c.get("sur")) or q["debut"]) - 0.06, 3)
                q["compteur"] = c
            for key in ("image", "detoure"):
                if q.get(key):
                    q[key] = f"assets/job/{q[key]}"
            if q.get("recap"):
                q["recap"] = [f"assets/job/{r}" for r in q["recap"]]
            plans.append(q)
    plans.sort(key=lambda q: q["debut"])
    for a_, b_ in zip(plans, plans[1:]):
        a_["fin"] = b_["debut"]
    plans[-1]["fin"] = D
    for q in plans:
        if q["fin"] - q["debut"] < 0.5:
            echec(f"shot of line {q['ligne']} lasts {q['fin'] - q['debut']:.2f} s (< 0.5 s): fewer shots on that line")
    # Captions
    larg = int(th.get("sous_titres_largeur", 24))
    st = []
    for i in range(n):
        accent = {norm(a) for a in lignes[i].get("accent", [])}
        for pg in pages(mots_lignes[i], larg):
            lignes_pg = couper_lignes([x[0] for x in pg], larg)
            k, rows = 0, []
            for row in lignes_pg:
                rows.append([{"m": x[0], "t": round(x[1], 3), "a": int(norm(x[0]) in accent)} for x in pg[k:k + len(row)]])
                k += len(row)
            st.append({"debut": round(pg[0][1] - 0.08, 3), "fin_mots": round(pg[-1][2], 3), "lignes": rows})
    st.sort(key=lambda s: s["debut"])
    for a_, b_ in zip(st, st[1:]):
        a_["fin"] = round(min(b_["debut"], a_["fin_mots"] + 0.9), 3)
    st[-1]["fin"] = round(D if boucle else st[-1]["fin_mots"] + 0.6, 3)
    if boucle:
        st[0]["debut"] = max(0.0, st[0]["debut"])

    # 4. Sound effects, ducking, master
    rng = np.random.default_rng(int(mu.get("graine", 1)) + 7)
    fx = np.zeros((N, 2))
    sfx = th.get("effets", {})
    g_w, g_c, g_s, g_r = (10 ** (sfx.get(k_, d_) / 20) for k_, d_ in
                          (("whoosh_db", -20), ("coup_db", -16), ("scintillement_db", -24), ("montee_db", -22)))
    for q in plans:
        tr = q.get("transition", "coupe")
        if tr != "coupe":
            poser(fx, sfx_whoosh(rng), q["debut"] - 0.42, g_w)
        else:
            poser(fx, sfx_clic(rng), q["debut"], g_w * 0.8, 0.5)
        if q.get("titre"):
            poser(fx, sfx_coup(rng), q["titre"]["t"] + 0.1, g_c)
        if q.get("or") or q.get("orne") in ("soleil", "eventail", "arcs") or (q.get("titre") or {}).get("or"):
            poser(fx, sfx_scintillement(rng), q["debut"] + 0.15, g_s, 0.6)
        if q.get("compteur"):
            poser(fx, sfx_clic(rng), q["compteur"]["t"], g_w, 0.4)
    if boucle:  # riser into the loop point; the hit lands on the first frame (and on the replay)
        poser(fx, sfx_monte(rng), D - 1.6, g_r)
        poser(fx, sfx_coup(rng), 0.0, g_c)
    # Ducking: the voice's envelope lowers the music.
    w = int(0.01 * SR)
    e = np.sqrt((piste[: N // w * w].reshape(-1, w) ** 2).mean(1))
    e = lisser_circulaire(np.minimum(1, e / (0.25 * e.max() + 1e-9)), 0.03, 0.35)
    duck_db = float(mu.get("baisse_db", 9))
    g = 10 ** (-duck_db * e / 20)
    g = np.repeat(g, w)
    g = np.pad(g, (0, N - len(g)), mode="edge")
    voix_n = piste * (10 ** ((-16 - sonie(piste)) / 20))
    zik_n = zik * (10 ** ((-16 + float(mu.get("volume_db", -15)) - sonie(zik)) / 20))
    mix = voix_n[:, None] * np.array([1.0, 1.0]) + zik_n * g[:, None] + fx
    cible = float(th.get("sonie", -14))
    mix *= 10 ** ((cible - sonie(mix)) / 20)
    for _ in range(3):
        mix = limiteur_circulaire(mix, -1.3)
        mix *= 10 ** ((cible - sonie(mix)) / 20)
    lufs, tp = sonie(mix), crete_vraie(mix)
    if tp > -1.0:
        mix *= 10 ** ((-1.05 - tp) / 20)
        lufs, tp = sonie(mix), crete_vraie(mix)
    ecrire_wav(stage / "bande.wav", mix)
    rapport_son = {"lufs": round(lufs, 2), "true_peak_dbtp": round(tp, 2), "voix_facteur": round(facteur, 4),
                   "parole_s": round(parole, 2), "pauses_s": [round(x, 2) for x in ajouts], "bpm": bpm,
                   "joint_echantillons": "voice cut at the spoken join" if boucle else None}
    print(json.dumps(rapport_son, ensure_ascii=False))

    # 5. Props for the composition: brand values from the shop profile, theme colours from the job.
    profil = json.loads((ROOT / th["profil"]).read_text(encoding="utf-8")) if th.get("profil") else {}
    if profil.get("logo"):
        (stage / "logo.png").write_bytes((ROOT / profil["logo"]).read_bytes())
    timeline = {"duree": D, "fps": fps, "battue": battue, "boucle": boucle, "plans": plans, "sous_titres": st,
                "marque": th.get("marque", {}), "da": th.get("da", {})}
    props = dict(job.get("props", {}))
    props.update({"timeline": json.dumps(timeline, ensure_ascii=False, separators=(",", ":")),
                  "bande": "assets/job/bande.wav"})
    for k_, v_ in {**profil.get("palette", {}), **(th.get("palette") or {})}.items():
        props[k_] = v_
    (OUT / "props.json").write_text(json.dumps(props, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "theme.json").write_text(json.dumps({"son": rapport_son, "timeline": timeline}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(plans)} shots, {len(st)} caption pages, voice x{facteur:.3f}, {lufs:.2f} LUFS, {tp:.2f} dBTP")


if __name__ == "__main__":
    main()
