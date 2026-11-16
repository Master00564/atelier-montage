# Fonctionnalités des deux moteurs

> Généré par `node scripts/inventaire.mjs` le 2026-11-08. Ne pas modifier à la main : relancer le script après tout changement de version.
> Versions : Remotion 4.0.541 · HyperFrames 0.9.20

Sources lues pour ces versions exactes : dépôt Remotion au tag `v4.0.541` (liste des paquets) et npm (descriptions, exports) ; CLI HyperFrames installée (`--help` de chaque commande, `catalog --json`) et dépôt HyperFrames au tag `v0.9.20` (exemples, attributs `data-*` de 75 pages de doc).

## Sommaire

1. [Remotion : paquets](#remotion--paquets)
2. [Remotion : boîte à outils, fonction par fonction](#remotion--boîte-à-outils-fonction-par-fonction)
3. [HyperFrames : commandes](#hyperframes--commandes)
4. [HyperFrames : attributs, animation, effets](#hyperframes--attributs-animation-effets)
5. [HyperFrames : catalogue (blocs et composants)](#hyperframes--catalogue-blocs-et-composants)
6. [Choisir le moteur par plan](#choisir-le-moteur-par-plan)

## Remotion : paquets

69 paquets publiés en 4.0.541. Installés dans ce dépôt : ceux de `remotion/package.json` ; ajouter un paquet = `npm install --save-exact <nom>@4.0.541` dans `remotion/`.

| Paquet | Ce qu’il fait (npm) | Dans un reel 9:16 |
|---|---|---|
| `@remotion/animated-emoji` | Google Fonts Animated Emojis as Remotion components | Emojis animés Google en composants. |
| `@remotion/animation-utils` | Helpers for animating CSS properties | Interpoler des styles CSS et des transformations : animations plus courtes à écrire. |
| `@remotion/babel-loader` | Babel loader for Remotion | Chargeur Babel pour le bundler. |
| `@remotion/browser-bundler` | Compile virtual Remotion projects in the browser | Compiler un projet Remotion dans le navigateur. |
| `@remotion/bundler` | Bundle Remotion compositions using Webpack | Empaquetage Webpack (utilisé par la CLI). |
| `@remotion/captions` | Primitives for dealing with captions | Structures et découpage de sous-titres mot à mot : texte qui suit une voix off. |
| `@remotion/cli` | Control Remotion features using the `npx remotion` command | La commande `remotion render/studio/still`. Toujours (le workflow s’en sert). |
| `@remotion/cloudrun` | Render Remotion videos on Google Cloud Run | Rendu sur Google Cloud Run : payant, hors de notre usage. |
| `@remotion/codemods` | Codemods for Remotion projects | Migrations de code entre versions. |
| `@remotion/design` | Design system | Système de design de Remotion (interne à leurs outils). |
| `@remotion/effects` | Effects that can be applied to Remotion-based canvas components | Effets appliqués aux composants canvas : grain, déformation, look. |
| `@remotion/elevenlabs` | Work with the output of the ElevenLabs API | Exploiter une voix off ElevenLabs (horodatage) : service payant, hors de notre usage gratuit. |
| `@remotion/enable-scss` | Enable SCSS support in Remotion | Écrire le style en SCSS. |
| `@remotion/eslint-config` | Default configuration for Remotion templates (ESLint <= 8) | Règles ESLint (≤ 8). |
| `@remotion/eslint-config-flat` | Default configuration for Remotion templates (ESLint >= 9) | Règles ESLint (≥ 9). |
| `@remotion/eslint-plugin` | Rules for writing Remotion code | Règles ESLint propres à Remotion. |
| `@remotion/fonts` | Helpers for loading local fonts into Remotion | Charger un fichier de police local (police de marque fournie par la boutique). |
| `@remotion/gif` | Embed GIFs in a Remotion video | Insérer un GIF synchronisé à la vidéo. |
| `@remotion/google-fonts` | Use Google Fonts in Remotion | Charger une police Google par son nom, sans fichier : titres et textes. |
| `@remotion/gsap` | Use GSAP timelines in Remotion | Piloter une timeline GSAP image par image dans Remotion : réutiliser une animation écrite pour HyperFrames. |
| `@remotion/install-whisper-cpp` | Helpers for installing and using Whisper.cpp | Transcrire localement avec Whisper.cpp pour générer des sous-titres. |
| `@remotion/lambda` | Render Remotion videos on AWS Lambda | Rendu sur AWS Lambda : payant, hors de notre usage. |
| `@remotion/lambda-client` |  | Client Lambda : payant, hors de notre usage. |
| `@remotion/layout-utils` | Utilities for working with layouts | Mesurer et ajuster le texte (fitText, measureText) : un titre long tient toujours dans la largeur. |
| `@remotion/licensing` | Manage your Remotion.pro license | Gestion de licence Remotion.pro (gratuit jusqu’à 3 personnes). |
| `@remotion/light-leaks` | Light leak effects for Remotion | Fuites de lumière par-dessus l’image : passage chaleureux entre deux plans de luminaire. |
| `@remotion/lottie` | Include Lottie animations in Remotion | Jouer une animation Lottie (icônes animées, pictos) image par image. |
| `@remotion/mac-cursors` | macOS cursor components for Remotion | Curseurs macOS : démos d’écran, sans usage pour un luminaire. |
| `@remotion/maptiler` | MapTiler components for Remotion | Cartes MapTiler : sans usage pour une fiche produit. |
| `@remotion/media` | Experimental WebCodecs-based media tags | Audio et Video nouvelle génération (WebCodecs) : musique, clips produit. |
| `@remotion/media-parser` | A pure JavaScript library for parsing video files | Lire les métadonnées d’un fichier vidéo. |
| `@remotion/media-utils` | Utilities for working with media files | Lire durée, dimensions, forme d’onde audio : caler les plans sur la musique, visualiseur. |
| `@remotion/motion-blur` | Motion blur effect for Remotion | Flou de bougé (Trail, CameraMotionBlur) sur un mouvement rapide : whip, titre qui file. |
| `@remotion/noise` | Noise generation functions | Bruit déterministe (Perlin/simplex) : flottement naturel d’un objet, grain animé, particules. |
| `@remotion/openai-whisper` | Work with the output of the OpenAI Whisper API | Convertir une transcription Whisper (API OpenAI) en sous-titres Remotion. |
| `@remotion/paths` | Utilities for working with SVG paths | Tracer et animer des chemins SVG (evolvePath…) : dessiner un filet, une flèche, un contour de produit. |
| `@remotion/player` | React component for embedding a Remotion preview into your app | Lire une composition dans une page web (aperçu interactif), pas pour le rendu. |
| `@remotion/preload` | Preloads assets for use in Remotion | Précharger images, vidéos, polices avant leur apparition (aperçu fluide). |
| `@remotion/promo-pages` |  | Pages promotionnelles de Remotion (interne). |
| `@remotion/renderer` | Render Remotion videos using Node.js or Bun | Rendu depuis Node (utilisé par la CLI). |
| `@remotion/rive` | Embed Rive animations in a Remotion video | Jouer une animation Rive. |
| `@remotion/rough-notation` | Rough annotation primitives for Remotion | Annotations dessinées à la main (souligner, entourer) : mettre en valeur un détail. |
| `@remotion/rounded-text-box` | Create a TikTok-like multiline text box SVG path with rounded corners | Bloc de texte multiligne aux coins arrondis façon TikTok : sous-titres, bulles de prix. |
| `@remotion/sdk` | Experimental primitives for building Remotion authoring interfaces | Expérimental : construire un éditeur. |
| `@remotion/sfx` | Sound effect library | Bibliothèque de bruitages : un « whoosh » sur une transition, un « pop » sur un prix. |
| `@remotion/shapes` | Generate SVG shapes | Formes SVG prêtes (cercle, rectangle, triangle, étoile, polygone, pie) pour pastilles et badges. |
| `@remotion/skia` | Include React Native Skia components in a Remotion video | Dessin React Native Skia : effets graphiques avancés. |
| `@remotion/starburst` | Starburst ray effect for Remotion | Rayons en étoile : fond d’une carte de prix ou d’accroche, avec retenue. |
| `@remotion/streaming` | Utilities for streaming data between programs | Interne : échanges de données entre programmes. |
| `@remotion/studio` | APIs for interacting with the Remotion Studio | API du Studio (aperçu local). |
| `@remotion/studio-protocol` | Create Element payloads and request installation into Remotion Studio | Envoyer des éléments au Studio. |
| `@remotion/studio-server` | Run a Remotion Studio with a server backend | Serveur du Studio. |
| `@remotion/studio-shared` | Internal package for shared objects between the Studio backend and frontend | Interne au Studio. |
| `@remotion/svg-3d-engine` | 3D SVG extrusion effects | Extrusion 3D de formes SVG : logo ou chiffre en relief. |
| `@remotion/tailwind` | Enable TailwindCSS support in Remotion (TailwindCSS v3) | Écrire le style en Tailwind v3. |
| `@remotion/tailwind-v4` | Enable TailwindCSS support in Remotion (TailwindCSS v4) | Écrire le style en Tailwind v4. |
| `@remotion/three` | Include React Three Fiber components in a Remotion video | Scène 3D React Three Fiber : produit en 3D si on a un modèle. |
| `@remotion/timeline-utils` | Internal utilities for rendering Remotion timelines | Interne : rendu des timelines. |
| `@remotion/transitions` | Library for creating transitions in Remotion | Enchaîner deux plans (fondu, glissé, volet, zoom…) avec TransitionSeries. Entre chaque plan produit. |
| `@remotion/vercel` | Render Remotion videos on Vercel Sandbox | Rendu sur Vercel Sandbox : payant, hors de notre usage. |
| `@remotion/video-matting` | Separate a video into a base layer and transparent foreground in the browser | Détourer une vidéo (sujet sur fond transparent) dans le navigateur. |
| `@remotion/web-renderer` | Render videos in the browser | Rendu dans le navigateur, sans serveur. |
| `@remotion/webcodecs` | Media conversion in the browser | Conversion de médias dans le navigateur. |
| `@remotion/whisper-web` | Helpers for using Whisper.cpp in browser using WASM | Transcription Whisper dans le navigateur (WASM). |
| `@remotion/whisper-webgpu` | Transcribe audio in the browser using Whisper and WebGPU | Transcription Whisper dans le navigateur (WebGPU). |
| `@remotion/zod-types` | Zod types for Remotion | Schéma Zod des props : contrôles éditables dans le Studio. |
| `@remotion/zod-types-v3` | Zod 3.22.3 types for Remotion | Variante Zod 3.22.3 de zod-types. |
| `create-video` | Create a new Remotion project | Créer un projet depuis un modèle (`npx create-video`). |
| `remotion` | Make videos programmatically | Le cœur : compositions, Sequence/Series, interpolate, spring, Easing, Img, staticFile. Toujours. |

Binaires du moteur (installés seuls selon la machine) : `@remotion/compositor-darwin-arm64`, `@remotion/compositor-darwin-x64`, `@remotion/compositor-linux-arm64-gnu`, `@remotion/compositor-linux-arm64-musl`, `@remotion/compositor-linux-x64-gnu`, `@remotion/compositor-linux-x64-musl`, `@remotion/compositor-win32-x64-msvc`.

Modèles de projet du dépôt (non publiés comme paquets, servent à `npx create-video`) : `ai-video`, `audiogram`, `code-hike`, `electron`, `element-library`, `empty`, `helloworld`, `music-visualization`, `next-app-tailwind`, `overlay`, `prompt-to-motion-graphics`, `react-router`, `recorder`, `render-server`, `skia`, `stargazer`, `still`, `three`, `tiktok`, `vercel`, `vibe-code`.

## Remotion : boîte à outils, fonction par fonction

Noms exportés lus dans les types publiés de chaque paquet (sans les types seuls).

### `@remotion/transitions`

Sous-chemins importables (`@remotion/transitions/<nom>`) : `cube`, `fade`, `flip`, `iris`, `none`, `swap`, `wipe`, `slide`, `ripple`, `dissolve`, `push-cut`, `book-flip`, `crosswarp`, `film-burn`, `zoom-blur`, `blur-slide`, `clock-wipe`, `cross-zoom`, `dreamy-zoom`, `linear-blur`, `zoom-in-out`.

Exports : `blurSlide`, `crossZoom`, `dreamyZoom`, `filmBurn`, `linearBlur`, `linearTiming`, `makeHtmlInCanvasPresentation`, `pushCut`, `springTiming`, `TransitionSeries`, `useTransitionProgress`.

### `@remotion/motion-blur`

Exports : `CameraMotionBlur`, `CameraMotionBlurProps`, `HtmlInCanvasMotionBlur`, `HtmlInCanvasMotionBlurProps`, `Trail`, `TrailProps`.

### `@remotion/light-leaks`

Exports : `lightLeak`, `LightLeak`, `lightLeakEffectSchema`, `LightLeakInternals`.

### `@remotion/starburst`

Exports : `starburst`, `Starburst`, `starburstEffectSchema`, `StarburstInternals`.

### `@remotion/effects`

Sous-chemins importables (`@remotion/effects/<nom>`) : `hue`, `lut`, `blur`, `glow`, `skew`, `tear`, `tile`, `tint`, `wave`, `lines`, `noise`, `paper`, `rings`, `scale`, `shine`, `waves`, `burlap`, `curves`, `emboss`, `evolve`, `invert`, `levels`, `mirror`, `sphere`, `zigzag`, `duotone`, `fisheye`, `flannel`, `outline`, `pattern`, `shatter`, `speckle`, `contrast`, `cylinder`, `dot-grid`, `exposure`, `halftone`, `pixelate`, `vibrance`, `vignette`, `color-key`, `film-burn`, `grayscale`, `gridlines`, `iris-wipe`, `lens-blur`, `page-turn`, `rain-fall`, `scanlines`, `snow-fall`, `starburst`, `translate`, `zoom-blur`, `brightness`, `corner-pin`, `light-leak`, `saturation`, `shrinkwrap`, `bevel-alpha`, `drop-shadow`, `light-trail`, `radial-wipe`, `region-blur`, `white-noise`, `checkerboard`, `long-shadows`, `contour-lines`, `fractal-noise`, `roughen-edges`, `tv-signal-off`, `white-balance`, `pixel-dissolve`, `thermal-vision`, `linear-gradient`, `liquid-contours`, `venetian-blinds`, `color-correction`, `barrel-distortion`, `noise-displacement`, `shadows-highlights`, `turbulent-displace`, `chromatic-aberration`, `linear-gradient-tint`, `linear-progressive-blur`, `radial-progressive-blur`, `halftone-linear-gradient`, `linear-progressive-pixelate`, `radial-progressive-pixelate`.

Exports : `checkerboard`, `cornerPin`, `gridlines`, `lightLeak`, `lightLeakEffectSchema`, `linearGradient`, `linearGradientTint`, `pattern`, `rings`, `starburst`, `starburstEffectSchema`, `tile`, `zigzag`.

### `@remotion/noise`

Exports : `noise2D`, `noise3D`, `noise4D`.

### `@remotion/paths`

Exports : `AbsoluteInstruction`, `BoundingBox`, `centerPath`, `cutPath`, `evolvePath`, `extendViewBox`, `getBoundingBox`, `getInstructionIndexAtLength`, `getLength`, `getPointAtLength`, `getSubpaths`, `getTangentAtLength`, `Instruction`, `interpolatePath`, `interpolatePaths`, `normalizePath`, `parsePath`, `Part`, `PathInternals`, `ReducedInstruction`, `reduceInstructions`, `resetPath`, `reversePath`, `scalePath`, `serializeInstructions`, `translatePath`, `warpPath`, `WarpPathFn`.

### `@remotion/shapes`

Exports : `Arrow`, `ArrowProps`, `Callout`, `CalloutProps`, `Circle`, `CircleProps`, `Ellipse`, `EllipseProps`, `Heart`, `HeartProps`, `makeArrow`, `MakeArrowProps`, `makeCallout`, `MakeCalloutProps`, `makeCircle`, `MakeCircleProps`, `makeEllipse`, `MakeEllipseOptions`, `makeHeart`, `MakeHeartProps`, `makePie`, `MakePieProps`, `makePolygon`, `MakePolygonProps`, `makeRect`, `MakeRectOptions`, `makeSpark`, `MakeSparkProps`, `makeStar`, `MakeStarProps`, `makeTriangle`, `MakeTriangleProps`, `Pie`, `PieProps`, `Polygon`, `PolygonProps`, `Rect`, `RectProps`, `Spark`, `SparkProps`, `Star`, `StarProps`, `Triangle`, `TriangleProps`.

### `@remotion/rounded-text-box`

Exports : `createRoundedTextBox`.

### `@remotion/rough-notation`

Exports : `Box`, `Bracket`, `Circle`, `CrossedOff`, `Highlight`, `StrikeThrough`, `Underline`.

### `@remotion/layout-utils`

Exports : `Dimensions`, `fillTextBox`, `fitText`, `fitTextOnNLines`, `measureText`, `TextTransform`.

### `@remotion/animation-utils`

Exports : `interpolateStyles`, `makeTransform`, `matrix`, `matrix3d`, `perspective`, `rotate`, `rotate3d`, `rotateX`, `rotateY`, `rotateZ`, `scale`, `scale3d`, `scaleX`, `scaleY`, `scaleZ`, `skew`, `skewX`, `skewY`, `translate`, `translate3d`, `translateX`, `translateY`, `translateZ`.

### `@remotion/gsap`

Exports : `useGsapTimeline`.

### `@remotion/media`

Exports : `Audio`, `AudioForPreview`, `AudioProps`, `experimental_Audio`, `experimental_Video`, `FallbackHtml5AudioProps`, `FallbackOffthreadVideoProps`, `getTargetSampleRate`, `MaxCanvasSinkFrameSize`, `MediaErrorAction`, `Video`, `VideoObjectFit`, `VideoProps`.

### `@remotion/media-utils`

Exports : `audioBufferToDataUrl`, `createSmoothSvgPath`, `getAudioData`, `getAudioDuration`, `getAudioDurationInSeconds`, `getImageDimensions`, `getVideoMetadata`, `getWaveformPortion`, `useAudioData`, `UseAudioDataOptions`, `useWindowedAudioData`, `UseWindowedAudioDataOptions`, `UseWindowedAudioDataReturnValue`, `visualizeAudio`, `VisualizeAudioOptions`, `visualizeAudioWaveform`, `VisualizeAudioWaveformOptions`.

### `@remotion/sfx`

Exports : `animeWow`, `boneCrack`, `bruh`, `ding`, `dramaticBoomer`, `fah`, `illuminatiConfirmed`, `loadingLag`, `macQuack`, `minecraftHurt`, `mouseClick`, `nellyAhh`, `ohMyGodVine`, `omgHellNah`, `pageTurn`, `priceIsRightFail`, `recordScratch`, `romanceMeme`, `sanctuaryGuardianWhat`, `shutterModern`, `shutterOld`, `skedaddle`, `snapchatNotification`, `spongebobFail`, `triggered`, `uiSwitch`, `vineBoom`, `whip`, `whoosh`, `wilhelmScream`, `windowsXpError`, `yippee`.

### `@remotion/captions`

Exports : `Caption`, `CaptionsInternals`, `createTikTokStyleCaptions`, `CreateTikTokStyleCaptionsInput`, `CreateTikTokStyleCaptionsOutput`, `EnsureMaxCharactersPerLineInput`, `EnsureMaxCharactersPerLineOutput`, `parseSrt`, `ParseSrtInput`, `ParseSrtOutput`, `parseVtt`, `ParseVttInput`, `ParseVttOutput`, `serializeSrt`, `SerializeSrtInput`, `TikTokPage`, `TikTokToken`.

### `@remotion/lottie`

Exports : `getLottieMetadata`, `Lottie`.

### `@remotion/three`

Sous-chemins importables (`@remotion/three/<nom>`) : `webgpu`.

Exports : `ThreeCanvas`, `ThreeCanvasProps`, `useOffthreadVideoTexture`, `UseOffthreadVideoTextureOptions`, `useVideoTexture`, `UseVideoTextureOptions`.

### `@remotion/svg-3d-engine`

Exports : `aroundCenterPoint`, `extrudeAndTransformElement`, `extrudeElement`, `interpolateMatrix4d`, `makeMatrix3dTransform`, `MatrixTransform4D`, `reduceMatrices`, `rotateX`, `rotateY`, `rotateZ`, `scaled`, `scaleX`, `scaleY`, `threeDIntoSvgPath`, `transformPath`, `translateX`, `translateY`, `translateZ`, `Vector4D`.

### `@remotion/fonts`

Exports : `FontFormat`, `loadFont`, `LoadFontOptions`.

## HyperFrames : commandes

CLI `hyperframes` 0.9.20, lue par `--help`. Commandes à ne pas utiliser ici (payantes ou compte HeyGen) : `auth`, `billing`, `cloud`, `templates`, `publish`, `reverse` ; `lambda` et `cloudrun` facturent le cloud.

### Getting Started

- **`init`** : Scaffold a new composition project. Arguments : NAME (Project name). Options : `--example` `--template` `--video` `--video-legacy` `--audio` `--skip-transcribe` `--keep-original` `--model` `--language` `--non-interactive` `--agent` `--skip-skills` `--tailwind` `--resolution` `--skill`
- **`add`** : Install a block or component from the registry. Arguments : NAME (Registry item name or tag. Single items install directly (e.g. shader-wipe). If the name matches a tag instead, all blocks with that tag are installed (e.g. html-in-canvas, captions). Give several names to install each of them in one call. (Required)). Options : `--dir` `--clipboard` `--no-clipboard` `--json` `--vars` `--force`
- **`capture`** : Capture a website for video production. Arguments : URL (Website URL to capture (omit when using --local-file or --video)). Options : `--local-file` `--video` `--local-root` `--output` `--skip-assets` `--skip-vision` `--max-screenshots` `--timeout` `--capture-budget` `--json` `--index` `--video-url` `--list`
- **`catalog`** : Browse and install blocks and components. Arguments : WORDS (Search words, same as --query (e.g. `catalog crossfade`)). Options : `--query` `--type` `--tag` `--json` `--human-friendly` `--yes` `--on-device`
- **`preview`** : Start the studio for previewing compositions. Arguments : DIR (Project directory). Options : `--port` `--force-new` `--background` `--foreground` `--status` `--stop` `--list` `--kill-all` `--lint-verbose` `--open` `--no-open` `--selection` `--json` `--context` `--context-fields` `--context-detail` `--browser-path` `--user-data-dir` `--remote-debugging-port` `--browser-no-gpu` `--disable-gpu` `--browser-gpu` `--no-browser-gpu` `--proxy` `--no-proxy`
- **`present`** : Open a slideshow deck in presenter mode (with audience sync). Arguments : DIR (Project directory). Options : `--port` `--open` `--no-open` `--browser-path` `--user-data-dir` `--remote-debugging-port`
- **`publish`** : Upload a project to a stable URL (private by default). Arguments : DIR (Project directory). Options : `--yes` `--public` `--update` `--space` `--proxy` `--no-proxy` `--lint-verbose`
- **`render`** : Render a composition to MP4 or WebM. Arguments : DIR (Project directory). Options : `--composition` `--output` `--fps` `--quality` `--prores-profile` `--skill` `--format` `--gif-loop` `--hls-segment-seconds` `--video-frame-format` `--page-motion-blur` `--workers` `--docker` `--hdr` `--sdr` `--crf` `--video-bitrate` `--start` `--end` `--keyframe-interval` `--max-bitrate` `--buffer-size` `--vp9-cpu-used` `--gpu` `--browser-gpu` `--no-browser-gpu` `--quiet` `--lint-verbose` `--debug` `--best-effort` `--no-best-effort` `--wait` `--no-wait` `--strict` `--strict-all` `--max-concurrent-renders` `--variables` `--variables-file` `--strict-variables` `--batch` `--batch-concurrency` `--batch-fail-fast` `--json` `--resolution` `--page-side-compositing` `--experimental-fast-capture` `--no-page-side-compositing` `--browser-timeout` `--protocol-timeout` `--player-ready-timeout` `--resume` `--keep-segments` `--low-memory-mode` `--frames-cache-dir`
- **`open`** : Open a project in the HyperFrames desktop app. Arguments : DIR (Project directory (default: current)). Options : `--json`
- **`catch-up`** : See what was done in the desktop app since you last looked. Arguments : DIR (Project directory (default: current)). Options : `--json`

### Project

- **`lint`** : Validate a composition for common mistakes. Arguments : DIR (Project directory, or one composition .html file). Options : `--json` `--verbose` `--lint-verbose`
- **`check`** : Run lint, runtime validation, and layout inspection as one gate. Arguments : DIR (Project directory). Options : `--json` `--lint-verbose` `--samples` `--range` `--components` `--at` `--at-transitions` `--max-transition-samples` `--max-issues` `--collapse-static` `--no-collapse-static` `--tolerance` `--budget` `--timeout` `--contrast` `--no-contrast` `--strict` `--prepare-media` `--proxy` `--browser-gpu` `--no-browser-gpu` `--snapshots` `--caption-zone` `--frame-check` `--layout`
- **`validate`** : Runtime-validate a composition in headless Chrome (JS errors, missing assets, contrast). Arguments : DIR (Project directory). Options : `--json` `--timeout` `--contrast` `--no-contrast`
- **`beats`** : Detect beats in the music track and write beats/<audio>.json. Arguments : DIR (Project directory, or one audio or video file to analyse). Options : `--json`
- **`audio`** : Measure where sounds land: onsets, hits, loudness, silence, in film time. Arguments : FILES (Audio or video files to analyze). Options : `--dir` `--element` `--at` `--range` `--place-at` `--skip-file-seconds` `--only` `--quality` `--provider` `--onset-method` `--threshold` `--band` `--hop-ms` `--onset-ratio` `--tail-db` `--silence-db` `--full` `--read` `--transcript` `--layer` `--json`
- **`inspect`** : Inspect rendered visual layout across the timeline. Arguments : DIR (Project directory). Options : `--json` `--samples` `--at` `--at-transitions` `--max-transition-samples` `--tolerance` `--timeout` `--max-issues` `--collapse-static` `--no-collapse-static` `--strict`
- **`keyframes`** : Inspect keyframes and render onion-shot diagnostics. Arguments : TARGET (Project dir or composition .html). Options : `--selector` `--runtime` `--json` `--shot` `--samples` `--layout` `--from` `--to` `--angle` `--fit` `--no-fit` `--ghost`
- **`snapshot`** : Capture key frames as PNG screenshots for visual verification. Arguments : DIR (Project directory). Options : `--output` `--frames` `--at` `--range` `--composition` `--timeout` `--angle` `--end` `--no-end` `--keep` `--zoom` `--zoom-scale` `--against` `--review` `--json` `--describe` `--proxy` `--browser-gpu` `--no-browser-gpu`
- **`media-treatment`** : Discover, apply, or clear deterministic media treatments on media elements. Options : `--capabilities` `--capability` `--all` `--project` `--file` `--selector` `--selector-index` `--grading` `--apply` `--analyze` `--clear` `--dry-run` `--json`
- **`normalize-audio`** : Match one authored audio clip's loudness to another using integrated LUFS. Arguments : DIR (Project directory). Options : `--target` `--reference` `--lufs` `--write` `--tolerance` `--json`
- **`grade-compare`** : Render candidate color grades onto a reference frame as one labeled comparison PNG. Options : `--for` `--grades` `--luts` `--project` `--out` `--json` `--timeout` `--baseline` `--no-baseline`
- **`compare`** : Render composition variants into one labeled comparison sheet. Arguments : PATH (Composition project directory or .html file (pass 2+ paths)). Options : `--at` `--labels` `--out` `--cols` `--timeout` `--json`
- **`diff`** : Score a render or a project against the original video, frame by frame. Arguments : REFERENCE (The original video (Required)) ; YOURS (A rendered video, or a project folder (captured at the original's frame times, no render) (required)). Options : `--at` `--range` `--offset` `--segments` `--ledger` `--project` `--min-mean` `--min-p05` `--min-cell` `--worst` `--sbs` `--out` `--timeout` `--drawn` `--json`
- **`measure`** : Measure a video file: clock, cuts, events, frames, motion, crops, boxes, eases, look. Options : `--map`
  - `measure probe` : Size (as displayed), frame rate, duration, sound, and what to fix before measuring or rebuilding
  - `measure cuts` : Hard cuts from the frame-to-frame difference (scene scores miss some), and the shots between them; light flashes, whips and fast moves are listed apart as not_cuts
  - `measure events` : When things change on screen: cuts, flashes, appears, disappears, changes and holds; --map adds the sound and the windows worth looking at
  - `measure frames` : Frames of a video as pictures: chosen moments, an overview sheet, consecutive native frames of a range, or strips around every event
  - `measure extract` : Cut a still (--at) or a clip (--from/--to) out of a video, cropped to a region, as project media
  - `measure curve` : Each move of one element on a flat background: start, duration, overshoot and the closest GSAP ease
  - `measure energy` : How much two clips move, and whether they move at the same moments, when their pixels differ
  - `measure ink` : The bounds, size and lines of the text or marks drawn in a region of one frame, in the video's pixels
  - `measure look` : Brightness, contrast, saturation, black-and-white share and warmth of a window, or compared with another video
  - `measure face` : How big the face is and where, over a window: its box per sampled frame and whether a generated presenter can keep the likeness at that size
  - `measure sync` : Picture against sound for a person speaking: the lag between mouth motion and the voice
- **`reverse`** : Open a reverse-any-video run: note it with HeyGen, then probe the video
  - `reverse start` : Note a reverse run with HeyGen (signed in: saves its session in the project), then print the video's probe; stops only when HeyGen blocks a Free account
- **`billing`** : Open the HyperFrames plans or credits page and wait until it is done. Arguments : ACTION (subscribe | add-credits (Required)). Options : `--needed` `--tool` `--feature` `--session` `--skill` `--timeout`
- **`templates`** : Pull a style template into this project (HyperFrames Pro). Arguments : ACTION (pull (Required)) ; SLUG (The template's slug, from the style-sampling skill (Required)). Options : `--dir`
- **`info`** : Print project metadata. Arguments : DIR (Project directory). Options : `--json` `--media`
- **`compositions`** : List all compositions in a project. Arguments : DIR (Project directory). Options : `--json`
- **`timeline`** : Print the project's tracks and clips. Arguments : DIR (Project directory). Options : `--component` `--at` `--range` `--boundary` `--generation` `--offset` `--json`
  - `timeline move` : move a timeline clip
  - `timeline trim` : trim a timeline clip
  - `timeline split` : split a timeline clip
  - `timeline delete` : delete a timeline clip
  - `timeline set` : set a timeline clip
  - `timeline duplicate` : duplicate a timeline clip
  - `timeline ids` : Stamp stable ids on timeline clips
  - `timeline apply` : Apply an atomic timeline edit plan
  - `timeline undo` : Restore a timeline mutation receipt
- **`history`** : List, undo and restore the project's recorded changes. Options : `--dir` `--json` `--since` `--who` `--limit`
  - `history show` : One entry's files, before and after
  - `history undo` : Undo an entry (default: your newest one still in effect)
  - `history restore` : Make the files what they were right after an entry, a time, or 'start'
  - `history peek` : The files at an entry, a time, or 'start' (read-only); with a path, that file
  - `history pin` : Keep an entry (and what it needs) when old history is trimmed
  - `history begin` : Start a turn: your writes until `end` become one entry under your name
  - `history end` : End your turn and print its entry
- **`docs`** : View inline documentation in the terminal. Arguments : TOPIC (Topic: data-attributes, examples, rendering, gsap, troubleshooting, compositions, audio, transcribe, motion-blur. Omit to list all.)

### Tooling

- **`benchmark`** : Render with preset fps/quality/worker configs and compare speed and file size. Arguments : DIR (Project directory). Options : `--runs` `--json`
- **`browser`** : Manage the Chrome browser used for rendering. Arguments : SUBCOMMAND (ensure = find or download Chrome, path = print executable path, clear = remove cached download). Options : `--force`
- **`doctor`** : Check system dependencies and environment. Options : `--json`
- **`clean`** : Find and remove what HyperFrames left on disk. Arguments : DIR (Project directory (default: current); its subfolders are not searched). Options : `--dry-run` `--snapshots` `--json`
- **`upgrade`** : Check for updates and show upgrade instructions. Options : `--yes` `--check` `--json` `--project`
- **`update`** : Check the CLI and the skills for updates in one call, and install them. Options : `--check` `--yes` `--json`

### Deploy

- **`cloud`** : Render compositions on HeyGen's cloud (no local Chrome/ffmpeg)
  - `cloud render` : Render a HyperFrames composition in the cloud
  - `cloud list` : List recent cloud renders
  - `cloud get` : Fetch detail for one cloud render
  - `cloud delete` : Soft-delete a cloud render
- **`lambda`** : Deploy and drive distributed renders on AWS Lambda. Arguments : SUBCOMMAND (deploy | sites | render | progress | destroy | policies) ; TARGET (Subcommand-specific positional (project dir, render id, policies verb, etc.)) ; EXTRA (Extra positional (e.g. `sites create <projectDir>` or `policies validate <policy.json>`)). Options : `--stack-name` `--region` `--profile` `--concurrency` `--chrome-source` `--memory` `--video-arch` `--skip-build` `--warm` `--no-warm` `--site-id` `--width` `--height` `--output-resolution` `--fps` `--format` `--codec` `--quality` `--keyframe-interval` `--max-bitrate` `--buffer-size` `--prores-profile` `--chunk-size` `--max-parallel-chunks` `--target-chunk-frames` `--execution-name` `--output-key` `--variables` `--variables-file` `--strict-variables` `--batch` `--max-concurrent` `--dry-run` `--wait` `--wait-interval-ms` `--json`
- **`cloudrun`** : Deploy and drive distributed renders on Google Cloud Run. Arguments : SUBCOMMAND (deploy | sites | render | render-batch | progress | destroy) ; TARGET (Subcommand positional (project dir, execution name, sites verb)) ; EXTRA (Extra positional (e.g. `sites create <projectDir>`)). Options : `--project` `--region` `--image` `--repo` `--cpu` `--memory` `--max-instances` `--timeout` `--site-id` `--width` `--height` `--fps` `--format` `--codec` `--quality` `--chunk-size` `--max-parallel-chunks` `--target-chunk-frames` `--output-resolution` `--variables` `--variables-file` `--strict-variables` `--batch` `--max-concurrent` `--dry-run` `--render-id` `--output-key` `--wait` `--wait-interval-ms` `--json`

### AI & Integrations

- **`skills`** : Install HyperFrames and GSAP skills for AI coding tools
  - `skills check` : Check whether installed skills are the latest version
  - `skills update` : Update the core set plus every installed HyperFrames skill to the latest. Pass skill names to also install those (how on-demand skills install) — without names it never expands a partial install, and it never removes a skill
- **`transcribe`** : Transcribe audio/video to word-level timestamps, or import an existing transcript. Arguments : INPUT (Audio/video file to transcribe, or transcript file to import (.json, .srt, .vtt) (Required)). Options : `--dir` `--engine` `--language` `--speakers` `--model` `--json` `--to` `--output` `--preserve-cues` `--runtime-install` `--no-runtime-install` `--optional` `--timeout`
- **`models`** : List or download on-device models (models list, models install parakeet). Arguments : ACTION (list or install (Required)) ; NAME (Model to install: parakeet). Options : `--json`
- **`tts`** : Generate speech audio from text using a local AI model (Kokoro-82M). Arguments : INPUT (Text to speak, or path to a .txt file). Options : `--text-file` `--output` `--voice` `--speed` `--lang` `--list` `--json`
- **`remove-background`** : Remove background from a video or image to produce transparent media. Arguments : INPUT (Source video (.mp4/.mov/.webm/.mkv) or image (.jpg/.png/.webp)). Options : `--output` `--background-output` `--device` `--quality` `--info` `--json`

### Account

- **`auth`** : Sign in to HeyGen and manage credentials. Options : `--api-key`
  - `auth login` : Sign in to HeyGen (OAuth by default; --api-key for long-lived keys)
  - `auth status` : Show the active HeyGen credential
  - `auth logout` : Remove the stored HeyGen credential
  - `auth refresh` : Force-refresh the OAuth access token

### Settings

- **`feedback`** : Submit feedback about your experience. Options : `--rating` `--comment` `--source` `--search-miss` `--wanted` `--tier` `--file-issue` `--dir` `--yes`
- **`telemetry`** : Manage usage telemetry. Arguments : SUBCOMMAND (Subcommand: enable, disable, status). Options : `--json`

## HyperFrames : attributs, animation, effets

Animation : Most composition authors do not implement this interface. HyperFrames already seeks registered GSAP, CSS, Anime.js, Lottie, Three.js, Web Animations, and TypeGPU animation through its browser runtime. Use the [GSAP guide](/guides/gsap-animation) for the normal authoring path. For a Three.js scene with a raster preview and a path-traced export, start from the [path-traced 3D example](/guides/path-tracing).

Exemples de départ (`hyperframes init --example <nom>`) : `decision-tree`, `kinetic-type`, `nyt-graph`, `play-mode`, `product-promo`, `swiss-grid`, `vignelli`, `warm-grain`.

Attributs `data-*` cités dans la documentation de la version (59) :

| Attribut | Rôle | Page |
|---|---|---|
| `data-attributes` | Topics: `data-attributes`, `examples`, `rendering`, `gsap`, `troubleshooting`, | packages/cli.mdx |
| `data-audio-group` | A plain id, not JSON | reference/audio-effects.mdx |
| `data-automation` | JSON | reference/audio-effects.mdx |
| `data-beat` | — | packages/cli.mdx |
| `data-chart` | — | guides/motion-graphics.mdx |
| `data-color-grading` | Everything lands in `data-color-grading`, in named sections: `adjust` for corrections, `details` for grain and | guides/media-effects.mdx |
| `data-color-group` | on an `<hf-color-group>` and point each clip at it with `data-color-group`: | reference/color-grading.mdx |
| `data-composition-file` | Returns `true` when `el` is the root of an inlined sub-composition — that is, it carries a `data-composition-file` attribute whose value differs from its parent's (or the parent has none). | sdk/reference/utilities.mdx |
| `data-composition-id` | Two rules make that work. | concepts/compositions.mdx |
| `data-composition-src` | `data-composition-src` names the file. | concepts/compositions.mdx |
| `data-composition-variables` | with `data-composition-variables`. | concepts/compositions.mdx |
| `data-duration` | An explicit root `data-duration` is the composition's render length: | concepts/data-attributes.mdx |
| `data-end` | For clips with `data-end`, the copy and any shifted clips keep their length by | packages/cli.mdx |
| `data-fade-in` | Clip-edge fades in seconds: gain rises 0 → 1 over the first `data-fade-in` seconds and falls 1 → 0 over the last `data-fade-out` seconds of the clip. | reference/html-schema.mdx |
| `data-fade-out` | — | reference/html-schema.mdx |
| `data-figma-unresolved` | Bound to a token you **haven't imported** → the literal color is used and the element is flagged `data-figma-unresolved`. | guides/figma.mdx |
| `data-fps` | The CLI uses the composition’s `data-fps` when present and otherwise defaults to 30 fps. | guides/rendering.mdx |
| `data-fx-carve` | JSON | reference/audio-effects.mdx |
| `data-fx-chain` | `data-vfx-chain` is JSON with the same field names as `data-fx-chain`: | guides/vfx-chain.mdx |
| `data-has-audio` | trims the start of the source. | guides/video-components.mdx |
| `data-height` | Missing composition dimensions (`data-width`, `data-height`) | packages/lint.mdx |
| `data-hf-` | All HTML attributes except `style`, `class`, and `data-hf-*` (those are represented elsewhere in the model). | sdk/guides/querying-and-editing.mdx |
| `data-hf-id` | `data-hf-id` values where they are missing so later edits target the same | sdk/quickstart.mdx |
| `data-hf-media-start-basis` | can preserve it explicitly with `data-hf-media-start-basis="global"`; new | concepts/compositions.mdx |
| `data-hidden` | `data-hidden`, and its own `data-fx-chain` / `data-automation`. | reference/audio-effects.mdx |
| `data-hold` | last 3 s (a held end card) or time when an element marked `data-hold` is on | packages/cli.mdx |
| `data-label` | `<hf-audio-group>` is optional metadata: `data-label`, `data-volume`, | reference/audio-effects.mdx |
| `data-layer` | — | reference/lint-rules.mdx |
| `data-layout-allow-caption-zone` | `data-layout-allow-caption-zone`. | packages/cli.mdx |
| `data-layout-allow-occlusion` | enters with `data-layout-allow-occlusion`. | packages/cli.mdx |
| `data-layout-allow-overflow` | re-run. | packages/cli.mdx |
| `data-layout-allow-overlap` | `data-layout-allow-overlap` on text you meant to stack, `data-layout-allow-occlusion` | packages/cli.mdx |
| `data-layout-ignore` | Captions-track text (`data-track-kind="captions"`) and `data-layout-ignore` | packages/cli.mdx |
| `data-link` | — | reference/lint-rules.mdx |
| `data-media-start` | `class="clip"` lets the timeline show and hide it; `data-start` and `data-duration` say when; `data-media-start` | guides/video-components.mdx |
| `data-motion-blur` | `on` enables blur. | guides/motion-blur.mdx |
| `data-motion-blur-events` | `on` runs timeline callbacks (`onUpdate` and similar) while blur looks for movers, and at each sample when a callback changes an element's inline style or its box. | guides/motion-blur.mdx |
| `data-motion-blur-phase` | When the shutter opens, in degrees of a frame, -360 to 360. | guides/motion-blur.mdx |
| `data-motion-blur-samples` | A fixed number of samples per frame, 2–64. | guides/motion-blur.mdx |
| `data-motion-blur-shutter` | Shutter angle in degrees, 0–720. | guides/motion-blur.mdx |
| `data-motion-blur-tier` | `auto` and `filter` draw with the filter tier; `capture` asks for the capture tier (below). | guides/motion-blur.mdx |
| `data-name` | Use `getElements()` for a flat snapshot of everything in the composition, or `find()` to filter by tag, text content, `data-name` attribute, track index, or sub-composition host. | sdk/quickstart.mdx |
| `data-no-timeline` | meant to be still can declare `data-no-timeline` to skip the guard. | packages/cli.mdx |
| `data-playback-rate` | forward by the time elapsed multiplied by `data-playback-rate`, so the | concepts/compositions.mdx |
| `data-playback-start` | `data-playback-start` picks which moment of the child timeline shows first. | concepts/compositions.mdx |
| `data-requires-webgpu` | A composition marked `data-requires-webgpu` must be able to create a WebGPU | packages/engine.mdx |
| `data-start` | When the element enters the composition timeline | concepts/data-attributes.mdx |
| `data-timeline-role` | `data-timeline-role="music"`, or an id like `music`, `bgm`, or `soundtrack` — | packages/cli.mdx |
| `data-track-index` | `data-duration`, and `data-track-index`; the timeline is created **paused**; and | concepts/data-attributes.mdx |
| `data-track-kind` | Captions-track text (`data-track-kind="captions"`) and `data-layout-ignore` | packages/cli.mdx |
| `data-var-` | its own text and colors. | concepts/compositions.mdx |
| `data-var-src` | `data-var-src` replaces an image, video, audio, or source URL. | concepts/variables.mdx |
| `data-var-text` | `data-var-text` replaces the element’s own text. | concepts/variables.mdx |
| `data-variable-values` | — | concepts/compositions.mdx |
| `data-vfx-chain` | `data-vfx-chain` gives an element a chain of per-pixel WebGL2 kernels — warps, | guides/vfx-chain.mdx |
| `data-volume` | `data-volume`. | guides/video-components.mdx |
| `data-width` | Missing composition dimensions (`data-width`, `data-height`) | packages/lint.mdx |
| `data-x` | Sets the element's position via `data-x` / `data-y` attributes. | sdk/reference/edit-operations.mdx |
| `data-y` | Sets the element's position via `data-x` / `data-y` attributes. | sdk/reference/edit-operations.mdx |

## HyperFrames : catalogue (blocs et composants)

448 éléments (210 blocs = scènes complètes, 238 composants = effets à poser dans une scène), installables par `npx hyperframes add <nom>` dans `hyperframes/<projet>/`. Classés par famille (premier mot-clé reconnu). « 9:16 » = bloc déjà vertical (14).

### Transitions (74)

- `avatar-group-hover` (composant) : A distance-falloff avatar group lift with bouncy hover return
- `badge-pop` (composant) : A transitions.dev-inspired notification badge pop with elastic scale and count reveal
- `beat-freeze-cut` (bloc 1920×1080, 6 s) : A beat-driven speed ramp, freeze-frame hit, and hard-cut sequence for music-led promos and montages.
- `before-after-wipe` (composant) : Two full-bleed content slots compare before and after states as a persistent divider wipes the after layer over the before layer and rests at a configurable split.
- `caption-clip-wipe` (composant) : Left-to-right clip-path wipe reveal per word
- `card-resize` (composant) : A transitions.dev-inspired card resize primitive that expands a compact card into a detail panel
- `chromatic-aberration-wipe` (composant) : A fast slide wipe with RGB channel split on peak frames.
- `chromatic-radial-split` (bloc 1920×1080, 4 s) : Shader transition with chromatic aberration radial split
- `cinematic-zoom` (bloc 1920×1080, 4 s) : Shader transition with dramatic zoom blur
- `code-slice-hero` (bloc 1920×1080, 8 s) : A tiled headline surface flips cell by cell under a sweeping depth field to reveal the rear headline.
- `colorama-wipe` (composant) : Headline reveal through a feathered, leaning wipe front that is blurred and colour-mapped as it passes, then settles to clean type and wipes off again — the After Effect…
- `comparison-split` (composant) : Two full-bleed panels compare before and after states as a persistent divider wipes the vivid after layer over the muted before layer and rests at a configurable split.
- `cross-warp-morph` (bloc 1920×1080, 4 s) : Shader transition with cross-warped morphing
- `curtain-reveal` (composant) : Two pleated stage curtains gather outward from center, the way real velvet bunches at the tieback, revealing the stage underneath.
- `cut-the-curve` (composant) : A velocity-matched directional hard cut: the outgoing subject accelerates with power4.in, swaps at peak velocity, and the incoming subject continues in the same directio…
- `directional-wipe` (composant) : A directional scene push that slides one panel over another.
- `domain-warp-dissolve` (bloc 1920×1080, 4 s) : Shader transition with fractal noise domain warping
- `editorial-flash-overlay` (bloc 1920×1080, 4 s) : Finite neutral-warm light layers for a seek-safe camera-flash cut or social reveal
- `fade-through` (composant) : A calm transition primitive that fades one layer out, passes through a wash, and reveals the next layer
- `flash-through-white` (bloc 1920×1080, 4 s) : Shader transition with white flash crossfade
- `glitch` (bloc 1920×1080, 4 s) : Shader transition with digital glitch artifacts
- `gravitational-lens` (bloc 1920×1080, 4 s) : Shader transition with gravitational lensing distortion
- `grid-pixelate-wipe` (composant) : Transition effect where the screen dissolves into a grid of squares that fade out with staggered timing — use between scenes
- `halftone-dissolve` (composant) : Scene A dissolves into scene B through a growing halftone dot field: accent ink dots pop onto a fixed grid smallest-first, each opens into a window onto B, until the win…
- `hw-scribble-transition` (bloc 1920×1080, 2.2 s) : Overlay transition: scribble bands accumulate to cover the frame with a solid backstop, the host cuts beneath, and the scribble clears
- `icon-swap` (composant) : A scale-and-blur icon swap primitive for toolbar and action state changes
- `input-feedback` (composant) : A transitions.dev-inspired input feedback primitive with shake, clear affordance, and success state
- `iris-reveal` (composant) : A circle clip-path opens from an authored origin revealing state B over state A in one confident pass, then holds on B.
- `light-leak` (bloc 1920×1080, 4 s) : Shader transition with cinematic light leak overlay
- `match-cut` (composant) : A circle accelerates into a hard single-frame scene swap, matches the incoming circle exactly, and continues into a smaller resting pose.
- `menu-morph` (composant) : A transitions.dev-inspired hamburger and plus-menu morph primitive for compact action menus
- `micro-transitions` (composant) : A transitions.dev-inspired pack of badge, dropdown, modal, tabs, tooltip, and success-check micro transitions
- `mk-clone-wall-transition` (bloc 1920×1080, 2.4 s) : Overlay transition: a tiled word wall covers the frame, inverts via difference blending, and clears — hard-cut the content beneath while covered
- `morph-swap` (composant) : Two slotted siblings stacked at one shared center: A holds, then condenses or reshapes into B on a shared 50% 50% transform origin.
- `number-pop-in` (composant) : A transitions.dev-inspired digit pop-in with blur, lift, and staggered value reveal
- `ordered-dither-pass` (composant) : Bayer-matrix ordered dithering quantizes a slotted scene (rasterized once at mount): the image emerges from pure 2-tone noise to clean, or dissolves the reverse.
- `organic-light-leak-overlay` (bloc 1920×1080, 4 s) : Finite CSS light-leak overlay for memory beats and motivated transitions
- `page-slide` (composant) : A transitions.dev-inspired page slide primitive with outgoing and incoming panels
- `panel-reveal` (composant) : A panel reveal primitive with height expansion and content fade
- `paper-collage-reveal` (composant) : A scrapbook patchwork of torn paper scraps, each with its own texture and tilt, flutters away in a staggered scatter to reveal the content underneath.
- `parallax-device-dive` (composant) : A canonical phone rises into view before the camera pushes through its screen and layered app UI expands to fill the frame.
- `parallax-unzoom` (composant) : Reveal transition — focus card scales down from full frame as siblings parallax in to form a grid (reverse of parallax-zoom)
- `parallax-zoom` (composant) : Center card scales up to fill the frame while siblings parallax outward — inspired by the eBay Playbook hero transition
- `ridged-burn` (bloc 1920×1080, 4 s) : Shader transition with ridged turbulence burn effect
- `ripple-waves` (bloc 1920×1080, 4 s) : Shader transition with concentric ripple wave distortion
- `rubber-band-bumper` (composant) : An outgoing panel pulls against increasing resistance, holds at tension, then snaps past an edge with overshoot as the incoming panel settles behind it.
- `sdf-iris` (bloc 1920×1080, 4 s) : Shader transition with signed distance field iris reveal
- `skeleton-reveal` (composant) : A skeleton loader transition that pulses, then cross-fades into content
- `success-check` (composant) : A success check primitive with ring pop, path draw, and subtle rotate blur
- `swirl-vortex` (bloc 1920×1080, 4 s) : Shader transition with swirling vortex distortion
- `tabs-slide-indicator` (composant) : A pill indicator transition that slides between active tabs
- `text-match-cut` (composant) : One line of text becomes another mid-move: both ride a single 85 % easy-ease curve and hard-swap at the speed peak, as scale, tracking, or a same-direction slide.
- `text-stagger` (composant) : A transitions.dev-inspired text stagger primitive with enter, shimmer, and exit-ready words
- `text-state-swap` (composant) : A text state swap primitive with outgoing blur and incoming lift
- `thermal-distortion` (bloc 1920×1080, 4 s) : Shader transition with heat haze thermal distortion
- `tilt-card` (composant) : A transitions.dev-inspired tilt card primitive with depth layers and hover-style parallax
- `torn-paper-rip` (composant) : A fibrous paper tear runs across the frame: the torn sheet shows its white paper core along the edge and lifts away on a soft shadow, leaving the next scene standing.
- `transitions-3d` (bloc 1920×1080, 11 s) : Showcase of 3D perspective flip and rotate transitions
- `transitions-blur` (bloc 1920×1080, 20 s) : Showcase of blur-based transitions between scenes
- `transitions-cover` (bloc 1920×1080, 21 s) : Showcase of cover/uncover slide transitions
- `transitions-destruction` (bloc 1920×1080, 14 s) : Showcase of destructive break-apart transitions
- `transitions-dissolve` (bloc 1920×1080, 24 s) : Showcase of dissolve and fade transitions
- `transitions-distortion` (bloc 1920×1080, 21 s) : Showcase of warp and distortion transitions
- `transitions-grid` (bloc 1920×1080, 11 s) : Showcase of grid-based tile transitions
- `transitions-light` (bloc 1920×1080, 21 s) : Showcase of light-based glow and flash transitions
- `transitions-mechanical` (bloc 1920×1080, 15 s) : Showcase of mechanical shutter and iris transitions
- `transitions-other` (bloc 1920×1080, 20 s) : Showcase of miscellaneous creative transitions
- `transitions-push` (bloc 1920×1080, 24 s) : Showcase of push and slide transitions
- `transitions-radial` (bloc 1920×1080, 20 s) : Showcase of radial wipe and reveal transitions
- `transitions-scale` (bloc 1920×1080, 15 s) : Showcase of scale and zoom transitions
- `type-match-cut` (composant) : A headline splits vertically around an incoming panel, which grows from the negative space and takes the frame as the words exit through opposite edges.
- `whip-pan` (bloc 1920×1080, 4 s) : Shader transition simulating a fast camera whip pan
- `whip-pan-cut` (composant) : A full-frame whip pan: scene A whips off laterally with capped directional motion blur while scene B enters in the same direction at matched velocity, on a speed-ramp pr…
- `zoom-through-transition` (composant) : A transition that zooms through a focal card into the next scene.

### Sous-titres (16)

- `caption-camera-follow` (composant) : One sentence written across a world far larger than the frame.
- `caption-editorial-emphasis` (composant) : Dual-font system with dramatic size contrast for emphasis words
- `caption-emoji-pop` (composant) : Emoji integration with stroked text and horizontal squeeze entrance
- `caption-glitch-rgb` (composant) : RGB chromatic aberration with CRT scanline overlay
- `caption-gradient-fill` (composant) : Gradient-clipped text with elastic bounce entrance
- `caption-highlight` (composant) : Red background sweep behind each active word, TikTok-style
- `caption-kinetic-slam` (composant) : Full-screen single-word display with alternating entrance directions
- `caption-matrix-decode` (composant) : Character scramble animation before text reveal
- `caption-neon-accent` (composant) : Multi-color neon glow accents with wiggle drift animation
- `caption-neon-glow` (composant) : Cyan and magenta neon glow with keyword accent colors
- `caption-parallax-layers` (composant) : Behind-subject 3D text layering with vertical stretch effect
- `caption-particle-burst` (composant) : Keyword words trigger colored particle explosions
- `caption-pill-karaoke` (composant) : Pill-shaped container with per-word karaoke color highlight
- `caption-texture` (composant) : Flowing texture mask over large uppercase text — ships with 6 textures (lava, marble, metal, wood, concrete, rock), configurable via the texture variable
- `caption-weight-shift` (composant) : Elegant font-weight transition between caption lines
- `mk-callout-highlight` (bloc 1920×1080, 8 s) : A sentence whose word-by-word emphasis is driven by a single scalar — tween it to sync the highlight with a voiceover

### Texte et titres (70)

- `blur-out-up` (composant) : Words arrive clean and depart upward with increasing blur for airy exits.
- `bottom-up-letters` (composant) : Splits text into letters and reveals each glyph from below with deterministic staggered timing
- `canopy-part-title` (bloc 1920×1080, 12 s) : Leaves sweep through the frame and part to reveal the headline.
- `caption-blend-difference` (composant) : Auto-inverting text using mix-blend-mode: difference — flips between white and black per-pixel against the background
- `caret-swap` (composant) : A gradient caret expands over one phrase, collapses to the left, then types its replacement with a blinking caret.
- `carousel-text-circle-1` (bloc 1920×1080, 5 s) : A headline mask-reveals word by word while a circle carousel converges from off-frame and threads the line, collapses to centre, hard-cuts to a second line that arrives …
- `carousel-text-circle-2` (bloc 1920×1080, 5 s) : A headline mask-reveals word by word while a circle carousel converges from off-frame and threads the line, collapses to centre, hard-cuts to a second line that arrives …
- `carousel-text-circle-3` (bloc 1920×1080, 5 s) : A headline mask-reveals word by word while a circle carousel converges from off-frame and threads the line, collapses to centre, hard-cuts to a second line that arrives …
- `carousel-text-circle-4` (bloc 1920×1080, 5 s) : A headline mask-reveals word by word while a circle carousel converges from off-frame and threads the line, collapses to centre, hard-cuts to a second line that arrives …
- `carousel-text-circle-5` (bloc 1920×1080, 5 s) : A headline mask-reveals word by word while a circle carousel converges from off-frame and threads the line, collapses to centre, hard-cuts to a second line that arrives …
- `char-slam-explode` (composant) : Headline glyphs hold in a deterministic scatter, then reassemble with an overshooting slam and a three-frame landing shake.
- `cursor-text-select` (composant) : An arrow turns into an I-beam over a document, drags a selection across a phrase character by character, raises a format toolbar, turns back into an arrow and clicks Bol…
- `extended-keyframe` (composant) : The never-fully-lands arrival: an element covers most of its move in the first fifth of the duration and creeps the rest to the last frame, exits along its arrival vecto…
- `extruded-logo` (bloc 1920×1080, 5 s) : Beveled 3D letters flip up one by one, the word swings so light runs across the bevels, then settles for a readable hold.
- `focus-blur-resolve` (composant) : A premium focus pull from heavy blur to crisp text, then a soft blur-out exit.
- `glass-hero` (bloc 1920×1080, 5 s) : A solid glass object rises in front of a giant headline and keeps turning, so the type bends and splits into colour through it.
- `glass-shard-title` (bloc 1920×1080, 12.16 s) : Glass shards fly in through fog and tile themselves into the headline.
- `headline-slam` (composant) : A heavyweight headline scales down into frame, lands with a deterministic three-frame shake, holds with subtle drift, and whips upward on exit.
- `hw-arrow` (composant) : Wobbled draw-on arrow with straight, gentle, and swoop curve poses, a four-way stroke texture matrix (plain/soft/sharp/spray), and a travel-aligned head-arrival stretch …
- `hw-boil` (composant) : Hand-drawn jitter that re-poses every N frames, as seek-safe helpers: pose derives from quantized timeline time through a seeded hash; includes the shared onUpdate dispa…
- `hw-box-label` (composant) : Wobbled rounded rectangle draws on — across the authored stroke matrix (plain/soft/sharp/spray) — or drops in and lands with a volume-true contact squash and bouncy spri…
- `hw-callout-circle` (composant) : Wobbled ellipse draws around a target with optional scribble fill and curved connector; the handwritten label pops in WITH momentum and the drawn shapes absorb the arriv…
- `hw-frame` (bloc 1920×1080, 8 s) : Media in a hand-drawn border with corner doodles and a handwritten caption; the unit tilts slightly and boils (images inside the block; keep live footage in the host)
- `hw-path-text` (bloc 1920×1080, 6 s) : Handwriting flowing along any SVG path with a per-character reveal; the path is the only geometry input
- `hw-pipeline` (bloc 1920×1080, 7 s) : Wobbled boxes with handwritten labels joined by curved connectors, drawing on in sequence from a node list
- `hw-text-cloud` (bloc 1920×1080, 6 s) : Hand-drawn speech bubble with a positionable tail: outline draws on, paper fill fades in, handwritten text types per character; boils
- `hw-title` (bloc 1920×1080, 6 s) : Handwritten display text with a scalar-driven word-by-word highlight sweep and a seeded squiggle underline sized to the text; boils
- `hw-underline` (composant) : Hand-drawn squiggle underline, double-pass strikethrough, and bracket marks that draw on
- `hw-write-title` (bloc 1920×1080, 6 s) : True glyph write-on: filled Caveat letterforms revealed by baked per-glyph centerline strokes traced in real stroke order with a curvature-adaptive pen-velocity ease (fa…
- `inline-highlight` (composant) : A clean marker-style inline highlight that animates behind text using a CSS scale variable
- `kinetic-center-build` (composant) : Words enter from the right and push the growing phrase left until the final line locks centered.
- `kinetic-type-swap` (composant) : A held sentence keeps its fixed text in place while one widest-word masked slot rolls through alternatives and settles on the final option.
- `line-by-line-slide` (composant) : Each line enters from the left with staggered slide and exits to the right.
- `line-swap` (composant) : A masked full-line beat replacement: line A holds center then exits up through an overflow-hidden mask as line B enters bottom-up on the same beat, with an optional acce…
- `logo-brand-close` (composant) : A display-scale wordmark cascades letter by letter into a centered lockup, the accent brand period lands last, an optional tagline and wide-tracked mono URL settle benea…
- `marker-checklist-card` (composant) : A hand-lettered paper card: marker headline with an underline and a drawn ellipse around one word, then three checklist rows whose checks draw themselves on - typewriter…
- `marker-highlight` (composant) : Display text settles in, then one hand-drawn marker stroke (highlight, circle, underline, or scribble) draws over the emphasized word on cue.
- `matrix-decode` (composant) : Random scramble resolves left-to-right into the target text.
- `mk-emphasis-type` (composant) : Oversized low-contrast background word drifting slowly behind the subject — typography as texture
- `morph-text` (composant) : Gooey text morph — cycles through an editable word list using SVG threshold + GSAP-driven blur for a fluid, satisfying transition effect
- `particle-text-dissolve` (composant) : Text assembles from a seeded particle cloud (or dissolves into it): per-particle targets sampled once from the rendered text bitmap at mount, table-driven particles, zer…
- `per-word-crossfade` (composant) : Words gently fade into place with a short vertical drift for calm keynote rhythm.
- `per-word-rise` (composant) : Words or characters rise into place in a controlled blur-to-sharp cascade, settle softly on landing, and hold still until the cut (optional fade or up exit).
- `perspective-marquee` (composant) : A 3D tilted marquee with depth feel as items roll toward the horizon.
- `rgb-glitch-text` (composant) : RGB-offset text copies jitter briefly for a controlled glitch window.
- `scan-band` (composant) : A diagonal distortion band sweeps once across a clean wordmark, revealing clipped red and cyan offsets only inside the moving band.
- `scramble-reveal` (composant) : A deterministic hacker-style text reveal that cycles fixed glyph rows and locks the target string from left to right.
- `shared-axis-y` (composant) : Per-word vertical shared-axis transition for sharp editorial swaps.
- `shared-axis-z` (composant) : Scale-based shared-axis transition for focus shifts and context depth.
- `shimmer-sweep` (composant) : Animated light sweep across text or elements using a CSS gradient mask — ideal for AI accents and premium reveals
- `slot-machine-roll` (composant) : A vertical reel scrolls characters from one value to another.
- `soft-blur-in` (composant) : A soft opacity, blur, and lift reveal for headlines, captions, and product UI callouts
- `split-flap-board` (bloc 1920×1080, 3.5 s) : Solari-style departure board: every cell walks its drum forward through the intervening characters of a fixed alphabet until it lands on its target, so the text resolves…
- `staggered-fade-up` (composant) : Words fade in and slide up one after another with configurable delay.
- `strikethrough-replace` (composant) : Draw a strike line across old text, then reveal the replacement.
- `text-shimmer` (composant) : A static headline receives one clean specular gradient sweep through its glyphs, then returns to its ordinary text color.
- `texture-mask-text` (composant) : CSS luminance masks that cut holes through letterforms - 66 pre-built texture masks from ambientCG PBR color maps
- `ticker-takeover` (composant) : A mono ticker rolls through options, locks on a final word with an accent flash, and promotes it into a full-frame headline.
- `titlecard-calm` (composant) : A restrained title card where a mono kicker and generous grotesque headline fade upward, drift almost imperceptibly, and exit cleanly.
- `titlecard-lockup` (composant) : The calm breather titlecard: an optional mono kicker fades up, the wordmark settles dead-center with one restrained move, a hairline rule draws left to right, a mono lab…
- `top-down-letters` (composant) : Letters descend from above in a pronounced staircase with zero blur.
- `tracking-in` (composant) : A precise letter-spacing reveal for premium headings and interface labels
- `typewriter` (composant) : Character-by-character text reveal with a deterministic blinking cursor.
- `variable-axis-type` (composant) : A locked one-line headline whose weight or width axis morphs into a decisive emphasis beat.
- `vfx-text-cursor` (bloc 1920×1080, 8 s) : Dramatic text reveal with cursor glow, chromatic shadow rays, and directional lighting on a black stage.
- `vox-annotate` (composant) : The Vox-style annotate gesture: a keyword in a held sentence gets a hand-drawn marker while a thin connector draws up to a mono callout label, all as one choreographed b…
- `weight-wave` (bloc 1920×1080, 6 s) : A crest of thickness travels along a headline: each character swells from light to black and leans forward as the wave passes, driven by the wght and slnt variable-font …
- `wireframe-portal-title` (bloc 1920×1080, 8 s) : A wireframe portal bursts open, the title comes through, then its letters swap into a second phrase.
- `wordmark-tiles` (composant) : A wordmark resolves from deterministic color noise into correctly cropped glyph tiles through a spatially modulated GSAP wave.
- `yt-prism-title` (bloc 1920×1080, 6 s) : Display title on a transparent root: blur-focus entrance, red/blue fringe that settles then breathes, perspective bow, slow scale drift

### Habillage (bandeaux, réseaux, annotations) (49)

- `agent-cursor` (composant) : An AI agent operating a UI: a cursor with an accent name label that types out each step, clicks each target with a small ring, and ends on a check.
- `camcorder-hud` (bloc 1920×1080, 4 s) : Responsive REC, battery, editable date placeholder, and timeline-driven counter overlay for creator-camera and camcorder treatments
- `cursor-annotate` (composant) : A marker pen glides onto the frame and hand-draws a loose loop, an underline, or an arrow around a region, the ink laid exactly under its nib, then lifts and leaves.
- `cursor-context-menu` (composant) : A cursor right-clicks a file, a context menu blooms from its tip, the hover highlight tracks the item under it, and the chosen action plays out: duplicate, rename, move …
- `cursor-drag-drop` (composant) : A cursor grabs a task card, lifts and tilts it into its motion, carries it in lockstep to an empty column, drops it with a small settle, and the list closes the gap behi…
- `cursor-glyph-trail` (composant) : A tutorial cursor path: on a settings screen the arrow clicks through three steps, leaving a dotted trail spaced evenly by distance and a numbered marker at each click; …
- `cursor-marquee-select` (composant) : A cursor drags a selection rectangle across a photo grid; each tile rings and pops a check the frame the rectangle touches it, while a pill counts the selection up.
- `cursor-zoom-follow` (composant) : Screen-recording auto-zoom: the camera pushes in toward each upcoming click, trails the cursor on a smooth spring, marks every click with a press and a ring, then eases …
- `dart-cursor` (composant) : A bold outlined arrowhead that dives in from camera depth, flies nose-first with motion blur along its path, squashes on two clicks, and whips out of frame.
- `freeze-frame-dressing` (bloc 1920×1080, 4 s) : Timeline-driven paper, tape, and flash dressing for a freeze-frame or background-removed subject
- `grain-overlay` (composant) : Animated film grain texture overlay using CSS keyframes — adds warmth and analog character to any composition
- `instagram-follow` (bloc 1080×1920 9:16, 4.5 s) : Animated Instagram follow overlay with profile card and follow button
- `light-sweep-pass` (composant) : A traveling key light re-shades a slotted scene: a soft diagonal gradient band crosses the frame once while every per-element highlight and shadow shifts in lockstep (al…
- `lower-third-bild` (bloc 1920×1080, 8 s) : News-style lower third with tight-fit text boxes: white headline bar with red drop-shadow, red sub-line with white drop-shadow.
- `lt-accent-underline` (bloc 1920×1080, 4.8 s) : Cardless lower third for footage overlay: name rises, an accent rule draws left-to-right, role fades in; text-shadowed for legibility
- `lt-bold-block` (bloc 1920×1080, 4.8 s) : High-energy podcast lower third: solid dark block wipes in, uppercase name slams up, accent tag pops
- `lt-clean-bar` (bloc 1920×1080, 4.8 s) : Minimal white-card lower third for podcasts/interviews: accent tab, name + role, clip-wipe entrance
- `lt-color-block` (bloc 1920×1080, 4.8 s) : High-energy lower third: bold accent-color block slides in with overshoot, condensed name + mono role
- `lt-dark-card` (bloc 1920×1080, 4.8 s) : Charcoal card lower third for bright footage: name, drawn accent underline, role; slide-up entrance
- `lt-kicker-name` (bloc 1920×1080, 4.8 s) : Cardless lower third with an accent eyebrow/kicker tag, heavy name, and a drawn baseline; for footage
- `lt-mask-reveal` (bloc 1920×1080, 4.8 s) : Cardless lower third: an accent sweep crosses and clip-path-reveals a heavy name, role fades up; for footage
- `lt-neon-border` (bloc 1920×1080, 4.8 s) : Two arcs of light travel the edge of a rounded panel and snap corner to corner, trailing a soft three-layer bloom.
- `lt-side-rule` (bloc 1920×1080, 4.8 s) : Cardless lower third with a vertical accent bar; condensed display name + mono role, text-shadowed for footage
- `lt-soft-pill` (bloc 1920×1080, 4.8 s) : Rounded white pill lower third for podcasts/interviews: status dot, name + role, scale-pop entrance
- `lt-stack-bars` (bloc 1920×1080, 4.8 s) : Two stacked bars: a dark name bar wipes from the left, an accent role bar wipes from the right
- `macos-notification` (bloc 1920×1080, 5 s) : Animated macOS-style notification banner with app icon and message
- `magnetic-cursor` (composant) : A soft dot pointer glides across an editor toolbar, is pulled into each button and morphs into its rounded hover plate while the icon leans toward it, presses one, and l…
- `multiplayer-cursors` (composant) : Labeled collaborator cursors with token-derived colors and soft glows drift from spread positions into a shared center zone, proving live multiplayer presence.
- `native-notification-pop` (composant) : One system-faithful notification banner (iOS or macOS) drops in over any scene on an accurate interruptible spring: fast arrival, soft overshoot, settled mass, backdrop …
- `news-ticker` (bloc 1920×1080, 7 s) : Premium broadcast-style lower-third ticker with live label, headline ribbon, and scrolling news crawl.
- `north-korea-locked-down` (bloc 1920×1080, 7 s) : Realistic map zoom into North Korea with a red scribble circle, locked-down pop-up label, and reddish editorial wash.
- `oversized-cursor` (composant) : The look-here pointer for a video: the macOS arrow at 3.5x its normal size lands its tip on one control, clicks it on, settles just below it so the result stays in view,…
- `press-ripple` (composant) : A cursor decel-arrives from off-stage, lands slightly off-center on a caller-positioned target, compresses with it in lockstep, releases with two small click rings while…
- `reddit-post` (bloc 1920×1080, 5 s) : Animated Reddit post card overlay with upvotes and comments
- `sheet-spring-up` (composant) : A bottom sheet rushes up from below the frame on a real spring sampled frame by frame from reference footage, overshooting its resting place and settling back without an…
- `snow` (bloc 1920×1080, 6 s) : Seek-safe falling-snow overlay: sparse or dense flakes drift down with size, speed and opacity correlated per flake for depth, radial-masked so the frame center stays cl…
- `spotify-card` (bloc 1080×1920 9:16, 5 s) : Animated Spotify now-playing card with album art and progress bar
- `starfield` (bloc 1920×1080, 6 s) : Seek-safe night-sky overlay: sparse or dense stars in three size tiers that twinkle and drift in two parallax layers, radial-masked to keep the frame center clear
- `thread-message-stack` (bloc 1920×1080, 8 s) : A source-owned editable conversation stack with arbitrary incoming and outgoing messages
- `tiktok-follow` (bloc 1080×1920 9:16, 4.5 s) : Animated TikTok follow overlay with profile card and follow button
- `touch-indicator` (composant) : A translucent contact-circle gesture actor for mobile UI scenes: it touches the glass on the frame the host target responds, then lifts.
- `typing-indicator` (composant) : The three-dot chat bubble that says someone is writing: it pops in at the thread's edge exactly as messaging apps do, holds while the reply is coming, and vanishes when …
- `vignette` (composant) : Cinematic radial vignette overlay using a pure-CSS gradient — darkens the edges to pull focus toward the center
- `x-post` (bloc 1920×1080, 5 s) : Animated X/Twitter post card overlay with engagement metrics
- `yt-circle-pointer` (composant) : Draw-on annotation ellipse around a target plus a countdown chip that pulses each tick
- `yt-comment-card` (bloc 1920×1080, 8 s) : Social comments typing on over footage: avatar pop, username and time, per-character typewriter, likes row; image avatars or initials chips
- `yt-feather-highlight` (composant) : Dims the frame except a feathered ellipse; the hole's position and size are CSS variables, so helpers glide the spotlight between targets
- `yt-lower-third` (bloc 1920×1080, 4.5 s) : Animated YouTube subscribe lower third with avatar and channel info
- `yt-screen-warp` (composant) : Grid, scanline, vignette, and sheen overlay plus a 3D-warp wrapper class that makes footage read as if playing on a physical display

### Produit et maquettes d’interface (50)

- `ai-answer-rank` (bloc 1080×1080, 9 s) : Is your brand in the AI answer?
- `ai-chat-reveal` (bloc 1080×1920 9:16, 19.3333 s) : A question is typed on a rising keyboard, sent, and answered by an AI that streams its reply word by word on a measured token rhythm - thinking dot, uneven bursts, bulle…
- `browser-device-stage` (composant) : A generic app surface in token-native device chrome (browser, window, or phone).
- `camera-scan-gate` (composant) : A camera and QR recognition moment with a viewfinder sweep, bracket lock, confirmation pulse, and verified next beat.
- `chat-message` (composant) : One message arrives on the measured entry - scale 0.75, 0.12s, growing from its sender's corner.
- `chat-thread` (composant) : The measured conversation as one mountable scene at full fidelity: status bar, back badge, avatar and name pill, bubbles with real iMessage tails, a Delivered receipt, l…
- `chatgpt-exchange` (bloc 1080×1920 9:16, 14.9 s) : A portrait ChatGPT-style exchange types and sends a prompt, streams an answer, assembles a comparison table, and scrolls back through the result
- `claude-exchange` (bloc 1080×1920 9:16, 21.4 s) : A portrait Claude-style exchange types a prompt, works through search and reasoning steps, then streams a detailed answer with citations and actions
- `code-3d-extrude` (bloc 1920×1080, 8 s) : Syntax-highlighted code on a lit, beveled 3D slab that rotates through real space and settles to a readable rest — true WebGL depth and lighting, not a 2D transform.
- `code-diff` (bloc 1920×1080, 6 s) : An edit shown as a colored diff — removed lines collapse in red, added lines expand in green.
- `code-highlight` (bloc 1920×1080, 5 s) : A highlight band sweeps across a target line while the surrounding context dims — draws the eye to one line.
- `code-morph` (bloc 1920×1080, 7 s) : One snippet transforms into another — tokens glide between positions, leavers fade out, enterers fade in.
- `code-particle-assemble` (bloc 1920×1080, 8 s) : Thousands of GPU points scatter through space and fly to the exact glyph pixels of the code, resolving into readable syntax-highlighted text — a particle system, not a t…
- `code-scroll` (bloc 1920×1080, 6 s) : The camera scrolls a long file to bring a target line to center and spotlights it — for walking through real modules.
- `code-shader-dissolve` (bloc 1920×1080, 7 s) : The code compiles into existence: a GPU fragment shader resolves it out of seeded noise with a chromatic dissolve front and edge glow, then holds crisp.
- `code-snippet-apple-terminal-pro` (bloc 1920×1080, 12 s) : Apple Terminal Pro profile: black background with grey text and lime green cursor, per-character typing animation of a shell session.
- `code-snippet-dark-2026` (bloc 1920×1080, 11 s) : VS Code workbench with per-character typing animation in the Dark 2026 theme.
- `code-snippet-dark-modern` (bloc 1920×1080, 11 s) : VS Code workbench with per-character typing animation in the Dark Modern theme.
- `code-terminal-run` (composant) : A token-chrome terminal panel runs one command: the prompt line types deterministically behind an integer-cycle caret, executes after a beat, and output lines print one …
- `code-typing` (bloc 1920×1080, 5 s) : Token-streamed typing reveal with a caret that tracks the frontier — deterministic, no CSS animation.
- `cta-close` (composant) : A display-scale action line lands per word and fills the frame with air, one generous CTA capsule pops beneath it with a single overshoot, and the finished close holds c…
- `cta-lockup` (composant) : A canonical closing lockup that reveals an action line, pops in an accent CTA capsule, settles supporting microcopy, and holds with confidence.
- `device-frame-stage` (composant) : A phone or tablet mockup staged as a physical scene prop with a screen slot for arbitrary reconstructed UI, rising onto the stage, settling, and holding an idle float
- `focus-swap` (composant) : Moves attention between two side-by-side cards as one recedes with scale, blur, and dimming while the other advances to full focus.
- `gesture-tap` (composant) : A contact circle taps a mobile pill button, releases it into a new labeled accent state, and lifts away.
- `icon-morph-beat` (composant) : An icon morphs between authored state silhouettes, shifts to an accent color, and marks completion with one restrained pulse.
- `message-thread-reveal` (bloc 1080×1920 9:16, 25.7667 s) : A full text conversation plays out on a phone - bubbles popping in, typing indicators, a shared link card, emoji, delivered receipts - with the whole thread scrolling up…
- `notes-reveal` (bloc 1080×1920 9:16, 24.85 s) : A personal note is typed character by character in a notes app - caret riding every letter, the page scrolling up on measured settle curves as each line lands - then cut…
- `notes-typing` (composant) : The notes-app confession as a mountable scene: a bold title, then body lines typed character by character on the measured human keystroke rhythm, the caret riding every …
- `notification-cascade` (bloc 1080×1920 9:16, 14 s) : Phone notifications land one after another and stack up the screen, each banner pushing the pile down as it arrives, before the whole stack lifts away into a closing card
- `notification-pileup` (composant) : Mobile notification cards arrive faster and faster, each new alert pushing the existing stack downward into a dense, anxious tower.
- `notification-stack` (composant) : 1 to 5 token notification cards slide-settle into a vertical stack on cues, newest on top; one card grows slightly and brightens as the focus while the rest dim by posit…
- `offset-path-traveler` (composant) : A slotted traveler follows an authored path with tangent rotation, curved entry, and curved exit.
- `screen-flow-carousel` (composant) : Two to five app screens ride a horizontal rail: one primary at center, neighbors receded, advancing on cues with a velocity-matched throw and a smooth long-tail catch wh…
- `segmentation-flood` (composant) : Machine-vision read of a slotted subject: translucent accent segmentation masks flood on in quantized scanline steps, each region gets a thin bracket and mono label chip…
- `share-sheet-carousel` (bloc 1080×1920 9:16, 7.2333 s) : A share sheet springs up from the bottom of the phone and cycles previews inside its card on a fast cut rhythm while the blurred ground swaps behind it, ending on an acc…
- `slack-notification-ad` (bloc 1080×1920 9:16, 12 s) : A portrait lock screen fills with escalating Slack video requests before HeyGen delivers the payoff
- `soft-blob-touch` (composant) : A granular soft blob idles with slow internal drift; a scripted touch dot decel-arrives, the blob deforms toward it with an attraction bulge, then recovers with a veloci…
- `spring-stack-shuffle` (composant) : A stack of 3 to 5 slotted cards reshuffles on cues: the back card throws over the top and lands at the front with real mass, the rest compress and resettle; cues that la…
- `state-chip-rail` (composant) : A rail of mono status chips advances a seek-safe data-state snap machine on a cue schedule: active chip ink on surface, done chips dim, pending chips hollow, optional ba…
- `sticky-mock-swap` (composant) : A pinned product mock cross-fades through accent-tinted feature states while matching captions rise, hold, and exit beside it.
- `store-badge-lockup` (composant) : Settles a short headline above equal-size App Store and Google Play badges as a token-driven mobile end-card call to action.
- `streaming-text` (composant) : Words arrive the way an AI answer streams - in uneven bursts on a measured token rhythm, each word landing grey and inking to full colour - rather than the even tick of …
- `telemetry-hud` (composant) : Quiet mono debug-HUD readouts frame a slotted subject: corner brackets draw on, label:value lines tick their values on cues, one readout emphasized in accent.
- `testimonial-card` (composant) : Reveals a customer quote at reading pace, then settles its avatar, author name, and handle beneath as a clean proof beat.
- `toggle-flip` (composant) : An oversized UI toggle switch that flips with real physicality: thumb overshoot, track color crossfade, and a soft press-compress before release.
- `tracing-beam` (composant) : A glowing dash follows one SVG path through three UI elements, lifting and brightening each element in sequence.
- `typed-prompt` (composant) : A prompt line types itself in chunked human cadence behind a deterministic blinking caret, with optional backspace-and-retype correction of the final word.
- `ui-focus-zoom` (composant) : A full app surface establishes with one settle, then the camera zooms and pans to an anchored region on its cue and holds the zoomed state, with an optional soft focus h…
- `vector-editor-rig` (composant) : A dark design-tool app chrome with a live vector pen path, sequential anchor points, bezier handles, a selection frame, and theme-driven blue accents.

### Images, galeries, carrousels, vidéo (28)

- `arc-motion-path` (composant) : A GSAP MotionPath primitive that flies a callout along a curved arc with autorotation.
- `blur-in` (composant) : An Operator Black word-level content reveal that resolves its own text from controlled blur
- `carousel-circle-1` (bloc 1920×1080, 6 s) : Image cards ride a circle with a size gradient by depth angle, sweeping in fast-slow-fast swings (Circle style 1); 12 image slots.
- `carousel-circle-2` (bloc 1920×1080, 6 s) : Image cards ride a circle with a size gradient by depth angle, sweeping in fast-slow-fast swings (Circle style 2); 12 image slots.
- `carousel-circle-3` (bloc 1920×1080, 6 s) : Image cards ride a circle with a size gradient by depth angle, sweeping in fast-slow-fast swings (Circle style 3); 12 image slots.
- `carousel-circle-4` (bloc 1920×1080, 6 s) : Image cards ride a circle with a size gradient by depth angle, sweeping in fast-slow-fast swings (Circle style 4); 12 image slots.
- `carousel-circle-5` (bloc 1920×1080, 6 s) : Image cards ride a circle with a size gradient by depth angle, sweeping in fast-slow-fast swings (Circle style 5); 12 image slots.
- `carousel-orbit-1` (bloc 1920×1080, 6 s) : Image cards on a spinning 3D Fibonacci sphere, billboarded to the camera, sized by camera distance (Orbit style 1); 24 image slots.
- `carousel-orbit-2` (bloc 1920×1080, 6 s) : Image cards on a spinning 3D Fibonacci sphere, billboarded to the camera, sized by camera distance (Orbit style 2); 24 image slots.
- `carousel-orbit-3` (bloc 1920×1080, 6 s) : Image cards on a spinning 3D Fibonacci sphere, billboarded to the camera, sized by camera distance (Orbit style 3); 24 image slots.
- `carousel-orbit-4` (bloc 1920×1080, 6 s) : Image cards on a spinning 3D Fibonacci sphere, billboarded to the camera, sized by camera distance (Orbit style 4); 24 image slots.
- `carousel-orbit-5` (bloc 1920×1080, 6 s) : Image cards on a spinning 3D Fibonacci sphere, billboarded to the camera, sized by camera distance (Orbit style 5); 24 image slots.
- `carousel-path-1` (bloc 1920×1080, 6 s) : Image cards ride an open bezier path (arc, V, diagonal, wave, S-curve) with depth scaling and tangent rotation (Path style 1); 24 image slots.
- `carousel-path-2` (bloc 1920×1080, 6 s) : Image cards ride an open bezier path (arc, V, diagonal, wave, S-curve) with depth scaling and tangent rotation (Path style 2); 12 image slots.
- `carousel-path-3` (bloc 1920×1080, 6 s) : Image cards ride an open bezier path (arc, V, diagonal, wave, S-curve) with depth scaling and tangent rotation (Path style 3); 12 image slots.
- `carousel-path-4` (bloc 1920×1080, 6 s) : Image cards ride an open bezier path (arc, V, diagonal, wave, S-curve) with depth scaling and tangent rotation (Path style 4); 24 image slots.
- `carousel-path-5` (bloc 1920×1080, 6 s) : Image cards ride an open bezier path (arc, V, diagonal, wave, S-curve) with depth scaling and tangent rotation (Path style 5); 24 image slots.
- `carousel-vision-1` (bloc 1920×1080, 6 s) : A ring of large image cards tilted into a row under a 3D camera, each card turning toward the centre (Vision style 1); 12 image slots.
- `carousel-vision-2` (bloc 1920×1080, 6 s) : A ring of large image cards tilted into a row under a 3D camera, each card turning toward the centre (Vision style 2); 12 image slots.
- `carousel-vision-3` (bloc 1920×1080, 6 s) : A ring of large image cards tilted into a row under a 3D camera, each card turning toward the centre (Vision style 3); 12 image slots.
- `carousel-vision-4` (bloc 1920×1080, 6 s) : A ring of large image cards tilted into a row under a 3D camera, each card turning toward the centre (Vision style 4); 12 image slots.
- `carousel-vision-5` (bloc 1920×1080, 6 s) : A ring of large image cards tilted into a row under a 3D camera, each card turning toward the centre (Vision style 5); 12 image slots.
- `cuboid-carousel` (bloc 1920×1080, 6.67 s) : A chain of bevelled cuboids rides a travelling wave as a content carousel.
- `dynamic-grid` (composant) : A responsive animated grid background driven by CSS variables for SaaS, code, and data scenes
- `number-wheel` (composant) : A rolling digit counter primitive for metrics, prices, counts, and scoreboards
- `separator` (composant) : A one-pixel structural separator with horizontal and vertical variants plus a seek-safe progress reveal
- `svg-line-draw-loader` (composant) : An Anime.js-style path drawing loader implemented as a seekable GSAP stroke timeline.
- `three-orbiting-cards` (composant) : A Three.js-powered orbit scene driven by a paused GSAP timeline for deterministic renders.

### Fonds, textures, lumière (39)

- `ascii-render-pass` (composant) : A slotted scene renders as live ASCII: a canvas samples the source's luminance grid (rasterized once at mount) and draws glyphs from a density ramp charset; resolution s…
- `aurora` (bloc 1920×1080, 2 s) : Green and violet aurora curtains ripple across a night sky.
- `aurora-drift` (composant) : Three soft accent-derived aurora fields drift in an exact ambient loop over a deep base and faint vignette.
- `beat-pulse-background` (composant) : An accent-derived backdrop pulses its glow intensity and saturation on a deterministic, supplied beat grid.
- `blob` (bloc 1920×1080, 2 s) : A soft coral and pink blob with a warm highlight slowly changes shape on black.
- `color-wheel` (bloc 1920×1080, 2 s) : A wide gradient slides slowly through the colours of the rainbow.
- `cosmic-orb` (bloc 1920×1080, 10 s) : An iridescent soap-bubble planet: a slowly spinning sphere of nebula bands, dust lanes and twinkling stars wrapped in a refracting glass limb with chromatic aberration a…
- `falling-lines` (bloc 1920×1080, 2 s) : White lines fall down the frame at varied speeds, each fading into a trail.
- `flowing-gradient` (bloc 1920×1080, 2 s) : Bands of orange and violet flow across the frame in a smooth gradient.
- `fractal-noise` (bloc 1920×1080, 2 s) : Soft grey fractal noise drifts across the frame like slow clouds.
- `frost-sequence-camera-orbit` (bloc 1920×1080, 22.5 s) : An orbiting camera follows an ice logo as it breaks apart, reforms into two text moments, and fades.
- `gabor-noise` (bloc 1920×1080, 2 s) : Grey streaky noise drifts across the frame like a moving fingerprint.
- `gallery-tunnel` (bloc 1920×1080, 12 s) : An infinite corridor of panels: a square tunnel receding to a vanishing point, its floor, ceiling and walls tiled with saturated colour slabs and caller-supplied images …
- `godrays` (bloc 1920×1080, 2 s) : Rays of light fan out from a corner and drift across a deep blue field.
- `grain-field` (composant) : A clearly visible accent-tinted dot field drifts over a subtle luminance gradient in an exact ambient loop.
- `halftone-field` (bloc 1920×1080, 10 s) : A full-bleed halftone light field: a grid of dots whose size and colour track a slow flowing simplex-noise field, so broad bands of light sweep across a mostly-black fra…
- `heatmap` (bloc 1920×1080, 2 s) : Thermal colours flow through a glowing orb, on black.
- `ink-bleed-reveal` (composant) : Liquid ink blooms through paper under a gooey blur-plus-threshold filter, merges, then contracts as a crisp slotted mark resolves beneath it, with static seeded paper gr…
- `lens-flare` (bloc 1920×1080, 2 s) : A camera lens flare: a bright star burst and a faint rainbow halo that slowly shimmer on black.
- `light-edge` (bloc 1920×1080, 2 s) : Purple and cyan light races around the edge of an orb on black.
- `marble` (bloc 1920×1080, 2 s) : Ink-dark veins wind through white in a marbled pattern that slowly shifts.
- `mesh-gradient` (bloc 1920×1080, 2 s) : Soft coral, orange and violet fields blend and drift in a mesh gradient.
- `mk-background` (bloc 1920×1080, 10 s) : Procedural soft-blob gradient backdrop in a minimalist presentation style: two radial blobs drifting over a base color, with an animatable rounded-card bar mask and opti…
- `particle-image-reveal` (composant) : A seeded deterministic particle field converges and settles while a slotted image reveals beneath it, the trail thinning until the image holds clean.
- `plasma` (bloc 1920×1080, 2 s) : Deep violet plasma folds and churns across the whole frame.
- `prism` (bloc 1920×1080, 2 s) : A white beam of light splits into a slowly turning rainbow.
- `ripples` (bloc 1920×1080, 2 s) : Concentric rings ripple outward from the centre, white on black.
- `sine-wave` (bloc 1920×1080, 2 s) : A glowing white sine wave travels across a black frame.
- `spiral` (bloc 1920×1080, 2 s) : A bold black and white spiral turns in the frame.
- `spiral-galaxy` (bloc 1920×1080, 10 s) : A spiral galaxy seen from outside, turning with real differential rotation: inner stars orbit faster than outer ones, so the arms wind up over the shot instead of spinni…
- `strands` (bloc 1920×1080, 2 s) : Thin ribbons of pink and blue light weave across a black field.
- `stripes` (bloc 1920×1080, 2 s) : Bold black and white diagonal stripes slide across the frame.
- `sun-burst` (bloc 1920×1080, 2 s) : Cream and black rays fan out from the centre and slowly turn.
- `swirl` (bloc 1920×1080, 2 s) : Orange and blue color fields swirl and flow into each other across the whole frame.
- `vfx-anamorphic-flare` (bloc 1920×1080, 10 s) : A drifting field of bright points, each one throwing the long horizontal blue-violet streak a real anamorphic cinema lens produces.
- `vfx-liquid-background` (bloc 1920×1080, 12 s) : Organic liquid simulation with vertex displacement on a subdivided plane.
- `voronoi` (bloc 1920×1080, 2 s) : Magenta cells with glowing blue centres shift and reshape across the frame.
- `worley-noise` (bloc 1920×1080, 2 s) : A field of drifting cells, light at their centres and dark at their edges.
- `yt-lcd-background` (bloc 1920×1080, 10 s) : Textured paper board: scanlines with slow drift, optional pixel grid, static grain, and display text with a blur-focus entrance and chromatic-fringe title

### Shaders et effets GPU (43)

- `avatar-cloud` (composant) : Lettermark avatars populate a loose elliptical cloud while fine SVG links draw between the community and its central proof label.
- `beat-accent` (composant) : A single music-hit sting: impact flash, micro scale-pulse on the subject, immediate decay.
- `camera-shake` (composant) : Procedural handheld, telephoto and rig camera shake for any wrapper: nine measured profiles with per-lens projection, closed-form and seek-safe
- `chrome-orb` (bloc 1920×1080, 2 s) : A mirror-chrome orb reflects a bright studio light, on black.
- `cinemagraph` (bloc 1920×1080, 10 s) : A still photograph with one living region: the frame is frozen while a single feathered window keeps moving - here, steam rising over a cup - drawn from the seek time al…
- `confetti` (composant) : A deterministic celebration burst with seeded particles and gravity.
- `echo-smear` (composant) : Distance-adaptive streak — records each element's real trajectory (position, rotation, scale, opacity), then trails time-offset copies behind it in proportion to its spe…
- `exploded-stack` (bloc 1920×1080, 5 s) : Isometric layer plates explode apart with a label beside each layer, hold, then collapse back into one stack.
- `filmed-screen` (composant) : Your scene, filmed off a screen: perspective, depth of field that follows an element you name, LED sub-pixels and per-shot colour grades.
- `frost` (bloc 1920×1080, 2 s) : A frozen blue orb with frost creeping in from its edge, on black.
- `goo` (bloc 1920×1080, 2 s) : A glossy green liquid ball whose surface bulges and ripples like wet goo, centred on black.
- `gooey-split` (bloc 1920×1080, 4.7 s) : A dot splits into a three-dot menu with a gooey metaball neck, spins into a swirl mark under directional shutter motion blur, then breaks back into three dots and merges…
- `hologram` (bloc 1920×1080, 2 s) : A pale blue holographic orb with scan rings and flicker, on black.
- `holographic` (bloc 1920×1080, 2 s) : An iridescent foil orb with a shifting rainbow sheen, centred on black.
- `ios26-liquid-glass` (bloc 1920×1080, 15 s) : 3D iPhone with a normal iOS 26 home screen, liquid glass app icons, shader wallpaper, dock, and fluid glass notifications that drop from the status area onto a GLTF devi…
- `liquid-glass-notification` (bloc 1920×1080, 8 s) : Frosted glass notification cards floating over an aurora shader background
- `liquid-glass-widgets` (bloc 1920×1080, 8 s) : Frosted glass stat cards, showcase panel and pill chips over an aurora shader background
- `liquid-metal` (bloc 1920×1080, 2 s) : A chrome sphere ripples and flows like molten metal on black.
- `macos-tahoe-liquid-glass` (bloc 1920×1080, 15 s) : 3D MacBook with a macOS Tahoe-style desktop, glass menu bar, Finder window, dock, and cinematic device camera move.
- `mesh-gradient-bg` (composant) : A render-safe mesh gradient using animated radial layers.
- `motion-blur` (composant) : After Effects-style motion blur — integrates each element over a shutter window (shutter angle, phase, samples per frame) by sampling the GSAP timeline at sub-frame time…
- `nebula` (bloc 1920×1080, 2 s) : A small world of pink and blue gas swirls inside a sphere on black.
- `obsidian` (bloc 1920×1080, 2 s) : A dark glass orb catches pink and cyan iridescent light on black.
- `outline-draw` (composant) : A rounded outline that proves a callout by drawing clockwise as a hollow conic-gradient border with a clean closure.
- `overwhelm-surround` (composant) : Tasks, tabs, pings, and notification bubbles accelerate inward around a calm central subject, turning overload into visible spatial pressure.
- `plastic` (bloc 1920×1080, 2 s) : A glossy white plastic orb with soft studio reflections, on black.
- `product-turntable` (bloc 1920×1080, 6 s) : A product turns a full revolution on a studio plinth in a seamless loop.
- `rack-focus` (bloc 1920×1080, 6 s) : A focus pull with real aperture bokeh: the focal plane travels from a near subject to a far one, so one resolves as the other blows into hard-edged polygon discs that cl…
- `scroll-feed` (composant) : A loop-friendly column of varied skeleton post cards scrolls upward with subtle motion trails and an agitated pace.
- `shutter-slam` (composant) : One word thrown through six single-property beats under integrated shutter blur — two translate slams, a scale punch, then a full turn about each axis — on the measured …
- `spotlight-card` (composant) : A card with a scripted cursor spotlight and lit border.
- `spring-pop` (composant) : A badge pops in from a visible near-rest scale, overshoots full size once, and settles cleanly.
- `stagger-cascade` (composant) : A responsive grid of tile cards that fades and travels into place with an evenly spaced per-item GSAP stagger.
- `svg-mask-reveal` (composant) : A soft token-colored sweep reveals media only through an editable SVG wordmark mask.
- `thin-film` (bloc 1920×1080, 2 s) : An orb's rim shimmers with soap-bubble iridescence on black.
- `vfx-iphone-device` (bloc 1920×1080, 15 s) : Real GLTF iPhone 15 Pro Max and MacBook Pro models with live HTML-in-Canvas screen content, morphing glass lens, product review camera choreography, and 360° turntable.
- `vfx-liquid-glass` (bloc 1920×1080, 20 s) : VFX composition block
- `vfx-magnetic` (bloc 1920×1080, 15 s) : VFX composition block
- `vfx-portal` (bloc 1920×1080, 10 s) : VFX composition block
- `vfx-shatter` (bloc 1920×1080, 12 s) : VFX composition block
- `water` (bloc 1920×1080, 2 s) : A sphere of wind-rippled water reflecting a blue sky, on black.
- `waveform` (bloc 1920×1080, 2 s) : Equalizer bars in a blue to pink gradient pulse across the middle of the frame, like an audio visualizer.
- `yt-camera-move` (composant) : Dynamic zoom, slide, and 3D tilt-pan helpers for any wrapper (video, include, card) with cubic-easing defaults and an edge-defocus pulse overlay

### 3D et caméra (11)

- `app-showcase` (bloc 1920×1080, 5.5 s) : Fitness app product showcase with three floating smartphone screens
- `camera-dolly-zoom` (bloc 1920×1080, 4 s) : Camera tracks toward or away from the subject while the field of view changes the opposite way, so the subject holds its frame size while the background collapses behind…
- `drift-hold` (composant) : A centered content card stays subtly alive through loop-exact rotation, scale breathing, and a slow light sweep.
- `focus-rack` (composant) : Focus shifts once between two cards at different apparent depths through synchronized blur, dimming, scale, and parallax.
- `locked-nucleus-orbit` (composant) : A fixed center nucleus anchors deterministic satellite orbits that settle into a composed lockup.
- `orbit-card` (bloc 1920×1080, 10 s) : A single feature card orbits a dot sphere on approved Blender camera motion.
- `pan-stations` (composant) : A lateral camera move across a continuous row of labeled feature stations, with a steady dwell at each stop before the next pan.
- `pull-back-reveal` (composant) : A tight stat detail holds, then one decelerating camera pull-back reveals the headline and supporting cards that recontextualize it.
- `push-in` (composant) : A centered headline gains focus through one slow, continuous camera push and a gentle fade out.
- `scroll-camera-story` (composant) : A compressed forced-scroll cinematic pass: a tall scene of slotted sections travels past the camera top to bottom, depth layers parallax at different rates, each section…
- `ui-3d-reveal` (bloc 1920×1080, 13 s) : Perspective 3D reveal animation for UI elements

### Données et cartes (18)

- `animated-bar-chart` (composant) : A compact data card with deterministic bar growth and value callouts.
- `bar-chart-race` (bloc 1920×1080, 12 s) : Ranked bars grow and overtake each other as a time series advances, with the axis rescaling as values climb and the accent handing over to whoever leads
- `chart-story` (composant) : One chart builds from data in reading order and lands the exact supplied values: staggered bars, a left-to-right line with area fill, a sweeping donut, or filling progre…
- `conic-progress-ring` (composant) : A token-driven conic progress ring whose angular fill and center count settle together from one registered percentage.
- `data-chart` (bloc 1920×1080, 15 s) : Animated bar + line chart with staggered reveal, NYT-style typography, and value labels
- `decline-chart` (composant) : A metric line draws downward as its value counts down and the ambient background darkens in lockstep.
- `logo-wall` (composant) : A trusted-by wall of placeholder lettermark logos that fades and scales into place with a deterministic per-cell stagger.
- `mk-line-graph` (bloc 1920×1080, 7 s) : One or two SVG series draw on with dots popping and value labels riding the draw front; dim baseline axis, x-labels, color-dot legend
- `nyc-paris-flight` (bloc 1920×1080, 6 s) : Apple-style realistic map animation with a plane flying from New York to Paris, marker circle, landing pop, and sound effects.
- `oscilloscope-trace` (bloc 1920×1080, 6 s) : CRT oscilloscope beam sweeping a waveform across a 10x8 graticule, with closed-form phosphor persistence: the tail decays as exp(-age/tau) and brightens where the beam s…
- `spain-map` (bloc 1920×1080, 12 s) : Animated Spain choropleth by autonomous community with staggered reveals and gradient legend — D3 conic conformal projection
- `star-rating-fill` (composant) : A token-driven star row whose colored layer sweeps to a rating, preserves the fractional final star, and can count the value in sync.
- `us-map` (bloc 1920×1080, 12 s) : Animated US choropleth map with staggered state reveals, value labels, and gradient legend — pure inline SVG with GSAP
- `us-map-bubble` (bloc 1920×1080, 12 s) : Animated US bubble map with proportional city markers, value callouts, and connection lines — composable with us-map
- `us-map-flow` (bloc 1920×1080, 12 s) : Animated connection arcs between US cities over a base map — composable origin-destination flow visualization
- `us-map-hex` (bloc 1920×1080, 10 s) : Animated hexagonal tile grid map — each state as an equal-weight hex with data fill and abbreviation label
- `week-in-merges` (bloc 1080×1350 9:16, 16 s) : Each author's avatar bounces across their row at a speed set by how many pull requests they merged
- `world-map` (bloc 1920×1080, 14 s) : Animated world choropleth with country-by-country reveal, tooltip labels, and rotating globe inset — D3 Natural Earth projection

### Primitives de mouvement (26)

- `ascii-trail-reveal` (composant) : An authored S-curve sweeps through a deterministic ASCII grid, flipping cells away to reveal a labeled panel.
- `constellation-hub` (composant) : Feature nodes brighten in narration order as real-length SVG connectors draw outward from a fixed central hub, then settle into one lockup.
- `count-up` (composant) : A token-native stat counter that eases between values, counting up or down, and lands with a restrained scale pulse.
- `echo-trail` (composant) : A moving element renders with N ghosted copies of itself at t minus i times delta, opacity stepped down per ghost; one traversal, echoes collapsing into the settled elem…
- `facet-morph` (composant) : A faceted low-poly mass of 36 triangles continuously reshapes between three authored silhouettes (blob, mark, badge) with per-facet flat shading that recomputes as the v…
- `gloss-sweep` (composant) : A card lands with a restrained slam, catches one diagonal specular gloss, and holds perfectly still.
- `grade-split-reveal` (composant) : The same picture twice, one flat and one finished, with a hard edge sweeping between them.
- `grid-card-assemble` (composant) : N capability cards (thin-line icon that draws on, mono label, optional muted body) stagger-assemble into a grid or vertical list with a fade plus short slide into slot, …
- `logo-sting` (composant) : A wordmark slams into its final scale, fires one accent ring and one white impact frame, then holds completely still.
- `modal-morph` (composant) : A small card expands into a full panel, shared-element style: both layouts measured once at mount, the container morphs by transform only (never width/height tweens) whi…
- `multi-device-splay` (composant) : Phone, tablet, and desktop product mockups fan from a centered stack into a proud splayed arrangement with a subtle idle float.
- `pendulum-swing` (composant) : Content hangs from a fixed pivot and swings into rest with gravity-damped oscillation, like a hanging sign settling on its hook.
- `physical-exit` (composant) : A card exits with physical momentum in toss, drop, or slide mode, carrying acceleration and rotation through the final offscreen pose without fading.
- `radial-surround` (composant) : Labeled hairline chips assemble around a centered subject on an elliptical ring, then optionally converge inward with a subtle edge dim.
- `slit-scan-reveal` (composant) : The frame's rows sample an authored subject at offset times: a canvas painter draws row slices of one pure position function evaluated at t minus offset(row), smearing a…
- `social-proof-card` (composant) : The app-store close as one mountable scene: wordmark, five stars, a proof line, three feature icons and a CTA capsule build in a quiet stagger and hold - measured from r…
- `split-tilt-cards` (composant) : Two equal-weight cards arrive from opposite wings with mirrored rotateY book-open tilts under one shared perspective, pill badges spring-pop at each inner edge, and the …
- `stitched-text-draw` (composant) : Text drawn as thread stitches: a single-stroke display alphabet draws via attribute-driven dashoffset with stitch-tuned dash patterns, seeded angle jitter, needle-hole d…
- `stop-motion-cadence` (composant) : The stepped-time law as a demo primitive: one driver quantizes timeline time to floor(t * fps) / fps and feeds ALL motion; four token paper-cut shapes throw-and-land wit…
- `svg-stroke-trace` (composant) : An authored SVG path draws from its measured length, holds with subtle drift, and optionally fills when the path is closed.
- `swipe-rail` (composant) : A contact circle leads a horizontal card rail through a fast drag, momentum carry, and settled snap to the next card.
- `testimonial-proof-card` (composant) : A quote card whose testimonial reveals per-line through a soft mask, with an avatar disc (initials default, image slot), mono name and role, an optional company text mar…
- `trust-strip` (composant) : A monochrome trust row of wide-tracked mono wordmarks that fade in with an opacity-only left-to-right stagger, then hold dead still.
- `variable-font-flex` (composant) : A word lands while its variable-font weight and width axes flex from hairline-condensed to black-wide with per-character stagger; font-size eases inversely so the letter…
- `velocity-throw-snap` (composant) : A five-shot rail whips past on a fast decaying curve, then overshoots and snaps the selected hero shot exactly to center.
- `whiteboard-ink` (composant) : A whiteboard sketch draws one measured stroke at a time while a pen nib follows the active tip.

### Autres (24)

- `apple-money-count` (bloc 1920×1080, 5 s) : Apple-style finance counter that counts from $0 to $10,000, flashes green, and bursts money icons with sound.
- `beat-timeline` (composant) : A paused master-timeline orchestration spine that pins titled beat rows to evenly spaced named labels.
- `blue-sweater-intro-video` (bloc 1920×1080, 12 s) : Warm AI creator intro sequence that resolves into an X follow card for @_blue_sweater_.
- `camera-rig-depth-stack` (composant) : A 3D camera-rig-style card stack with depth, parallax, and focus shift.
- `flowchart` (bloc 1920×1080, 12 s) : Animated decision tree with SVG connectors, sticky-note nodes, cursor interaction, and typing correction
- `flowchart-vertical` (bloc 1440×2560 9:16, 12 s) : Portrait animated decision tree with SVG connectors, sticky-note nodes, cursor interaction, and typing correction
- `heygen-avatar-promo-card` (bloc 1080×1920 9:16, 10 s) : A portrait HeyGen offer card pairs a moving avatar mosaic with bold promotional typography and a branded callout
- `keyframe-scrub-stack` (composant) : A keyframe-sequenced stack of cards with offset timing and easing presets.
- `logo-outro` (bloc 1920×1080, 6 s) : Cinematic logo reveal with piece-by-piece assembly, glow bloom, tagline fade-in, and URL pill
- `lottie-character-walk` (bloc 1920×1080, 7.5 s) : A jointed flat character walks in on planted feet, stops and points at a card; the body acting is a Lottie file and the stage is GSAP.
- `mk-placeholder-grid` (bloc 1920×1080, 8 s) : N-up rounded-corner media grid (2-up, 3-up, 4-up, 3x2, hero plus two): per-cell inside-scale framing, staggered box-in entrance, slow settle
- `mk-progress-stat` (bloc 1920×1080, 7 s) : Big-numeral statistic with count-up, label, thin progress track filling to value/max, and caption; light and dark schemes
- `mk-specs-list` (bloc 1920×1080, 8 s) : Left-aligned specs/traits checklist over footage or a board: rows slide in staggered with an accent underline sweep; light and dark schemes
- `mk-usage-arc` (composant) : Thin circular gauge that draws on while its percentage counts up; one helper call drives both
- `onboarding-stepper-flow` (composant) : A composed onboarding flow with milestone rail, active step card, and next-action button
- `pull-to-refresh` (composant) : A mobile list pulls through nonlinear rubber-band resistance, arms at a threshold, commits to a bounded loading indicator, then snaps exactly back to rest.
- `settings-toggle-flow` (composant) : A composed settings flow with preference rows, toggle switches, and active-state feedback
- `signup-flow` (composant) : A composed signup flow with social action, email field, password field, and submit button
- `stagger-lattice` (composant) : A staggered grid reveal inspired by Anime.js v4 stagger utilities, implemented with GSAP for HyperFrames.
- `terminal-simulator` (composant) : A terminal window types commands and streams log output.
- `vpn-youtube-spot` (bloc 1920×1080, 7 s) : Snappy Apple-style YouTube insert showing a phone finding and installing a friendly VPN app with sound effects.
- `x-follow-card` (composant) : A social follow card with avatar, handle, and follower motion.
- `yt-logo-intro` (bloc 1920×1080, 6 s) : Logo stamp pops on a lined board, a kicker line gives way to the title with an accent arrow chip; seeded line distortion
- `yt-vertical-fill` (bloc 1920×1080, 8 s) : Portrait media filling a widescreen frame via blurred-scale, mirror, or copy side fills; grid texture and foreground contrast lift (images inside the block; keep live fo…

## Choisir le moteur par plan

| Le plan demande | Moteur | Pourquoi |
|---|---|---|
| Gabarit répété avec des données (titre, prix, photo, couleurs) | les deux | props Remotion ou variables HyperFrames, même job |
| Durée qui dépend des données (nombre de photos, texte) | Remotion | la durée se calcule depuis les props ; dans HyperFrames elle est fixe dans le HTML |
| Transition prête entre deux plans | HyperFrames (catalogue) ou Remotion (`@remotion/transitions`) | HyperFrames a plus de transitions toutes faites, dont des shaders ; Remotion les assemble en code |
| Effet GPU (liquide, verre, dissolution, lumière) | HyperFrames | blocs et composants WebGL/WebGPU prêts, `data-vfx-chain` |
| Flou de bougé | les deux | `data-motion-blur` (HyperFrames) ou `@remotion/motion-blur` |
| Sous-titres mot à mot sur une voix | les deux | `@remotion/captions` ou les blocs « Sous-titres » |
| Animation écrite en GSAP | HyperFrames (natif) ou Remotion (`@remotion/gsap`) | GSAP est la langue d’HyperFrames |
| Logique de composant (boucles, calculs, composants réutilisés) | Remotion | React et TypeScript |
| 3D | les deux | `@remotion/three` ou les blocs 3D d’HyperFrames |
| Contrôle du résultat image par image | les deux | rendu déterministe ; contrôle commun dans `scripts/render.mjs check` |
