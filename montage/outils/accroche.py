"""The hook, measured in the controle run, before any render.

    python montage/outils/accroche.py temps PROJECT          prints the --at times of the stills
    python montage/outils/accroche.py mesure PROJECT DIR OUT reads DIR/*.png (the engine names them frame-NN-at-<t>s.png)

The render refuses a film whose first 2 s hold no hook (rapport.py); on the fourth test that gate was
met at render only, and renders were refused (about 20 minutes and three renders). Here the same
measure runs on stills, in one `hyperframes snapshot --at … --no-end` (the engine has no range render):
every frame of the first 2 s, and 8 pairs of consecutive frames spread over the rest of the film for
its floor (the change of a frame where only grain moves). OUT/accroche.json says pass or fail with the
render's own numbers (rapport.accroche); a fail is printed as an error line, the run itself goes on (a
controle shows everything, it stops nothing). First proof, essai-orvane-4 (2026-11-14): 6 strong frames
and 31.5 here, 5 and 34.3 on the render of the same commit; both pass.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

from rapport import HAUT, accroche, changes

PAIRES = 8


def duree(projet):
    racine = re.search(r'<[^>]*id="root"[^>]*>', (projet / "index.html").read_text(encoding="utf-8"), re.S)
    return float(re.search(r'data-duration="([\d.]+)"', racine[0])[1])


def temps(projet, ips=30):
    """Every frame of the first 2 s, then 8 pairs of consecutive frames for the floor."""
    debuts = np.linspace(2.2, max(2.3, duree(projet) - 0.3), PAIRES)
    accroche_t = [i / ips for i in range(2 * ips)]
    paires = [x for t in debuts for x in (round(t * ips) / ips, (round(t * ips) + 1) / ips)]
    return [round(x, 3) for x in accroche_t + paires]


def images(fichiers):
    """Stills as grey pictures HAUT px high, the same copy as the render's measure."""
    out = []
    for f in fichiers:
        p = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(f), "-vf", f"scale=-2:{HAUT},format=gray",
                            "-f", "rawvideo", "-"], capture_output=True)
        out.append(np.frombuffer(p.stdout, np.uint8).reshape(HAUT, -1).astype(np.float32))
    return np.stack(out) if out else np.zeros((0, HAUT, 1), np.float32)


def mesure(projet, dossier, sortie):
    manifeste = json.loads((projet / "montage.json").read_text(encoding="utf-8"))
    attendu = manifeste.get("attendu", {})
    vus = sorted((float(m[1]), f) for f in dossier.glob("*.png") if (m := re.search(r"at-([\d.]+)s", f.name)))
    fin = attendu.get("accroche_s", 2.0) - 1e-3
    noms_d = [f for t, f in vus if t < fin]
    noms_p = [f for t, f in vus if t >= 2.2]
    debut, paires = images(noms_d), images(noms_p)
    r = {"images_debut": len(noms_d), "images_plancher": len(noms_p), "premiers_fichiers": [p.name for p in noms_d[:3]]}
    if len(noms_d) < 30 or len(noms_p) < 2:
        r["erreur"] = "too few stills: the snapshot commands wrote less than expected (controle.log)"
        print(f"::warning::early hook not measured: {r['erreur']}")
    else:
        m, _ = changes(debut)
        plancher = float(np.median([np.abs(paires[i + 1] - paires[i]).mean() for i in range(0, len(paires) - 1, 2)]))
        mesures, faute = accroche(list(m), plancher, attendu)
        r.update(mesures, passe=faute is None, par_image=[round(float(x), 2) for x in m])
        if faute:
            print(f"::error::FAILED (early measure, the render will refuse it): {faute}")
    sortie.mkdir(parents=True, exist_ok=True)
    (sortie / "accroche.json").write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: r.get(k) for k in ("images_fortes", "energie", "plancher", "passe", "erreur")}, ensure_ascii=False))


if __name__ == "__main__":
    if sys.argv[1] == "temps":
        print(",".join(str(t) for t in temps(Path(sys.argv[2]))))
    else:
        mesure(Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]))
