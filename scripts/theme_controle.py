#!/usr/bin/env python3
"""Gates of a theme video, run by render.yml after the render (jobs with "theme").

    python scripts/theme_controle.py          reads out/job.json and out/<name>.mp4

Checks, each with its measure in out/<name>-controle.json:
- length: theme.duree to one frame, frame count, constant frame pacing (no irregular timestamps);
- smoothness: no duplicated-frame stutter (a near-zero step between frames followed by a double step
  while the picture moves);
- loop: the step from the last frame to the first is no bigger than the steps around it (picture
  outside the caption band), and the audio has no jump at the join;
- sound: integrated loudness theme.sonie +/- 1 LU, true peak <= -1 dBTP (FFmpeg ebur128);
- words: Whisper (faster-whisper small) hears the script (word error rate on spoken words).
Writes out/<name>-raccord.mp4, the last 3 s followed by the first 3 s, to watch the join.
Any failed gate exits 1 with a "FAILED:" line.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
sys.path.insert(0, str(ROOT / "voix"))
from alignement import parle  # noqa: E402


def run(args, **kw):
    return subprocess.run(args, capture_output=True, check=True, **kw)


def images_grises(mp4, w=96, h=170):
    p = run(["ffmpeg", "-v", "error", "-i", str(mp4), "-vf", f"scale={w}:{h}:flags=area,format=gray", "-f", "rawvideo", "-"])
    return np.frombuffer(p.stdout, dtype=np.uint8).reshape(-1, h, w).astype(np.float32)


def wer(ref, hyp):
    r, h = ref.split(), hyp.split()
    d = list(range(len(h) + 1))
    for i in range(1, len(r) + 1):
        prev, d[0] = d[0], i
        for j in range(1, len(h) + 1):
            cur = d[j]
            d[j] = min(d[j] + 1, d[j - 1] + 1, prev + (r[i - 1] != h[j - 1]))
            prev = cur
    return d[len(h)] / max(1, len(r))


def main():
    job = json.loads((OUT / "job.json").read_text(encoding="utf-8"))
    th = job["theme"]
    D = float(th.get("duree", 60))
    fps = int(job.get("expect", {}).get("fps", 30))
    mp4 = OUT / job["output"]
    nom = job["output"][:-4]
    res, echecs = {}, []

    # Length and pacing
    pts = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "packet=pts_time", "-of", "csv=p=0", str(mp4)]).stdout.decode().split()
    pts = sorted(float(x) for x in pts if x.strip())
    pas = np.diff(pts)
    irreguliers = int(np.sum(np.abs(pas - 1 / fps) > 0.002))
    duree = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4)]).stdout)
    res["duree_s"], res["images"], res["pas_irreguliers"] = round(duree, 4), len(pts), irreguliers
    if abs(len(pts) - D * fps) > 1:
        echecs.append(f"{len(pts)} frames, expected {int(D * fps)} (+/- 1)")
    if irreguliers:
        echecs.append(f"{irreguliers} irregular frame timestamps")

    # Smoothness: duplicated frames while the picture moves
    g = images_grises(mp4)
    hors_st = np.ones(g.shape[1:], bool)
    hors_st[int(g.shape[1] * 1290 / 1920): int(g.shape[1] * 1500 / 1920), :] = False  # caption band
    d = np.abs(np.diff(g, axis=0))[:, hors_st].mean(1)
    # A duplicated frame inside a move: the picture moves before and after, one step is near zero
    # (identical frames: < 0.1 on this scale; a move that eases out then restarts stays above 0.2)
    # and the next is about double. (A cut, a flash or a move that starts after a still is not one.)
    saccades = []
    for i in range(3, len(d) - 4):
        avant, apres = np.median(d[i - 3:i]), np.median(d[i + 2:i + 5])
        if min(avant, apres) > 0.6 and d[i] < min(0.1, 0.25 * min(avant, apres)) and 1.4 * avant < d[i + 1] < 3.2 * max(avant, apres):
            saccades.append(round(i / fps, 2))
    res["saccades"] = saccades
    # Longest stretch where the picture (captions left out) does not move at all.
    fige = (d < 0.05).astype(int)
    plus_long, cour = 0, 0
    for x in fige:
        cour = cour + 1 if x else 0
        plus_long = max(plus_long, cour)
    res["plus_long_fige_s"] = round(plus_long / fps, 2)
    if plus_long / fps > 2.5:
        echecs.append(f"the picture is still for {plus_long / fps:.1f} s")
    res["pas_image_median"] = round(float(np.median(d)), 3)
    if saccades:
        echecs.append(f"duplicated-frame stutter at {saccades[:10]} s")

    # Loop join, picture
    if th.get("boucle"):
        joint = float(np.abs(g[-1] - g[0])[hors_st].mean())
        autour = float(np.median(np.r_[d[-6:], d[:6]]))
        res["boucle_image"] = {"saut": round(joint, 3), "pas_autour": round(autour, 3)}
        if joint > max(3 * autour, autour + 3.0):
            echecs.append(f"visible jump at the loop join: {joint:.2f} against {autour:.2f} around it")

    # Sound: loudness, true peak, join
    log = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(mp4), "-map", "0:a:0", "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True).stderr.decode()
    resume = log[log.rfind("Summary:"):]
    lufs = float(re.search(r"I:\s+(-?[\d.]+) LUFS", resume)[1])
    tp = float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", resume)[1])
    res["sonie_lufs"], res["crete_vraie_dbtp"] = lufs, tp
    cible = float(th.get("sonie", -14))
    if abs(lufs - cible) > 1.0:
        echecs.append(f"loudness {lufs} LUFS, expected {cible} +/- 1")
    if tp > -1.0:
        echecs.append(f"true peak {tp} dBTP, above -1")
    a = np.frombuffer(run(["ffmpeg", "-v", "error", "-i", str(mp4), "-map", "0:a:0", "-ac", "1", "-ar", "48000", "-f", "f32le", "-"]).stdout, dtype=np.float32)
    a = a[: int(D * 48000)]
    if th.get("boucle"):
        pas_a = np.abs(np.diff(a))
        saut_a = abs(float(a[-1]) - float(a[0]))
        res["boucle_son"] = {"saut": round(saut_a, 5), "p999": round(float(np.quantile(pas_a, 0.999)), 5),
                             "rms_fin_db": round(float(20 * np.log10(np.sqrt((a[-2400:] ** 2).mean()) + 1e-9)), 1),
                             "rms_debut_db": round(float(20 * np.log10(np.sqrt((a[:2400] ** 2).mean()) + 1e-9)), 1)}
        if saut_a > max(0.02, float(np.quantile(pas_a, 0.999))):
            echecs.append(f"audio jump at the loop join ({saut_a:.4f})")

    # Words heard
    from faster_whisper import WhisperModel
    m = WhisperModel("small", device="cpu", compute_type="int8")
    a16 = a[::3].copy()
    segs, _ = m.transcribe(a16, language="fr", beam_size=5, temperature=0, condition_on_previous_text=False)
    entendu = " ".join(s.text.strip() for s in segs)
    ecran = " ".join(l["ecran"] for l in th["lignes"])
    taux = wer(" ".join(parle(ecran)), " ".join(parle(entendu)))
    res["whisper"] = {"wer": round(taux, 4), "entendu": entendu}
    if taux > 0.15:
        echecs.append(f"Whisper hears {taux:.0%} of the words wrong")

    # Join clip: last 3 s then first 3 s
    raccord = OUT / f"{nom}-raccord.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-sseof", "-3", "-i", str(mp4), "-t", "3", "-i", str(mp4),
         "-filter_complex", "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]", "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-crf", "16", "-c:a", "aac", "-b:a", "192k", str(raccord)])
    res["echecs"] = echecs
    (OUT / f"{nom}-controle.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    print(json.dumps({k: v for k, v in res.items() if k != "whisper"}, ensure_ascii=False))
    print("whisper:", res["whisper"])
    if echecs:
        msg = "; ".join(echecs)
        print(f"FAILED: {msg}")
        print(f"::error title=theme gates failed::{msg}")
        sys.exit(1)


if __name__ == "__main__":
    main()
