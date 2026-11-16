# atelier-video: instructions for Claude

Private render farm for motion-design videos. One GitHub Actions run renders one job with
**Remotion** or **HyperFrames** on a free Linux runner and returns the MP4 as an artifact.
Nothing runs on the owners' PCs. Everything below was executed for real on 2026-11-08.

## Layout

| Path | What |
|---|---|
| `jobs/*.json` | Saved render requests (one JSON per video). Inline jobs need no file. |
| `jobs/<shop>/` | A shop's own files that have no public URL (logo, music), referenced by its jobs. |
| `remotion/` | Remotion 4 project. Compositions are registered in `src/Root.tsx`. |
| `hyperframes/<name>/index.html` | One HyperFrames project per folder (`promo/` is the first). CLI pinned in `hyperframes/package.json`. |
| `library/` | Shop-neutral shared files (e.g. `library/audio/soft-pad.m4a`, an original synthesized pad). |
| Style teasers (2026-11-09) | Five 8 s product reels in five styles, same props shape per engine: HyperFrames `style-editorial`, `style-dynamique`, `style-magazine`; Remotion `StyleCinema`, `StyleStudio` (`remotion/src/styles/`). Jobs: `jobs/linoa-style-*.json`. |
| `scripts/detourer.py` | Cuts a product out of its photo for jobs with `cutouts` (BiRefNet lite, MIT; pinned model and packages). |
| `scripts/render.mjs` | `prepare` (validate job, stage assets), `render`, `check` (probe the MP4). |
| `scripts/render.test.mjs` | Runs first in every render (about 1 s): job validation, output checks, no job data in engine code, inventory up to date. |
| `scripts/inventaire.mjs` | Regenerates `docs/fonctionnalites.md` (everything both engines offer at the pinned versions). |
| `.github/workflows/render.yml` | The render workflow. `workflow_dispatch` only: it never runs by itself. |
| `hyperframes/theme-video/`, `scripts/theme.py`, `scripts/theme_controle.py` | Theme videos: 60 s narrated loops from one job file (see below), art direction in `docs/direction-artistique.md`. |
| `voix/`, `.github/workflows/voix.yml` | TTS lab (2026-11-08): free French voices read one test narration and are measured (Whisper WER and French-accent probability, UTMOS, pitch, LUFS). See below. |

## Job format

```json
{
  "note": "free text",
  "engine": "remotion | hyperframes",
  "composition": "Promo (Remotion composition id) | promo (folder under hyperframes/)",
  "output": "file-name.mp4",
  "assets": {"photo.jpg": "https://…", "music.m4a": "library/audio/soft-pad.m4a"},
  "cutouts": {"lamp.png": "photo.jpg"},
  "props": {"title": "…", "image": "assets/job/photo.jpg", "music": "assets/job/music.m4a"},
  "expect": {"width": 1080, "height": 1920, "fps": 30, "minSeconds": 4.9, "maxSeconds": 5.1, "audio": true}
}
```

- `assets`: each file is downloaded (https only) or copied (`library/` or `jobs/` only) to `assets/job/<name>` of the
  engine's static root before rendering (`remotion/public/assets/job/`, `hyperframes/<name>/assets/job/`).
  Props then use the same path `assets/job/<name>` for both engines. HyperFrames forbids network media, so
  always stage media this way.
- `cutouts` (optional): each listed PNG is the product cut out of a staged photo (transparent background),
  made on the runner before the render (BiRefNet general lite, about 20 s more; the model and its Python
  packages are cached). Props point to it like any staged file. The step fails if the mask is empty or
  covers almost the whole photo.
- `props`: Remotion input props, or HyperFrames variables (rendered with `--strict-variables`: an undeclared
  key fails the run). The `Promo` templates of both engines take the same keys: `eyebrow`, `title`,
  `subtitle`, `image`, `music`, `background`, `ink`, `accent` (+ `seconds` for Remotion only; HyperFrames
  duration is fixed in its HTML).
