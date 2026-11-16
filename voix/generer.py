"""Generate the test narration with one TTS engine, one process per engine.

    python voix/generer.py ENGINE OUT_DIR [--voix V ...] [--prises lettres chiffres]
    python voix/generer.py ENGINE OUT_DIR --voix V --narration TEXT.txt [--graines 0 1]

The second form reads a theme video's narration (voix/narration.py) once per seed:
OUT_DIR/<engine>__<voice>__narration-g<seed>.wav.

Writes OUT_DIR/<engine>__<voice>__<take>.wav (16-bit mono) and appends one JSON line
per sample to OUT_DIR/generation.jsonl: duration, synthesis time, real-time factor,
model load time, peak RAM of the process, machine. Same script on the PC and on
GitHub Actions; engines are imported lazily so each one needs only its own packages.
"""
import argparse
import json
import os
import platform
import re
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from textes import PRISES, phrases  # noqa: E402

CACHE = Path(os.environ.get("VOIX_CACHE", Path.home() / ".cache" / "voix"))


def ram_pic_mo():
    """Peak resident memory of this process, in MB."""
    try:
        import resource  # Linux / macOS
        return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)
    except ImportError:
        import psutil  # Windows
        return round(psutil.Process().memory_info().peak_wset / 2**20)


def telecharger(url, nom):
    """Download a model file once into the cache and return its path."""
    chemin = CACHE / nom
    if not chemin.exists():
        chemin.parent.mkdir(parents=True, exist_ok=True)
        tmp = chemin.with_suffix(chemin.suffix + ".part")
        urllib.request.urlretrieve(url, tmp)
        tmp.replace(chemin)
    return chemin


def torch_threads():
    import torch
    torch.set_num_threads(os.cpu_count() or 2)
    return torch


# ---------------------------------------------------------------- engines
# Each engine: VOIX (default voices), charger() loads the model, dire(text, voice)
# returns (float32 mono array, sample rate).

class Supertonic:
    VOIX = [f"M{i}" for i in range(1, 6)] + [f"F{i}" for i in range(1, 6)]

    def charger(self):
        from supertonic import TTS
        self.tts = TTS(model="supertonic-3")

    def dire(self, texte, voix):
        wav, _ = self.tts.synthesize(texte, voice_style=self.tts.get_voice_style(voice_name=voix), lang="fr")
        return np.asarray(wav, dtype=np.float32).squeeze(), self.tts.sample_rate


class Kokoro:
    VOIX = ["ff_siwis"]
    BASE = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"

    def charger(self):
        from kokoro_onnx import Kokoro as K
        self.k = K(str(telecharger(self.BASE + "kokoro-v1.0.onnx", "kokoro/kokoro-v1.0.onnx")),
                   str(telecharger(self.BASE + "voices-v1.0.bin", "kokoro/voices-v1.0.bin")))

    def dire(self, texte, voix):
        audio, sr = self.k.create(texte, voice=voix, speed=1.0, lang="fr-fr")
        return np.asarray(audio, dtype=np.float32), sr


class Piper:
    """Piper voices from rhasspy/piper-voices (multi-speaker voices: one entry per speaker)."""
    def __init__(self, nom, qualite):
        self.nom, self.qualite = nom, qualite

    @property
    def VOIX(self):
        ids = self.voice.config.speaker_id_map
        return sorted(ids, key=ids.get) if ids else [self.nom]

    def charger(self):
        from piper import PiperVoice
        base = (f"https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/"
                f"{self.nom}/{self.qualite}/fr_FR-{self.nom}-{self.qualite}.onnx")
        modele = telecharger(base, f"piper/fr_FR-{self.nom}-{self.qualite}.onnx")
        telecharger(base + ".json", f"piper/fr_FR-{self.nom}-{self.qualite}.onnx.json")
        self.voice = PiperVoice.load(str(modele))

    def dire(self, texte, voix):
        from piper import SynthesisConfig
        ids = self.voice.config.speaker_id_map
        cfg = SynthesisConfig(speaker_id=ids[voix] if ids else None)
        morceaux = [c.audio_float_array for c in self.voice.synthesize(texte, syn_config=cfg)]
        return np.concatenate(morceaux).astype(np.float32), self.voice.config.sample_rate


