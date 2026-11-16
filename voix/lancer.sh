#!/usr/bin/env bash
# One engine group on a GitHub runner: install it, generate the samples, measure them.
#   bash voix/lancer.sh GROUP      (output: sorties/GROUP/)
# Measuring runs in its own venv so engine pins (transformers, torch) never clash with it.
# Multi-speaker engines are screened: first take for every voice, measure, keep the best
# men and women (voix/choisir.py), second take for those only, other WAVs deleted.
# GROUP "engine+voice+voice" replays both takes of given voices of an engine of the
# groups below (same install), e.g. pocket+charles+peter_yearsley.
# GROUP "theme:jobs/<job>.json" reads a theme video's narration with the job's own voice and
# seeds (voix/narration.py), then times and checks every take (voix/aligner.py).
set -uo pipefail
G="$1"
OUT="sorties/${NOM:-$G}"
mkdir -p "$OUT"
CPU=https://download.pytorch.org/whl/cpu
M=/tmp/mesure/bin/python

pipi() { python -m pip install -q --extra-index-url "$CPU" soundfile "$@"; }

# Model caches in one place, outside the home folder.
sudo mkdir -p /mnt/voix && sudo chown "$USER" /mnt/voix
export HF_HOME=/mnt/voix/hf VOIX_CACHE=/mnt/voix/modeles TORCH_HOME=/mnt/voix/torch XDG_CACHE_HOME=/mnt/voix/cache
df -h / /mnt | tail -2

# Extra swap (leaving 10 GB of disk for packages and models) so a model whose loading
# briefly needs more than the runner's 7 GB of RAM is slowed down instead of killed.
# On ubuntu-24.04 runners /mnt is on the system disk (72 GB, about 14 GB free).
swap() {
  local libre=$(df --output=avail -BG /mnt | tail -1 | tr -dc 0-9)
  local taille=$(( libre - 10 > 12 ? 12 : libre - 10 ))
  if [ "$taille" -ge 2 ]; then
    sudo fallocate -l "${taille}G" /mnt/swap-voix && sudo chmod 600 /mnt/swap-voix && sudo mkswap -q /mnt/swap-voix && sudo swapon /mnt/swap-voix
  fi
  free -m | head -3; df -h / /mnt | tail -2
}

outils_mesure() {
  python -m venv /tmp/mesure
  $M -m pip install -q --extra-index-url "$CPU" torch torchaudio faster-whisper jiwer num2words \
    praat-parselmouth imageio-ffmpeg soundfile numpy
}

crible_tout() {  # engine, men kept, women kept
  gen "$1" --prises lettres
  $M voix/mesurer.py "$OUT"
  mapfile -t garde < <($M voix/choisir.py "$OUT" "$1" --hommes "$2" --femmes "$3")
  echo "kept for $1: ${garde[*]}"
  if [ "${#garde[@]}" -eq 0 ]; then echo "FAILED: screening of $1 kept no voice"; return 1; fi
  gen "$1" --prises chiffres --voix "${garde[@]}"
  for f in "$OUT/$1"__*__lettres.wav; do
    v=$(basename "$f" | sed -E "s/^$1__(.*)__lettres\.wav$/\1/")
    printf '%s\n' "${garde[@]}" | sed -E 's/[^A-Za-z0-9_-]+/-/g' | grep -qx -- "$v" || rm -f "$f"
  done
}

IFS=+ read -r -a REJOUE <<< "$G"
if [ "${#REJOUE[@]}" -gt 1 ]; then G="${REJOUE[0]}"; fi
gen() {
  if [ "${#REJOUE[@]}" -gt 1 ]; then
    [ "$1" = "$G" ] && timeout "${BUDGET:-150m}" python voix/generer.py "$1" "$OUT" --voix "${REJOUE[@]:1}"
    return
  fi
  timeout "${BUDGET:-150m}" python voix/generer.py "$1" "$OUT" "${@:2}"
}
crible() { if [ "${#REJOUE[@]}" -gt 1 ]; then gen "$1"; else crible_tout "$@"; fi; }

[[ "$G" == theme:* || "$G" == aligner:* ]] || outils_mesure
case "$G" in
  aligner:*)
    # Time and check a take already committed in the repo (theme.voix.fichier), without generating.
    JOB="${G#aligner:}"
    read -r FICHIER NOMWAV <<< "$(python voix/narration.py "$JOB" --prise)"
    cp "$FICHIER" "$OUT/$NOMWAV"
    python -m venv /tmp/aligne
    /tmp/aligne/bin/python -m pip install -q faster-whisper jiwer num2words imageio-ffmpeg soundfile numpy       phonemizer espeakng-loader
    /tmp/aligne/bin/python voix/aligner.py "$OUT" "$JOB"
    exit $?
    ;;
  theme:*)
    JOB="${G#theme:}"
    read -r MOTEUR VOIX_T GRAINES <<< "$(python voix/narration.py "$JOB" --reglage)"
    python voix/narration.py "$JOB" --texte > "$OUT/narration.txt"
    cat "$OUT/narration.txt"
    case "$MOTEUR" in
      qwen3-design | qwen3-preset) sudo apt-get install -y -qq sox > /dev/null; pipi torch torchaudio qwen-tts ;;
      *) echo "FAILED: theme voice engine $MOTEUR is not wired in voix/lancer.sh"; exit 2 ;;
    esac
    # shellcheck disable=SC2086
    timeout "${BUDGET:-150m}" python voix/generer.py "$MOTEUR" "$OUT" --voix "$VOIX_T"       --narration "$OUT/narration.txt" --graines $GRAINES || { echo "FAILED: narration of $JOB"; exit 1; }
    python -m venv /tmp/aligne
    /tmp/aligne/bin/python -m pip install -q faster-whisper jiwer num2words imageio-ffmpeg soundfile numpy       phonemizer espeakng-loader
    /tmp/aligne/bin/python voix/aligner.py "$OUT" "$JOB"
    exit $?
    ;;
  leger)
    pipi supertonic kokoro-onnx piper-tts sherpa-onnx
    for e in supertonic kokoro piper-tom coqui-css10; do gen "$e"; done
    ;;
  piper-mls)
    pipi piper-tts
    crible piper-mls 3 1
    ;;
  pocket)
    pipi torch pocket-tts
    crible pocket 3 2
    ;;
  melo)
    pipi torch torchaudio "git+https://github.com/myshell-ai/MeloTTS.git"
    python -m unidic download
    gen melo
    ;;
  parler)
    pipi torch parler-tts
    python -m pip install -q -U "protobuf>=5.26.1"  # transformers' tokenizer needs it; parler pins an older one
    gen parler
    ;;
  qwen3-design | qwen3-preset)
    sudo apt-get install -y -qq sox > /dev/null
    pipi torch torchaudio qwen-tts
    gen "$G"
    ;;
  voxcpm2)
    sudo apt-get install -y -qq ffmpeg > /dev/null
    swap
    pipi torch torchaudio voxcpm
    gen voxcpm2
    ;;
  kyutai | kyutai-cml)
    swap
    pipi "torch<2.10" moshi
    if [ "$G" = kyutai ]; then gen kyutai; else crible kyutai-cml 3 2; fi
    ;;
  bark)
    swap
    pipi torch "transformers>=4.45,<5" scipy
    crible bark 3 1
    ;;
  *) echo "unknown group $G"; exit 2 ;;
esac
$M voix/mesurer.py "$OUT"
mesure=$?
ls "$OUT"/*.wav > /dev/null 2>&1 || { echo "FAILED: no sample generated for $G"; exit 1; }
exit $mesure