- `expect`: optional, but always set `width`/`height` for a reel. The check always fails on: missing file,
  no video stream, flat picture (blank or missing media), identical first and last frames (nothing moves);
  and on any `expect` mismatch, a missing or silent audio track when `audio: true`.
- Brand data (names, texts, colours, fonts, photos, music) lives in jobs only. The test suite fails if a
  string passed as a prop in `jobs/` appears in engine code.

## Theme videos (60 s narrated loop, one job file)

A theme video (art deco on 2026-11-09; art nouveau, scandinave, verre soufflé… next) is **one job
file** `jobs/<name>.json` with `"engine": "hyperframes"`, `"composition": "theme-video"` and a
`"theme"` key. Nothing about a shop or a theme is written in code: a new theme is a new job file
(plus its pictures in `jobs/<shop>/<theme>/`). Art direction shared by every theme video:
`docs/direction-artistique.md`. Shop brand values: `jobs/<shop>/profil.json` (logo, palette).

```json
"theme": {
  "titre": "…", "duree": 60, "boucle": true,
  "profil": "jobs/<shop>/profil.json",
  "palette": {"fond": "#0b0a09", "fond2": "#0e2a24", "or_clair": "#ecd39a"},
  "voix": {"moteur": "qwen3-design", "voix": "femme-decrit", "graines": [0, 1],
           "fichier": "jobs/<shop>/<theme>/A-voix.wav", "mots": "jobs/<shop>/<theme>/A-voix.json"},
  "noms": {"Ruhlmann": "Ruhlmann"},
  "musique": {"style": "stride-1925", "tempo": 128, "graine": 1925, "volume_db": -15, "baisse_db": 9},
  "sonie": -14,
  "da": {"capMin": 110, "capSecondaire": 62, "titreMax": 230},
  "lignes": [
    {"dit": "what the voice says (respelled for the TTS if needed, numbers in words)",
     "ecran": "what is printed (correct spelling, digits)",
     "accent": ["1-2 words of the line in gold in the captions"],
     "pause": false,
     "plans": [{"image": "a.jpg", "detoure": "a-d.png", "cadre": "arche|gradins|carre|plein|haut",
                "fenetre": {"l": 0, "t": 760, "w": 1080, "h": 580}, "taille": [1254, 1254],
                "foyer": [50, 50], "zoom": 1.0, "gris": false,
                "mouvement": "pousse|recul|glisse-g|glisse-d|monte", "fond": "noir|vert",
                "orne": "soleil|eventail|chevrons|gradins|arcs|lignes|points",
                "orne_opts": {"couleurs": ["#…"], "trace": "SVG path for points", "cy": 1100},
                "recap": ["a.jpg", "b.jpg"],
                "transition": "volet-or|iris|eventail|persienne|fouet|zoom|profondeur|eclat|coupe",
                "titre": {"kicker": "Name", "lignes": ["LINE 1", "LINE 2"], "or": [0], "sur": "word", "y": 300},
                "compteur": {"kicker": "Plus de", "valeur": 250000, "legende": "ampoules", "sur": "250", "y": 300}}]}
  ]
}
```

