#!/usr/bin/env python3
"""Camera light-fitting app, first step of a model: the shop's lit catalogue photo of a fitting and its unlit twin
become two cut-outs with ONE outline, cropped to the fitting. scripts/essayage_3d.py then colours the
manufacturer's 3D file from them.

    python scripts/essayage_modele.py prepare LOT_DIR    -> out/cutouts.json (for scripts/detourer.py)
    python scripts/essayage_modele.py assemble LOT_DIR   -> out/essayage/<nom>-eteint.webp, <nom>-allume.webp

LOT_DIR holds demande.json and the files it names:
  {"modeles": [{"nom": "handle-of-the-product",
                "allume": "https://…/photo-1.webp" or "file.png",   the shop's catalogue photo, light on
                "eteint": "file.png" or "https://…",                the same photo with the light off (same framing)
                "pose": "plafond" | "mur",
                "taille_cm": 70, "cotes_cm": [70, 20, 80],          the product's size (optional; read by the 3D step)
                "source_3d": "https://…/file.zip"}]}                the manufacturer's 3D file (read by the 3D step)
The outline is the unlit photo's (its ground is even, so its edge is the cleaner one). Nothing is drawn or invented
here: a twin that does not show the photo's framing is refused. Fails (exit 1, line starting "FAILED:") on a
missing file or a twin that moved the fitting; the other models of the lot are still made.
"""
import io
import json
import os
import sys
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out" / "essayage"
WORK = ROOT / "out" / "essayage-travail"
LONG_SIDE = 1000      # px of the longer side of a cut-out: enough to read each part's colour
MATCH_MIN = 0.92      # intersection over union of the two outlines; an aligned twin measured 0.97 to 0.99
EDGES_MIN = 0.5       # edge correlation of the two photos that proves one framing when the outlines disagree
STATES = ("eteint", "allume")


def fail(reason: str) -> None:
    print(f"FAILED: {reason}")
    if os.environ.get("GITHUB_ACTIONS"):
        print(f"::error title=try-on model failed::{reason}")
    sys.exit(1)


def request_of(lot: Path) -> list[dict]:
    path = lot / "demande.json"
    if not path.is_file():
        fail("no demande.json in the lot")
    models = json.loads(path.read_text(encoding="utf-8")).get("modeles") or []
    if not models:
        fail("demande.json names no model")
    for m in models:
        name = str(m.get("nom", ""))
        if not name or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in name):
            fail(f"model name {name!r}: lower-case letters, digits and dashes only")
        if m.get("pose") not in ("plafond", "mur"):
            fail(f"{name}: pose must be plafond or mur")
        for state in STATES:
            if not m.get(state):
                fail(f"{name}: no {state} photo")
    return models


def photo_of(lot: Path, source: str) -> Image.Image:
    if source.startswith("https://"):
        req = urllib.request.Request(source, headers={"User-Agent": "essayage-modele"})
        with urllib.request.urlopen(req, timeout=60) as answer:
            return Image.open(io.BytesIO(answer.read())).convert("RGB")
    path = (lot / source).resolve()
    if lot.resolve() not in path.parents or not path.is_file():
        fail(f"photo {source} is not a file of the lot (or an https address)")
    return Image.open(path).convert("RGB")


def prepare(lot: Path) -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    pairs = []
    for m in request_of(lot):
        size = None
        for state in STATES:
            photo = photo_of(lot, m[state])
            size = size or photo.size
            if photo.size != size:  # the twin comes back at its maker's size: same framing, so a plain resize
                photo = photo.resize(size, Image.Resampling.LANCZOS)
            stem = WORK / f"{m['nom']}-{state}"
            photo.save(f"{stem}.png")
            pairs.append({"from": f"{stem}.png", "to": f"{stem}-coupe.png", "plate": f"{stem}-fond.png"})
    (ROOT / "out" / "cutouts.json").write_text(json.dumps(pairs), encoding="utf-8")
    print(f"{len(pairs)} photos to cut out")


def luminance(rgb: np.ndarray) -> np.ndarray:
    return (rgb * np.array([0.2126, 0.7152, 0.0722], np.float32)).sum(-1) / 255