class CoquiCss10:
    """Coqui tts_models/fr/css10/vits, as converted to ONNX by sherpa-onnx."""
    VOIX = ["css10"]
    URL = "https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-coqui-fr-css10.tar.bz2"

    def charger(self):
        import tarfile
        import sherpa_onnx
        dossier = CACHE / "vits-coqui-fr-css10"
        if not (dossier / "model.onnx").exists():
            with tarfile.open(telecharger(self.URL, "vits-coqui-fr-css10.tar.bz2")) as t:
                t.extractall(CACHE, filter="data")
        cfg = sherpa_onnx.OfflineTtsConfig(
            model=sherpa_onnx.OfflineTtsModelConfig(
                vits=sherpa_onnx.OfflineTtsVitsModelConfig(
                    model=str(dossier / "model.onnx"), lexicon="", tokens=str(dossier / "tokens.txt")),
                num_threads=os.cpu_count() or 2, provider="cpu"),
            max_num_sentences=1)
        self.tts = sherpa_onnx.OfflineTts(cfg)

    def dire(self, texte, voix):
        audio = self.tts.generate(texte, sid=0, speed=1.0)
        return np.asarray(audio.samples, dtype=np.float32), audio.sample_rate


class Pocket:
    """Kyutai Pocket TTS, French 24-layer model, predefined voices only (no cloning).
    cosette (Expresso) and jean (EARS) are non-commercial; juergen, rafael and daan have
    no stated licence: all five are left out."""
    VOIX = ["estelle", "alba", "anna", "azelma", "charles", "eponine", "eve", "fantine", "george",
            "jane", "mary", "michael", "paul", "vera", "bill_boerst", "caro_davy", "peter_yearsley",
            "stuart_bell", "javert", "marius", "giovanni", "lola"]

    def charger(self):
        torch_threads()
        from pocket_tts import TTSModel
        self.m = TTSModel.load_model(language="french_24l")
        self.etats = {}

    def dire(self, texte, voix):
        if voix not in self.etats:
            self.etats[voix] = self.m.get_state_for_audio_prompt(voix)
        audio = self.m.generate_audio(self.etats[voix], texte)
        return audio.detach().cpu().numpy().astype(np.float32).squeeze(), self.m.sample_rate


class Melo:
    VOIX = ["FR"]

    def charger(self):
        torch_threads()
        from melo.api import TTS
        self.m = TTS(language="FR", device="cpu")

    def dire(self, texte, voix):
        audio = self.m.tts_to_file(texte, self.m.hps.data.spk2id[voix], None, speed=1.0, quiet=True)
        return np.asarray(audio, dtype=np.float32), self.m.hps.data.sampling_rate


class Parler:
    """Parler-TTS mini multilingual v1.1: named speakers or a voice described in text."""
    REPO = "parler-tts/parler-tts-mini-multilingual-v1.1"
    FIN = "speaks in a warm, calm and expressive voice at a moderate pace, with very clear audio and no background noise."
    DESCRIPTIONS = {
        "Daniel": f"Daniel {FIN}",
        "Christine": f"Christine {FIN}",
        "homme-decrit": f"A man with a warm, low-pitched voice {FIN}",
    }
    VOIX = list(DESCRIPTIONS)

    def charger(self):
        torch = torch_threads()
        from parler_tts import ParlerTTSForConditionalGeneration
        from transformers import AutoTokenizer
        self.torch = torch
        self.m = ParlerTTSForConditionalGeneration.from_pretrained(self.REPO).eval()
        self.tok = AutoTokenizer.from_pretrained(self.REPO)
        self.tok_desc = AutoTokenizer.from_pretrained(self.m.config.text_encoder._name_or_path)

    def dire(self, texte, voix):
        self.torch.manual_seed(0)
        d = self.tok_desc(self.DESCRIPTIONS[voix], return_tensors="pt")
        p = self.tok(texte, return_tensors="pt")
        with self.torch.inference_mode():
            out = self.m.generate(input_ids=d.input_ids, attention_mask=d.attention_mask,
                                  prompt_input_ids=p.input_ids, prompt_attention_mask=p.attention_mask)
        return out.cpu().numpy().astype(np.float32).squeeze(), self.m.config.sampling_rate