- **Lines**: line 0 is the hook. With `"boucle": true` the last line leads into it ("… et c'est
  pour ça que"): the TTS reads lines 1…n then line 0 in one take, so the join is one spoken
  sentence; `scripts/theme.py` cuts the take at that join and turns it around.
- **Shots**: the first shot of a line starts on the music beat just before its first word; a
  second shot starts on the word `sur`. A headline enters on its `sur` word. A key headline line
  (`or`) whose capitals would be under 110 px tall fails the page (`FAILED: headline line … split
  it`), caught in seconds by the `validate` run with the job's values before the render: with
  Josefin Sans 700 that is about 8 capitals per line at most (cap height 0.74 em).
- **Captions**: only ordinary spaces break a caption; write a no-break space in `ecran` where words
  must stay together ("250 000", "New York", "Edgar Brandt"). The voice's own pauses decide where
  lines are cut (`scripts/theme.py` finds the silences in the sound, not in Whisper's word edges,
  which can be 0.1-0.2 s late).
- **Assets**: list every picture and the two fonts (`affiche.ttf`, `texte.ttf`) in `assets`, every
  cut-out in `cutouts` (BiRefNet, made on the runner). The shop logo comes from the profile.

Steps (each from any device, through Composio as below):

1. **Voice**: dispatch `voix.yml` with `groupes: ["theme:jobs/<job>.json"]` (one entry per job, they
   run in parallel). Artifact `voix-theme-jobs-<job>.json`: one WAV per seed and its `.json`
   (Whisper medium words with times, word error rate, names heard by sound). Measured on
   2026-11-09: Qwen3-TTS 1.7B VoiceDesign runs at about 11 times real time on a runner (25 min
   for two 60 s takes), but at 68 times on another one that ran out of memory (6.5 GB peak): one
   seed per run is safer; a take's length varies a lot with the seed (43 s and 65 s for the same
   text). `aligner:jobs/<job>.json` times a take already committed (about 2 min). Pick the take whose spoken length is closest to 57-59 s with no name fault, copy its
   WAV and JSON to `jobs/<shop>/<theme>/` and set `theme.voix.fichier` and `theme.voix.mots`.
2. **Render**: dispatch `render.yml` with the job. The workflow runs `scripts/theme.py` (voice cut,
   pauses, speed within -8/+12 %, original stride music, sound effects, ducking, -14 LUFS, timeline)
   then HyperFrames, then `scripts/theme_controle.py`: exactly 60 s, frame pacing, duplicated-frame
   stutter, loop join (picture and sound), loudness and true peak, Whisper word error rate. The
   artifact adds `<output>-raccord.mp4` (last 3 s + first 3 s, to watch the join),
   `<output>-controle.json` and `theme.json` (timeline and sound report).
3. **Preview before rendering** (optional, saves minutes): run `node scripts/render.mjs prepare`
   and `python scripts/theme.py` locally (numpy, num2words, FFmpeg), serve `out/` and open the
   composition with the props injected as `window.__hyperframes.getVariables()` and the colour
   variables as CSS custom properties; seek `window.__timelines["theme-video"]` to check frames.

## Trigger, poll, download (Composio, any device)

Use the MCP tool `COMPOSIO_PROXY_EXECUTE` with `toolkit_slug: "github"` (account Master00564).

1. **Trigger** (returns the run id at once thanks to `return_run_details`):
   ```
   method: POST
   endpoint: /repos/Master00564/atelier-video/actions/workflows/render.yml/dispatches
   body: {"ref":"main","inputs":{"job":"jobs/test-remotion.json","request_id":"my-label"},"return_run_details":true}
   → 200 {"workflow_run_id": 42525056371, "html_url": "…/actions/runs/42525056371"}
   ```
   Inline job, no commit needed: `"inputs": {"job_json": "<the job as a JSON string>", "request_id": "…"}`
   (give exactly one of `job` and `job_json`).
2. **Poll** every 15–20 s: `GET /repos/Master00564/atelier-video/actions/runs/{run_id}` until
   `status == "completed"`; success only if `conclusion == "success"`. Step timings:
   `GET …/actions/runs/{run_id}/jobs`. Measured for a 5 s reel: about 1 minute end to end with warm
   caches (job 44–57 s, render 26–29 s), 65–82 s on a cold cache.
   **On failure**, the reason is one call away: take `jobs[0].id` from `…/runs/{run_id}/jobs`, then
   `GET /repos/Master00564/atelier-video/check-runs/{job_id}/annotations`: the `render.mjs` step writes
   its `FAILED:` message there (invalid job, download error, size or sound mismatch…).
3. **Find the artifact**: `GET …/actions/runs/{run_id}/artifacts` → `artifacts[0].id`, `.digest`
   (`sha256:…`), `.size_in_bytes`. The artifact is named after the job's output file.