def same_edges(one: np.ndarray, other: np.ndarray, inside: np.ndarray) -> float:
    """How well two photos of the same framing line up, 0 to 1: the correlation of their edges (strength of the
    change of brightness from pixel to pixel) on the fitting, read at 256 px. A twin that moved or resized the
    fitting scores low whatever its lighting."""
    step = max(1, max(inside.shape) // 256)
    mask = inside[::step, ::step]

    def edges(photo):
        light = luminance(photo[::step, ::step])
        gy, gx = np.gradient(light)
        return np.hypot(gx, gy) * mask

    a, b = edges(one), edges(other)
    return float((a * b).sum() / max(np.sqrt((a * a).sum() * (b * b).sum()), 1e-9))


def unmix(photo: np.ndarray, ground: np.ndarray, alpha: np.ndarray) -> np.ndarray:
    """The fitting's own colour on its edge pixels: photo = a * fitting + (1 - a) * ground."""
    a = np.clip(alpha, 0.12, 1)[..., None]
    return np.clip((photo - (1 - a) * ground) / a, 0, 255)


def assemble(lot: Path) -> None:
    """Every model of the request. One that fails (fail() has said why) does not stop the others; the run
    then ends in error."""
    OUT.mkdir(parents=True, exist_ok=True)
    failed = 0
    for m in request_of(lot):
        try:
            assemble_one(m)
        except SystemExit:
            failed += 1
    if failed:
        sys.exit(1)


def assemble_one(m: dict) -> None:
    name = m["nom"]
    cut, ground = {}, {}
    for state in STATES:
        stem = WORK / f"{name}-{state}"
        if not Path(f"{stem}-coupe.png").is_file():
            fail(f"{name}: the {state} photo was not cut out")
        cut[state] = np.asarray(Image.open(f"{stem}-coupe.png").convert("RGBA"), np.float32)
        ground[state] = np.asarray(Image.open(f"{stem}-fond.png").convert("RGB"), np.float32)
    off_in, on_in = cut["eteint"][..., 3] > 127, cut["allume"][..., 3] > 127
    match = float((off_in & on_in).sum()) / max(float((off_in | on_in).sum()), 1)
    if match < MATCH_MIN:
        # the lit photo's own cut-out can be the wrong one (a glowing white diffuser against a light ground is cut
        # away): before refusing the twin, compare the two photos themselves, edge against edge
        edges = same_edges(cut["eteint"][..., :3], cut["allume"][..., :3], off_in)
        if edges < EDGES_MIN:
            fail(f"{name}: the unlit twin does not match its photo (outlines overlap {match:.0%}, edges {edges:.2f}; "
                 f"{MATCH_MIN:.0%} or {EDGES_MIN} needed): make the twin again")
        print(f"NOTE {name}: outlines overlap {match:.0%} only, but the two photos line up (edges {edges:.2f}): kept", flush=True)
    alpha = cut["eteint"][..., 3] / 255
    alpha[alpha < 0.04] = 0
    ys, xs = np.nonzero(alpha > 0.04)
    pad = round(0.01 * max(alpha.shape))
    y0, y1 = max(int(ys.min()) - pad, 0), min(int(ys.max()) + 1 + pad, alpha.shape[0])
    x0, x1 = max(int(xs.min()) - pad, 0), min(int(xs.max()) + 1 + pad, alpha.shape[1])
    alpha = alpha[y0:y1, x0:x1]
    colour = {s: unmix(cut[s][y0:y1, x0:x1, :3], ground[s][y0:y1, x0:x1], alpha) for s in STATES}
    h, w = alpha.shape
    scale = min(LONG_SIDE / max(h, w), 1)
    size = (max(round(w * scale), 1), max(round(h * scale), 1))
    for state in STATES:
        rgba = np.dstack([colour[state], alpha * 255]).astype(np.uint8)
        Image.fromarray(rgba, "RGBA").resize(size, Image.Resampling.LANCZOS).save(
            OUT / f"{name}-{state}.webp", "WEBP", quality=86, alpha_quality=92, method=6)
    print(f"cut-outs {name}: {size[0]}x{size[1]}, outlines {match:.1%}", flush=True)


def main() -> None:
    if len(sys.argv) != 3 or sys.argv[1] not in ("prepare", "assemble"):
        sys.exit("usage: essayage_modele.py prepare|assemble LOT_DIR")
    (prepare if sys.argv[1] == "prepare" else assemble)(Path(sys.argv[2]))


if __name__ == "__main__":
    main()
