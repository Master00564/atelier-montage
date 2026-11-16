"""Bring a rendered film's sound to the delivery loudness: -14 LUFS integrated, true peak -1.5 dBTP or lower.

    python montage/outils/master.py FILM.mp4

Short-video practice is -14 LUFS (the networks turn louder films down and leave quieter ones quiet);
the fourth test went out at -16.1 and earshot's critique asked for +2.1 dB. One gain for the whole
track, so every balance the gates measured (voice over music, breaths, effects over the bed) is kept;
where that gain would push the true peak over the ceiling, a brick-wall limiter at 4 times the sample
rate (FFmpeg alimiter, no auto level) shaves the peaks. The file is written back in place: picture
copied, sound AAC 320 kb/s (the sharing copy re-encodes it at 192). Measured again after encoding: if
the codec's overshoot passes the ceiling, the limiter goes 0.3 dB lower (three tries).
Prints the measures before and after as JSON.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

CIBLE = -14.0        # LUFS integrated
PLAFOND = -1.5       # dBTP after encoding (rapport.py refuses over -1.0)


def mesure(f):
    log = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(f), "-map", "0:a:0", "-af", "ebur128=peak=true",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    fin = log[log.rfind("Summary:"):]
    return float(re.search(r"I:\s+(-?[\d.]+) LUFS", fin)[1]), float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", fin)[1])


def main():
    film = Path(sys.argv[1])
    lufs, crete = mesure(film)
    gain = CIBLE - lufs
    tmp = film.with_name(film.stem + "-master.mp4")
    limite, essais = PLAFOND - 0.3, []
    for _ in range(4):
        filtre = f"volume={gain:.2f}dB"
        if crete + gain > PLAFOND:
            filtre += f",aresample=192000,alimiter=limit={10 ** (limite / 20):.4f}:attack=1:release=60:level=false,aresample=48000"
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(film), "-map", "0:v:0", "-map", "0:a:0",
                        "-c:v", "copy", "-af", filtre, "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", str(tmp)], check=True)
        apres = mesure(tmp)
        essais.append({"filtre": filtre, "lufs": apres[0], "crete_dbtp": apres[1]})
        if apres[1] <= PLAFOND + 0.05:
            break
        limite -= 0.3
    tmp.replace(film)
    print(json.dumps({"avant": {"lufs": lufs, "crete_dbtp": crete}, "gain_db": round(gain, 2), "essais": essais}))


if __name__ == "__main__":
    main()
