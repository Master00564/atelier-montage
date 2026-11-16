#!/usr/bin/env python3
"""Cut a subject out of its photo (transparent PNG), and optionally fill the hole it leaves (the plate).

    python scripts/detourer.py MODEL.onnx

Reads out/cutouts.json, written by `node scripts/render.mjs prepare` (render jobs with "cutouts")
or `node montage/outils/assets.mjs` (montage projects with "detourages"):
  [{"from": photo, "to": png, "zone": [x0, y0, x1, y1] (optional), "plate": path (optional)}]
- zone: the box (photo pixels) that holds the subject. The model sees only that box, at its full
  input size, so a small subject in a wide room is cut finely and nothing outside the box is kept.
- plate: the same photo with the subject removed and the hole filled from its surroundings, so a
  cut-out can move over its own background (parallax, focus pulls). The hole is the mask grown by
  a few pixels; it is filled by pull-push (mask-weighted pyramid averaging): smooth, no streaks,
  numpy only.
For each cut-out, out/derives/<name>.jpg shows the photo, the cut-out over dark and light grounds
and the plate side by side, so the edges can be judged before the cut-out is trusted.
Model: BiRefNet general, lite (MIT licence, ZhengPeng7/BiRefNet; ONNX export published by
danielgatis/rembg, MIT). Same pre- and post-processing as rembg's BiRefNet session.
Fails (exit 1, line starting "FAILED:") when the mask is empty or covers almost the whole box.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import onnxruntime as ort
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
SIZE = 1024
MEAN = np.array([0.485, 0.456, 0.406], np.float32)
STD = np.array([0.229, 0.224, 0.225], np.float32)
GROW = 6  # hole margin for the plate (Gaussian radius on the mask, in photo pixels): no fringe left


def fail(reason: str) -> None:
    print(f"FAILED: {reason}")
    if os.environ.get("GITHUB_ACTIONS"):  # readable from the API, like render.mjs failures
        print(f"::error title=cutout failed::{reason}")
    sys.exit(1)


def mask_of(session: ort.InferenceSession, photo: Image.Image) -> Image.Image:
    x = np.asarray(photo.resize((SIZE, SIZE), Image.Resampling.LANCZOS), np.float32)
    x = ((x / max(float(x.max()), 1.0) - MEAN) / STD).transpose(2, 0, 1)[None]
    logits = session.run(None, {session.get_inputs()[0].name: x})[0][0, 0]
    pred = 1 / (1 + np.exp(-logits))
    pred = (pred - pred.min()) / max(float(pred.max() - pred.min()), 1e-6)
    return Image.fromarray((pred * 255).astype(np.uint8), "L").resize(photo.size, Image.Resampling.LANCZOS)


def pull_push(colour: np.ndarray, weight: np.ndarray) -> np.ndarray:
    """Fill where weight is 0 with the weighted average of the surroundings, coarse to fine."""
    h, w = weight.shape
    if min(h, w) <= 2:
        total = max(float(weight.sum()), 1e-6)
        return np.broadcast_to((colour * weight[..., None]).sum((0, 1)) / total, colour.shape).copy()
    ph, pw = h + h % 2, w + w % 2
    c = np.pad(colour * weight[..., None], ((0, ph - h), (0, pw - w), (0, 0)), mode="edge")
    k = np.pad(weight, ((0, ph - h), (0, pw - w)), mode="edge")
    k2 = k.reshape(ph // 2, 2, pw // 2, 2).sum((1, 3))
    c2 = c.reshape(ph // 2, 2, pw // 2, 2, 3).sum((1, 3)) / np.maximum(k2, 1e-6)[..., None]
    coarse = pull_push(c2, np.minimum(k2, 1.0))
    up = np.stack([np.asarray(Image.fromarray(coarse[..., i].astype(np.float32), "F")
                              .resize((pw, ph), Image.Resampling.BILINEAR))[:h, :w] for i in range(3)], -1)
    a = weight[..., None]
    return a * colour + (1 - a) * up


def plate_of(photo: Image.Image, mask: Image.Image) -> Image.Image:
    grown = np.asarray(mask.filter(ImageFilter.GaussianBlur(GROW)), np.float32) / 255
    hole = np.clip(np.maximum(grown * 4, np.asarray(mask, np.float32) / 255 * 4), 0, 1)
    filled = pull_push(np.asarray(photo, np.float32), 1 - hole)
    return Image.fromarray(np.clip(filled, 0, 255).astype(np.uint8), "RGB")


def preview(photo: Image.Image, cut: Image.Image, plate: Image.Image | None, out: Path) -> None:
    panels = [photo]
    for ground in ((30, 30, 30), (236, 236, 236)):
        g = Image.new("RGB", photo.size, ground)
        g.paste(cut, (0, 0), cut)
        panels.append(g)
    if plate is not None:
        panels.append(plate)
    w, h = photo.width // 2, photo.height // 2
    sheet = Image.new("RGB", (w * len(panels), h))
    for i, p in enumerate(panels):
        sheet.paste(p.resize((w, h), Image.Resampling.LANCZOS), (i * w, 0))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, quality=88)


def main() -> None:
    if len(sys.argv) not in (2, 3):
        sys.exit("usage: detourer.py MODEL.onnx [INDEX]")
    pairs = json.loads((ROOT / "out" / "cutouts.json").read_text(encoding="utf-8"))
    if len(sys.argv) == 2 and len(pairs) > 1:
        # One process per photo: two inferences in one process ran the 7 GB runner out of memory
        # (the runner was shut down during the second cut-out, twice on 2026-11-09).
        for i in range(len(pairs)):
            r = subprocess.run([sys.executable, __file__, sys.argv[1], str(i)])
            if r.returncode:
                sys.exit(r.returncode)
        return
    if len(sys.argv) == 3:
        pairs = [pairs[int(sys.argv[2])]]
    options = ort.SessionOptions()
    options.enable_cpu_mem_arena = False
    session = ort.InferenceSession(sys.argv[1], sess_options=options, providers=["CPUExecutionProvider"])
    for pair in pairs:
        photo = Image.open(pair["from"]).convert("RGB")
        zone = tuple(pair.get("zone") or (0, 0, photo.width, photo.height))
        if not (0 <= zone[0] < zone[2] <= photo.width and 0 <= zone[1] < zone[3] <= photo.height):
            fail(f"zone {list(zone)} is outside {Path(pair['from']).name} ({photo.width}x{photo.height})")
        part = mask_of(session, photo.crop(zone))
        cover = float((np.asarray(part) > 127).mean())
        if not 0.005 < cover < 0.95:
            fail(f"cut-out of {Path(pair['from']).name} covers {cover:.1%} of its box")
        mask = Image.new("L", photo.size, 0)
        mask.paste(part, zone[:2])
        cut = photo.copy()
        cut.putalpha(mask)
        cut.save(pair["to"], optimize=True)
        plate = None
        if pair.get("plate"):
            plate = plate_of(photo, mask)
            plate.save(pair["plate"], quality=92)  # quality is read by JPEG, ignored by PNG
        preview(photo, cut, plate, ROOT / "out" / "derives" / (Path(pair["to"]).stem + ".jpg"))
        print(f"cut-out {Path(pair['to']).name}: {cover:.1%} of its box, box {mask.getbbox()}"
              + (f", plate {Path(pair['plate']).name}" if plate else ""), flush=True)


if __name__ == "__main__":
    main()