4. **Get a download link**: `GET /repos/Master00564/atelier-video/actions/artifacts/{artifact_id}/zip`.
   Composio follows GitHub's redirect and answers `binary_data.url`: a signed link valid 1 hour, no login
   needed. Download it anywhere (`curl -o video.zip "<url>"`), check `sha256sum video.zip` equals the
   digest, unzip: `<output>.mp4` + `<output>.json` (the check report: size, duration, fps, loudness,
   setup and render seconds).

### Fewer calls: start and wait in the workbench

Polling through the MCP tool costs one call (and its headers) per poll. In `COMPOSIO_REMOTE_WORKBENCH`,
one cell starts the render and waits; it returns the artifact id and digest, or the failure reasons.
A cell lasts 180 s at most: if `wait` returns `None`, call `wait(run_id)` again in a new cell.

```python
import contextlib, io, time
REPO = '/repos/Master00564/atelier-video'

def gh(method, endpoint, body=None):
    with contextlib.redirect_stdout(io.StringIO()):  # the workbench prints first responses otherwise
        res, err = proxy_execute(method, REPO + endpoint, 'github', body=body)
    if err:
        raise RuntimeError(f'{method} {endpoint}: {err}')
    return res

def start(inputs):
    body = {'ref': 'main', 'inputs': inputs, 'return_run_details': True}
    return gh('POST', '/actions/workflows/render.yml/dispatches', body)['workflow_run_id']

def wait(run_id, budget=150):
    end = time.time() + budget
    while time.time() < end:
        run = gh('GET', f'/actions/runs/{run_id}')
        if run['status'] == 'completed':
            out = {'run_id': run_id, 'conclusion': run['conclusion']}
            if run['conclusion'] == 'success':
                a = gh('GET', f'/actions/runs/{run_id}/artifacts')['artifacts'][0]
                out.update(artifact_id=a['id'], digest=a['digest'], bytes=a['size_in_bytes'])
            else:
                job = gh('GET', f'/actions/runs/{run_id}/jobs')['jobs'][0]
                notes = gh('GET', f'/check-runs/{job["id"]}/annotations')
                out['errors'] = [n['message'] for n in notes if n['annotation_level'] == 'failure']
            return out
        time.sleep(15)
    return None

run_id = start({'job': 'jobs/test-remotion.json', 'request_id': 'my-label'})
print(wait(run_id))
```

The workbench's `proxy_execute` returns an empty object for the artifact zip (binary bodies are dropped,
tested): get the download link with the MCP tool, step 4 above.

## Use a file that only exists on a device

Upload it to Composio's temporary storage, then pass the returned link as an asset URL:
in the workbench `POST $BACKEND_URL/api/v3/tool_router/internal/presigned_url` with
`{"operation":"upload"}` → `upload_url` (PUT, 1 h) and `download_url`; on the device
`curl -X PUT --data-binary @file "<upload_url>"`; in the job `"assets": {"photo.jpg": "<download_url>"}`.
The render must start within the hour.

## Change the code

`gh` is not installed and no local git credential exists. What worked (2026-11-08): keep a local mirror
(`C:\Users\lyceen-bfc\.claude\maintenance\atelier-video\depot`, a git repo), commit there, `git archive
--format=zip HEAD`, upload the zip with the presigned route above, then in the workbench create blobs,
one tree, one commit and move `refs/heads/main` with the Git Data API (`/git/blobs`, `/git/trees`,
`/git/commits`, `PATCH /git/refs/heads/main`). The GitHub tree SHA must equal the local
`git rev-parse HEAD^{tree}`: that proves the files are byte-identical. The connection has the `workflow`
scope, so workflow files can be pushed this way.

Before pushing, run locally: `node --test scripts/*.test.mjs`; for a HyperFrames change also
`npx hyperframes lint` in its folder (needs `npm ci` in `hyperframes/`).

### Add a composition

- **Remotion**: add `remotion/src/<Name>.tsx`, register a `<Composition id="<Name>">` in `src/Root.tsx`
  with fixed width/height/fps and, if the duration depends on props, `calculateMetadata`. Load media with
  `staticFile('assets/job/…')` (or an https URL). Fonts: `@remotion/google-fonts/<Font>` or `@remotion/fonts`.
  Run `npx tsc --noEmit`. New Remotion packages: same exact version as `remotion` (`--save-exact`).