class Qwen3:
    """Qwen3-TTS: VoiceDesign (voice described in text) or CustomVoice (preset speakers)."""
    DESIGN = {
        "homme-decrit": "A French man in his thirties with a warm, deep, calm voice, speaking "
                        "standard French clearly at a relaxed pace, like a narrator of a refined "
                        "interior design documentary.",
        "femme-decrit": "A French woman in her thirties with a warm, soft, calm voice, speaking "
                        "standard French clearly at a relaxed pace, like a narrator of a refined "
                        "interior design documentary.",
    }

    def __init__(self, repo, mode):
        self.repo, self.mode = repo, mode
        self.VOIX = list(self.DESIGN) if mode == "design" else ["Ryan", "Aiden"]

    def charger(self):
        torch = torch_threads()
        from qwen_tts import Qwen3TTSModel
        self.torch = torch
        self.m = Qwen3TTSModel.from_pretrained(self.repo, device_map="cpu", dtype=torch.bfloat16)

    def dire(self, texte, voix):
        self.torch.manual_seed(getattr(self, "graine", 0))
        if self.mode == "design":
            wavs, sr = self.m.generate_voice_design(text=texte, language="French", instruct=self.DESIGN[voix])
        else:
            wavs, sr = self.m.generate_custom_voice(text=texte, language="French", speaker=voix)
        return np.asarray(wavs[0], dtype=np.float32).squeeze(), sr


class VoxCPM2:
    DESIGN = {
        "homme-decrit": "A French man in his thirties, warm deep calm voice, relaxed pace",
        "femme-decrit": "A French woman in her thirties, warm soft calm voice, relaxed pace",
    }
    VOIX = list(DESIGN)

    def charger(self):
        self.torch = torch_threads()
        from voxcpm import VoxCPM
        # Build the 2B model directly in bfloat16: built in float32 first, it needs ~9 GB and
        # the 7 GB runner is killed while loading.
        self.torch.set_default_dtype(self.torch.bfloat16)
        try:
            self.m = VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False)
        finally:
            self.torch.set_default_dtype(self.torch.float32)

    def dire(self, texte, voix):
        self.torch.manual_seed(0)
        wav = self.m.generate(text=f"({self.DESIGN[voix]}){texte}", cfg_value=2.0, inference_timesteps=10)
        return np.asarray(wav, dtype=np.float32).squeeze(), self.m.tts_model.sample_rate


class KyutaiTTS:
    """Kyutai TTS 1.6B en/fr with precomputed voices from kyutai/tts-voices (CC0 / CC BY 4.0 only)."""
    VOIX = ["unmute-prod-website/fabieng-enhanced-v2.wav", "voice-donations/Hugo_the_frenchie_enhanced.wav",
            "unmute-prod-website/developpeuse-3.wav"]

    def charger(self):
        torch = torch_threads()
        from moshi.models.loaders import CheckpointInfo
        from moshi.models.tts import DEFAULT_DSM_TTS_REPO, TTSModel
        self.torch = torch
        info = CheckpointInfo.from_hf_repo(DEFAULT_DSM_TTS_REPO)
        self.m = TTSModel.from_checkpoint_info(info, n_q=32, temp=0.6, device="cpu", dtype=torch.bfloat16)

    def dire(self, texte, voix):
        self.torch.manual_seed(0)
        entries = self.m.prepare_script([texte], padding_between=1)
        cond = self.m.make_condition_attributes([self.m.get_voice_path(voix)], cfg_coef=2.0)
        with self.torch.no_grad():
            result = self.m.generate([entries], [cond])
            with self.m.mimi.streaming(1):
                pcm = [self.m.mimi.decode(f[:, 1:, :]).float().cpu().numpy()[0, 0]
                       for f in result.frames[self.m.delay_steps:]]
        return np.clip(np.concatenate(pcm), -1, 1).astype(np.float32), self.m.mimi.sample_rate


class KyutaiCml(KyutaiTTS):
    """Kyutai TTS 1.6B with the 35 French CML-TTS voices of kyutai/tts-voices (CC BY 4.0)."""
    VOIX = [f"cml-tts/fr/{i}_enhanced.wav" for i in (
        "10087_11650_000028-0002 10177_10625_000134-0003 10179_11051_000005-0001 12080_11650_000047-0001 "
        "12205_11650_000004-0002 12977_10625_000037-0001 1406_1028_000009-0003 1591_1028_000108-0004 "
        "1770_1028_000036-0002 2114_1656_000053-0001 2154_2576_000020-0003 2216_1745_000007-0001 "
        "2223_1745_000009-0002 2465_1943_000152-0002 296_1028_000022-0001 3267_1902_000075-0001 "
        "4193_3103_000004-0001 4482_3103_000063-0001 4724_3731_000031-0001 4937_3731_000004-0001 "
        "5207_3078_000031-0002 5476_3103_000072-0001 577_394_000070-0001 5790_4893_000052-0001 "
        "579_2548_000015-0001 5830_4703_000037-0001 6318_7016_000027-0002 7142_2432_000124-0003 "
        "7400_2928_000100-0001 7591_6742_000149-0002 7601_7727_000062-0001 7762_8734_000048-0002 "
        "8128_7016_000047-0002 928_486_000075-0001 9834_9697_000150-0003").split()]