- **HyperFrames**: copy `hyperframes/promo/` to `hyperframes/<name>/`, declare every swappable value in
  `data-composition-variables` and bind it (`data-var-text`, `data-var-src`, `var(--id)`). Follow the
  contract: every timed element has `class="clip"`, `data-start`, `data-duration`; one paused GSAP timeline
  registered as `window.__timelines["<data-composition-id>"]`; no `Date.now()`, unseeded random or network
  fetch; every `<audio>` has an `id`. Bundled fonts resolve by name (Inter, Playfair Display, Poppins…,
  list in `docs/fonctionnalites.md`); any other font needs `@font-face` to a file in the project.
  Registry blocks: `npx hyperframes add <name>` in the project folder (the registry is pinned to the CLI's
  tag in `hyperframes.json`).

### Upgrade an engine

Change the exact version in `remotion/package.json` (all `@remotion/*` and `remotion` together) or
`hyperframes/package.json`, run `npm install --package-lock-only` there, then `node scripts/inventaire.mjs`
(the tests fail until `docs/fonctionnalites.md` matches the new versions), push, and render both test jobs.

## Limits and costs (free plan)

- Private repo Actions minutes: 2,000 per month for the account, shared with `smp-drop-elite`
  (~30 min/day). GitHub rounds each job up to the minute: a 5 s reel costs 1 minute warm, 2 cold
  (6 proof runs on 2026-11-08 = 9 minutes, read with `GET /users/Master00564/settings/billing/usage`).
  Render time measured: Remotion 3 s video → 24.6 s, 5 s → 28.5 s (about 20 s fixed + 2 s per video
  second); HyperFrames 5 s → 25.7–27.2 s. Theme video (60 s, 1 800 frames, motion blur, 19-22
  shots, 4-5 cut-outs): render 531-668 s, job 12-17 min (measured 2026-11-09, 8 runs).
  `timeout-minutes: 30` caps a stuck run.
- Artifacts are kept 3 days (`retention-days: 3`); artifact storage on the free plan is limited (500 MB),
  so download what you need and let them expire.
- Caches (npm, FFmpeg, each engine's Chrome and fonts) make later runs faster; they are evicted after
  7 days without use, the next run just rebuilds them.

## TTS lab (`voix/`)

`voix.yml` (`workflow_dispatch` only) takes `groupes`, a JSON list of engine groups
(`leger`, `piper-mls`, `pocket`, `melo`, `parler`, `qwen3-design`, `qwen3-preset`, `voxcpm2`, `kyutai`, `kyutai-cml`, `bark`; `theme:jobs/<job>.json` to read a theme narration, `aligner:jobs/<job>.json` to time a committed take): one job per
group, in parallel. `voix/lancer.sh GROUP` installs the group, runs `voix/generer.py` (one engine per
process: WAV + `generation.jsonl` with RTF and peak RAM), then `voix/mesurer.py` in its own venv
(`mesures.json`). Multi-speaker engines are screened (`voix/choisir.py`). Artifact `voix-<group>`:
WAVs, `mesures.json`, `journal.log`. `voix/bilan.py` (run locally) scores pronunciation by sound
(`voix/phonetique.py`, eSpeak NG phonemes), ranks the voices and writes one MP3 per voice at -16 LUFS. Text of the test: `voix/textes.py`. Same scripts run on a PC.

## Never

- Sign in to HeyGen, use `hyperframes cloud/publish/templates/auth/billing`, or any paid feature.
  Telemetry and update checks are off in the workflow (`HYPERFRAMES_NO_TELEMETRY=1`,
  `HYPERFRAMES_NO_UPDATE_CHECK=1`, `DO_NOT_TRACK=1`).
- Put a secret in the repo. The workflow needs none (`permissions: contents: read`).
- Hard-code a shop's name, texts, colours or media in `remotion/src`, `hyperframes/*/index.html` or `scripts/`.