class Bark:
    """Suno Bark (MIT) with its French speaker presets; at most ~13 s per call, so sentence by sentence."""
    VOIX = [f"v2/fr_speaker_{i}" for i in range(10)]

    def charger(self):
        self.torch = torch_threads()
        from transformers import AutoProcessor, BarkModel
        self.proc = AutoProcessor.from_pretrained("suno/bark")
        self.m = BarkModel.from_pretrained("suno/bark").eval()

    def dire(self, texte, voix):
        sr = self.m.generation_config.sample_rate
        blanc = np.zeros(int(0.25 * sr), dtype=np.float32)
        morceaux = []
        for i, phrase in enumerate(phrases(texte)):
            self.torch.manual_seed(i)
            entree = self.proc(phrase, voice_preset=voix)
            with self.torch.inference_mode():
                morceaux += [self.m.generate(**entree).cpu().numpy().astype(np.float32).squeeze(), blanc]
        return np.concatenate(morceaux), sr


MOTEURS = {
    "supertonic": Supertonic,
    "kokoro": Kokoro,
    "piper-mls": lambda: Piper("mls", "medium"),
    "piper-tom": lambda: Piper("tom", "medium"),
    "coqui-css10": CoquiCss10,
    "pocket": Pocket,
    "melo": Melo,
    "parler": Parler,
    "qwen3-design": lambda: Qwen3("Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign", "design"),
    "qwen3-preset": lambda: Qwen3("Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice", "preset"),
    "voxcpm2": VoxCPM2,
    "kyutai": KyutaiTTS,
    "kyutai-cml": KyutaiCml,
    "bark": Bark,
}


def nom_fichier(moteur, voix, prise):
    return f"{moteur}__{re.sub(r'[^A-Za-z0-9_-]+', '-', voix)}__{prise}.wav"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("moteur", choices=MOTEURS)
    ap.add_argument("sortie", type=Path)
    ap.add_argument("--voix", nargs="*")
    ap.add_argument("--prises", nargs="*", default=list(PRISES))
    ap.add_argument("--narration", type=Path, help="text file read once per seed instead of the test takes")
    ap.add_argument("--graines", nargs="*", type=int, default=[0])
    a = ap.parse_args()
    if a.narration:
        recit = a.narration.read_text(encoding="utf-8").strip()
        prises = {f"narration-g{g}": (g, recit) for g in a.graines}
    else:
        prises = {p: (0, PRISES[p]) for p in a.prises}
    a.sortie.mkdir(parents=True, exist_ok=True)

    moteur = MOTEURS[a.moteur]()
    t0 = time.perf_counter()
    moteur.charger()
    chargement = time.perf_counter() - t0
    machine = "github" if os.environ.get("GITHUB_ACTIONS") else platform.node()
    journal = a.sortie / "generation.jsonl"
    erreurs = 0
    for voix in a.voix or moteur.VOIX:
        for prise, (graine, texte) in prises.items():
            fichier = nom_fichier(a.moteur, voix, prise)
            moteur.graine = graine
            t0 = time.perf_counter()
            try:
                audio, sr = moteur.dire(texte, voix)
            except Exception as e:  # one failing voice must not hide the others
                erreurs += 1
                print(f"ECHEC {fichier}: {type(e).__name__}: {e}", flush=True)
                continue
            synthese = time.perf_counter() - t0
            sf.write(a.sortie / fichier, np.clip(audio, -1, 1), sr, subtype="PCM_16")
            duree = len(audio) / sr
            ligne = {"fichier": fichier, "moteur": a.moteur, "voix": voix, "prise": prise, "sr": sr,
                     "duree_s": round(duree, 2), "synthese_s": round(synthese, 2),
                     "rtf": round(synthese / duree, 3) if duree else None,
                     "chargement_s": round(chargement, 1), "ram_pic_mo": ram_pic_mo(),
                     "machine": machine, "coeurs": os.cpu_count()}
            with journal.open("a", encoding="utf-8") as f:
                f.write(json.dumps(ligne, ensure_ascii=False) + "\n")
            print(json.dumps(ligne, ensure_ascii=False), flush=True)
    sys.exit(1 if erreurs and erreurs == len(a.voix or moteur.VOIX) * len(prises) else 0)


if __name__ == "__main__":
    main()
