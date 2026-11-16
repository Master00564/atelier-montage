#!/usr/bin/env node
// Writes docs/fonctionnalites.md: everything the two pinned engines offer, read from the
// sources of exactly those versions (never from memory), so it stays true after an upgrade.
//   node scripts/inventaire.mjs          regenerate (network; run `npm ci` in hyperframes/ first)
//   node scripts/inventaire.mjs --check  offline: fail if the doc was made for other versions
// Sources: the Remotion monorepo at tag v<version> and npm (package list, descriptions, exports);
// the installed HyperFrames CLI (--help, catalog --json) and the HyperFrames repo at tag v<version>.
import {execFile} from 'node:child_process';
import {readFileSync, writeFileSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {promisify} from 'node:util';
import {gunzipSync} from 'node:zlib';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DOC = path.join(ROOT, 'docs', 'fonctionnalites.md');
const readJson = (p) => JSON.parse(readFileSync(path.join(ROOT, p), 'utf8'));

export function pinnedVersions() {
  return {
    remotion: readJson('remotion/package.json').dependencies.remotion,
    hyperframes: readJson('hyperframes/package.json').dependencies.hyperframes,
  };
}
export const versionLine = (v) => `Versions : Remotion ${v.remotion} · HyperFrames ${v.hyperframes}`;

// One line per package: when it helps a 9:16 product reel. A package missing here is still
// listed (with its npm description) and counted as "à évaluer", so nothing is silently left out.
const REEL_NOTES = {
  remotion: 'Le cœur : compositions, Sequence/Series, interpolate, spring, Easing, Img, staticFile. Toujours.',
  '@remotion/cli': 'La commande `remotion render/studio/still`. Toujours (le workflow s’en sert).',
  '@remotion/transitions': 'Enchaîner deux plans (fondu, glissé, volet, zoom…) avec TransitionSeries. Entre chaque plan produit.',
  '@remotion/motion-blur': 'Flou de bougé (Trail, CameraMotionBlur) sur un mouvement rapide : whip, titre qui file.',
  '@remotion/light-leaks': 'Fuites de lumière par-dessus l’image : passage chaleureux entre deux plans de luminaire.',
  '@remotion/starburst': 'Rayons en étoile : fond d’une carte de prix ou d’accroche, avec retenue.',
  '@remotion/effects': 'Effets appliqués aux composants canvas : grain, déformation, look.',
  '@remotion/noise': 'Bruit déterministe (Perlin/simplex) : flottement naturel d’un objet, grain animé, particules.',
  '@remotion/paths': 'Tracer et animer des chemins SVG (evolvePath…) : dessiner un filet, une flèche, un contour de produit.',
  '@remotion/shapes': 'Formes SVG prêtes (cercle, rectangle, triangle, étoile, polygone, pie) pour pastilles et badges.',
  '@remotion/rounded-text-box': 'Bloc de texte multiligne aux coins arrondis façon TikTok : sous-titres, bulles de prix.',
  '@remotion/rough-notation': 'Annotations dessinées à la main (souligner, entourer) : mettre en valeur un détail.',
  '@remotion/layout-utils': 'Mesurer et ajuster le texte (fitText, measureText) : un titre long tient toujours dans la largeur.',
  '@remotion/animation-utils': 'Interpoler des styles CSS et des transformations : animations plus courtes à écrire.',
  '@remotion/gsap': 'Piloter une timeline GSAP image par image dans Remotion : réutiliser une animation écrite pour HyperFrames.',
  '@remotion/google-fonts': 'Charger une police Google par son nom, sans fichier : titres et textes.',
  '@remotion/fonts': 'Charger un fichier de police local (police de marque fournie par la boutique).',
  '@remotion/media': 'Audio et Video nouvelle génération (WebCodecs) : musique, clips produit.',
  '@remotion/media-utils': 'Lire durée, dimensions, forme d’onde audio : caler les plans sur la musique, visualiseur.',
  '@remotion/sfx': 'Bibliothèque de bruitages : un « whoosh » sur une transition, un « pop » sur un prix.',
  '@remotion/captions': 'Structures et découpage de sous-titres mot à mot : texte qui suit une voix off.',
  '@remotion/openai-whisper': 'Convertir une transcription Whisper (API OpenAI) en sous-titres Remotion.',
  '@remotion/install-whisper-cpp': 'Transcrire localement avec Whisper.cpp pour générer des sous-titres.',
  '@remotion/whisper-web': 'Transcription Whisper dans le navigateur (WASM).',
  '@remotion/whisper-webgpu': 'Transcription Whisper dans le navigateur (WebGPU).',
  '@remotion/elevenlabs': 'Exploiter une voix off ElevenLabs (horodatage) : service payant, hors de notre usage gratuit.',
  '@remotion/lottie': 'Jouer une animation Lottie (icônes animées, pictos) image par image.',
  '@remotion/rive': 'Jouer une animation Rive.',
  '@remotion/gif': 'Insérer un GIF synchronisé à la vidéo.',
  '@remotion/animated-emoji': 'Emojis animés Google en composants.',
  '@remotion/three': 'Scène 3D React Three Fiber : produit en 3D si on a un modèle.',
  '@remotion/skia': 'Dessin React Native Skia : effets graphiques avancés.',
  '@remotion/svg-3d-engine': 'Extrusion 3D de formes SVG : logo ou chiffre en relief.',
  '@remotion/maptiler': 'Cartes MapTiler : sans usage pour une fiche produit.',
  '@remotion/mac-cursors': 'Curseurs macOS : démos d’écran, sans usage pour un luminaire.',
  '@remotion/tailwind': 'Écrire le style en Tailwind v3.',
  '@remotion/tailwind-v4': 'Écrire le style en Tailwind v4.',
  '@remotion/enable-scss': 'Écrire le style en SCSS.',
  '@remotion/preload': 'Précharger images, vidéos, polices avant leur apparition (aperçu fluide).',
  '@remotion/zod-types': 'Schéma Zod des props : contrôles éditables dans le Studio.',
  '@remotion/zod-types-v3': 'Variante Zod 3.22.3 de zod-types.',
  '@remotion/player': 'Lire une composition dans une page web (aperçu interactif), pas pour le rendu.',
  '@remotion/studio': 'API du Studio (aperçu local).',
  '@remotion/studio-server': 'Serveur du Studio.',
  '@remotion/studio-shared': 'Interne au Studio.',
  '@remotion/studio-protocol': 'Envoyer des éléments au Studio.',
  '@remotion/renderer': 'Rendu depuis Node (utilisé par la CLI).',
  '@remotion/bundler': 'Empaquetage Webpack (utilisé par la CLI).',
  '@remotion/babel-loader': 'Chargeur Babel pour le bundler.',
  '@remotion/browser-bundler': 'Compiler un projet Remotion dans le navigateur.',
  '@remotion/web-renderer': 'Rendu dans le navigateur, sans serveur.',
  '@remotion/webcodecs': 'Conversion de médias dans le navigateur.',
  '@remotion/media-parser': 'Lire les métadonnées d’un fichier vidéo.',
  '@remotion/video-matting': 'Détourer une vidéo (sujet sur fond transparent) dans le navigateur.',
  '@remotion/streaming': 'Interne : échanges de données entre programmes.',
  '@remotion/timeline-utils': 'Interne : rendu des timelines.',
  '@remotion/sdk': 'Expérimental : construire un éditeur.',
  '@remotion/design': 'Système de design de Remotion (interne à leurs outils).',
  '@remotion/lambda': 'Rendu sur AWS Lambda : payant, hors de notre usage.',
  '@remotion/lambda-client': 'Client Lambda : payant, hors de notre usage.',
  '@remotion/cloudrun': 'Rendu sur Google Cloud Run : payant, hors de notre usage.',
  '@remotion/vercel': 'Rendu sur Vercel Sandbox : payant, hors de notre usage.',
  '@remotion/licensing': 'Gestion de licence Remotion.pro (gratuit jusqu’à 3 personnes).',
  '@remotion/codemods': 'Migrations de code entre versions.',
  '@remotion/eslint-config': 'Règles ESLint (≤ 8).',
  '@remotion/eslint-config-flat': 'Règles ESLint (≥ 9).',
  '@remotion/eslint-plugin': 'Règles ESLint propres à Remotion.',
  '@remotion/promo-pages': 'Pages promotionnelles de Remotion (interne).',
  'create-video': 'Créer un projet depuis un modèle (`npx create-video`).',
};
// Packages whose exported functions and components are listed one by one.
const TOOLBOX = [
  '@remotion/transitions', '@remotion/motion-blur', '@remotion/light-leaks', '@remotion/starburst', '@remotion/effects',
  '@remotion/noise', '@remotion/paths', '@remotion/shapes', '@remotion/rounded-text-box', '@remotion/rough-notation',
  '@remotion/layout-utils', '@remotion/animation-utils', '@remotion/gsap', '@remotion/media', '@remotion/media-utils',
  '@remotion/sfx', '@remotion/captions', '@remotion/lottie', '@remotion/three', '@remotion/svg-3d-engine', '@remotion/fonts',
];

// Registry families, first matching tag wins.
const FAMILIES = [
  ['Transitions', ['transition', 'transition-primitive', 'wipe']],
  ['Sous-titres', ['captions', 'caption-style']],
  ['Texte et titres', ['typography', 'text', 'title-card', 'text-effects', 'handwritten']],
  ['Habillage (bandeaux, réseaux, annotations)', ['overlay', 'lower-third', 'social', 'annotation', 'cursor']],
  ['Produit et maquettes d’interface', ['product-demo', 'mock-ui', 'ui-props', 'chat', 'code', 'developer', 'ad-template']],
  ['Images, galeries, carrousels, vidéo', ['images', 'gallery', 'carousel', 'video-primitive']],
  ['Fonds, textures, lumière', ['background', 'texture', 'gradient', 'light', 'glow', 'particles']],
  ['Shaders et effets GPU', ['webgpu', 'webgpu-shader', 'shader', 'webgl', 'effect', 'effects', 'motion-blur', 'html-in-canvas']],
  ['3D et caméra', ['3d', '3d-motion', 'camera', 'orbit', 'object']],
  ['Données et cartes', ['data', 'chart', 'map']],
  ['Primitives de mouvement', ['motion-primitive', 'reveal', 'morph', 'path']],
];

// ---------- helpers ----------
const UA = {'user-agent': 'atelier-video-inventaire', ...(process.env.GITHUB_TOKEN ? {authorization: `Bearer ${process.env.GITHUB_TOKEN}`} : {})};
async function get(url, as = 'json') {
  for (let attempt = 1; ; attempt++) {
    const res = await fetch(url, {headers: url.includes('api.github.com') ? UA : {'user-agent': UA['user-agent']}}).catch((e) => ({ok: false, status: e.message}));
    if (res.ok) return as === 'json' ? res.json() : as === 'text' ? res.text() : Buffer.from(await res.arrayBuffer());
    if (res.status === 404) return null;
    if (attempt === 3) throw new Error(`${url}: ${res.status}`);
    await new Promise((r) => setTimeout(r, 2000 * attempt));
  }
}
async function pool(items, size, fn) {
  const out = new Array(items.length);
  let i = 0;
  await Promise.all(Array.from({length: size}, async () => {
    while (i < items.length) {
      const k = i++;
      out[k] = await fn(items[k]);
    }
  }));
  return out;
}
const oneLine = (s, max = 170) => {
  const t = String(s ?? '').replace(/\s+/g, ' ').trim();
  const first = t.match(/^.*?[.!?](\s|$)/)?.[0].trim() ?? t;
  return first.length > max ? `${first.slice(0, max - 1)}…` : first;
};

function untar(buf) {
  const files = new Map();
  for (let off = 0; off + 512 <= buf.length; ) {
    const field = (a, b) => buf.toString('utf8', off + a, off + b).replace(/\0.*$/s, '');
    const name = field(0, 100);
    if (!name) break;
    const size = parseInt(field(124, 136).trim() || '0', 8);
    const prefix = field(345, 500);
    const type = buf[off + 156];
    if (type === 48 || type === 0) files.set(prefix ? `${prefix}/${name}` : name, buf.subarray(off + 512, off + 512 + size));
    off += 512 + Math.ceil(size / 512) * 512;
  }
  return files;
}
function typesEntry(m) {
  let e = m.types || m.typings || m.exports?.['.']?.types;
  if (!e && m.exports?.['.']) {
    const x = m.exports['.'];
    e = x.import?.types || x.require?.types || x.default?.types;
  }
  return path.posix.normalize(`package/${e || 'dist/index.d.ts'}`);
}
// Runtime names exported by a .d.ts entry, following `export * from` a few levels.
function namedExports(files, entry) {
  const names = new Set();
  const seen = new Set();
  const resolve = (from, rel) => {
    const base = path.posix.join(path.posix.dirname(from), rel).replace(/\.js$/, '');
    return [`${base}.d.ts`, `${base}/index.d.ts`, base].find((f) => files.has(f));
  };
  const visit = (file, depth) => {
    if (!file || seen.has(file) || depth > 4) return;
    seen.add(file);
    const src = files.get(file)?.toString('utf8') ?? '';
    for (const m of src.matchAll(/export\s+(?:declare\s+)?(?:const|function|class|let|enum)\s+([A-Za-z_$][\w$]*)/g)) names.add(m[1]);
    for (const m of src.matchAll(/export\s+(type\s+)?\{([^}]*)\}/g)) {
      if (m[1]) continue;
      for (const part of m[2].split(',')) {
        const p = part.trim();
        if (!p || p.startsWith('type ')) continue;
        const n = p.split(/\s+as\s+/).pop().trim();
        if (n && n !== 'default' && /^[A-Za-z_$][\w$]*$/.test(n)) names.add(n);
      }
    }
    for (const m of src.matchAll(/export\s+\*\s+from\s+['"](\.[^'"]+)['"]/g)) visit(resolve(file, m[1]), depth + 1);
  };
  visit(entry, 0);
  return [...names].sort((a, b) => a.localeCompare(b));
}
const run = promisify(execFile);
async function cli(args, cwd) {
  const bin = path.join(ROOT, 'hyperframes', 'node_modules', 'hyperframes', 'bin', 'hyperframes.mjs');
  const env = {...process.env, HYPERFRAMES_NO_TELEMETRY: '1', DO_NOT_TRACK: '1', HYPERFRAMES_NO_UPDATE_CHECK: '1', HYPERFRAMES_SKIP_SKILLS: '1', HYPERFRAMES_NO_AUTO_INSTALL: '1', NO_COLOR: '1', CI: '1'};
  try {
    const {stdout, stderr} = await run(process.execPath, [bin, ...args], {cwd: cwd ?? ROOT, env, maxBuffer: 64 * 1024 * 1024, timeout: 300_000});
    return (stdout + stderr).replace(/\x1b\[[0-9;]*m/g, '');
  } catch (e) {
    return `${e.stdout ?? ''}${e.stderr ?? ''}`.replace(/\x1b\[[0-9;]*m/g, '');
  }
}

// ---------- Remotion ----------
async function remotion(v) {
  const tag = `v${v}`;
  const root = await get(`https://api.github.com/repos/remotion-dev/remotion/git/trees/${tag}`);
  const pk = await get(root.tree.find((t) => t.path === 'packages').url);
  const dirs = pk.tree.filter((t) => t.type === 'tree').map((t) => t.path);
  const rows = (
    await pool(dirs, 12, async (d) => {
      const p = await get(`https://raw.githubusercontent.com/remotion-dev/remotion/${tag}/packages/${d}/package.json`);
      if (!p?.name) return null;
      if (p.private) return {name: p.name, private: true, description: p.description};
      const m = await get(`https://registry.npmjs.org/${p.name.replace('/', '%2F')}/${v}`);
      return {name: p.name, npm: !!m, description: m?.description || p.description || '', manifest: m};
    })
  ).filter(Boolean);
  rows.sort((a, b) => a.name.localeCompare(b.name));
  const published = rows.filter((r) => r.npm && !/compositor-/.test(r.name));
  const binaries = rows.filter((r) => r.npm && /compositor-/.test(r.name));
  const templates = rows.filter((r) => r.private && /^template-/.test(r.name));
  const toolbox = await pool(TOOLBOX.filter((n) => published.some((r) => r.name === n)), 6, async (name) => {
    const m = published.find((r) => r.name === name).manifest;
    const files = untar(gunzipSync(await get(m.dist.tarball, 'buffer')));
    const subpaths = Object.keys(m.exports ?? {}).filter((k) => k !== '.' && k !== './package.json').map((k) => k.slice(2));
    return {name, exports: namedExports(files, typesEntry(m)), subpaths};
  });
  return {published, binaries, templates, toolbox};
}

// ---------- HyperFrames ----------
async function hyperframes(v) {
  const tag = `v${v}`;
  const help = await cli(['--help']);
  const installed = help.match(/hyperframes v([\d.]+)/)?.[1];
  if (installed !== v) throw new Error(`installed HyperFrames is ${installed}, pinned is ${v}: run npm ci in hyperframes/`);
  const groups = [];
  let group = null;
  for (const line of help.split('\n')) {
    if (/^Examples:/.test(line)) break;
    const g = line.match(/^([A-Z][A-Za-z &]+):\s*$/);
    if (g) groups.push((group = {name: g[1], commands: []}));
    const c = line.match(/^ {2}([a-z][a-z-]*)\s{2,}(.+)$/);
    if (c && group) group.commands.push({name: c[1], summary: c[2].trim()});
  }
  const parseHelp = (name, text) => {
    if (!/USAGE/.test(text)) throw new Error(`"hyperframes ${name} --help" gave no USAGE section: ${text.slice(0, 200)}`);
    const flags = [...new Set([...text.matchAll(/(?:^|\s)(--[a-z][a-z0-9-]*)/gm)].map((m) => m[1]))].filter((f) => f !== '--help');
    const blocks = text.split(/\n(?=[A-Z][A-Z ]+\n)/);
    const section = (title) => blocks.find((b) => b.trim().startsWith(title)) ?? '';
    const sub = [...section('COMMANDS').matchAll(/^[ \t]{2,}([a-z][a-z0-9-]*)[ \t]{2,}(.+)$/gm)].map((m) => ({name: m[1], summary: m[2].trim()}));
    const args = [...section('ARGUMENTS').matchAll(/^[ \t]{2,}([A-Z][A-Z0-9_]*)[ \t]{2,}(.+)$/gm)].map((m) => `${m[1]} (${m[2].trim()})`);
    return {flags, sub, args};
  };
  const all = groups.flatMap((g) => g.commands);
  await pool(all, 3, async (c) => Object.assign(c, parseHelp(c.name, await cli([c.name, '--help']))));
  const catalog = JSON.parse(await cli(['catalog', '--json'], path.join(ROOT, 'hyperframes', 'promo')));
  const registry = await get(`https://raw.githubusercontent.com/heygen-com/hyperframes/${tag}/registry/registry.json`);
  const examples = (registry?.items ?? []).filter((i) => i.type === 'hyperframes:example').map((i) => i.name);
  // Every data-* attribute named in the docs of this version, with the first table description found.
  const tree = await get(`https://api.github.com/repos/heygen-com/hyperframes/git/trees/${tag}?recursive=1`);
  const docs = tree.tree.filter((t) => t.type === 'blob' && /^docs\/(concepts|guides|reference|packages|sdk)\/.+\.mdx$/.test(t.path)).map((t) => t.path);
  const attrs = new Map();
  let adapters = '';
  await pool(docs, 12, async (p) => {
    const text = (await get(`https://raw.githubusercontent.com/heygen-com/hyperframes/${tag}/${p}`, 'text')) ?? '';
    if (p.endsWith('frame-adapters.mdx')) adapters = text.split('\n').find((l) => /already seeks/.test(l)) ?? '';
    for (const m of text.matchAll(/^\|\s*`(data-[a-z0-9-]+)(?:="[^"]*")?`[^|]*\|\s*(.*?)\s*\|\s*(.*?)\s*\|/gm)) {
      const desc = m[3] && !/^-+$/.test(m[3]) ? m[3] : m[2];
      if (!attrs.has(m[1]) || !attrs.get(m[1]).desc) attrs.set(m[1], {doc: p, desc: oneLine(desc, 200)});
    }
    // Attributes only named in prose: keep the sentence that names them.
    for (const line of text.split('\n'))
      for (const m of line.matchAll(/`(data-[a-z0-9-]+)/g)) {
        const prose = /^\s*([-*]\s+)?[A-Za-z`]/.test(line) ? oneLine(line.replace(/^\s*[-*]\s+/, ''), 200) : '';
        if (!attrs.has(m[1])) attrs.set(m[1], {doc: p, desc: prose});
        else if (!attrs.get(m[1]).desc && prose) attrs.get(m[1]).desc = prose;
      }
  });
  return {installed, groups, catalog, examples, attrs, adapters, docsCount: docs.length};
}

function familyOf(item) {
  for (const [name, tags] of FAMILIES) if (item.tags?.some((t) => tags.includes(t))) return name;
  return 'Autres';
}

function render(v, rm, hf) {
  const L = [];
  const p = (...x) => L.push(...x);
  const missing = rm.published.filter((r) => !REEL_NOTES[r.name]);
  p(
    '# Fonctionnalités des deux moteurs',
    '',
    `> Généré par \`node scripts/inventaire.mjs\` le ${new Date().toISOString().slice(0, 10)}. Ne pas modifier à la main : relancer le script après tout changement de version.`,
    `> ${versionLine(v)}`,
    '',
    'Sources lues pour ces versions exactes : dépôt Remotion au tag `v' + v.remotion + '` (liste des paquets) et npm (descriptions, exports) ; CLI HyperFrames installée (`--help` de chaque commande, `catalog --json`) et dépôt HyperFrames au tag `v' + v.hyperframes + '` (exemples, attributs `data-*` de ' + hf.docsCount + ' pages de doc).',
    '',
    '## Sommaire',
    '',
    '1. [Remotion : paquets](#remotion--paquets)',
    '2. [Remotion : boîte à outils, fonction par fonction](#remotion--boîte-à-outils-fonction-par-fonction)',
    '3. [HyperFrames : commandes](#hyperframes--commandes)',
    '4. [HyperFrames : attributs, animation, effets](#hyperframes--attributs-animation-effets)',
    '5. [HyperFrames : catalogue (blocs et composants)](#hyperframes--catalogue-blocs-et-composants)',
    '6. [Choisir le moteur par plan](#choisir-le-moteur-par-plan)',
    '',
    '## Remotion : paquets',
    '',
    `${rm.published.length} paquets publiés en ${v.remotion}${missing.length ? ` (${missing.length} sans note d’usage : « à évaluer »)` : ''}. Installés dans ce dépôt : ceux de \`remotion/package.json\` ; ajouter un paquet = \`npm install --save-exact <nom>@${v.remotion}\` dans \`remotion/\`.`,
    '',
    '| Paquet | Ce qu’il fait (npm) | Dans un reel 9:16 |',
    '|---|---|---|',
    ...rm.published.map((r) => `| \`${r.name}\` | ${oneLine(r.description, 110).replace(/\|/g, '\\|')} | ${REEL_NOTES[r.name] ?? 'à évaluer'} |`),
    '',
    `Binaires du moteur (installés seuls selon la machine) : ${rm.binaries.map((r) => `\`${r.name}\``).join(', ')}.`,
    '',
    `Modèles de projet du dépôt (non publiés comme paquets, servent à \`npx create-video\`) : ${rm.templates.map((r) => `\`${r.name.replace(/^template-/, '')}\``).join(', ')}.`,
    '',
    '## Remotion : boîte à outils, fonction par fonction',
    '',
    'Noms exportés lus dans les types publiés de chaque paquet (sans les types seuls).',
    '',
  );
  for (const t of rm.toolbox) {
    p(`### \`${t.name}\``, '');
    if (t.subpaths.length) p(`Sous-chemins importables (\`${t.name}/<nom>\`) : ${t.subpaths.map((s) => `\`${s}\``).join(', ')}.`, '');
    p(t.exports.length ? `Exports : ${t.exports.map((e) => `\`${e}\``).join(', ')}.` : 'Exports : aucun nom lisible dans les types (voir la doc du paquet).', '');
  }
  p('## HyperFrames : commandes', '', `CLI \`hyperframes\` ${hf.installed}, lue par \`--help\`. Commandes à ne pas utiliser ici (payantes ou compte HeyGen) : \`auth\`, \`billing\`, \`cloud\`, \`templates\`, \`publish\`, \`reverse\` ; \`lambda\` et \`cloudrun\` facturent le cloud.`, '');
  for (const g of hf.groups) {
    p(`### ${g.name}`, '');
    for (const c of g.commands) {
      p(`- **\`${c.name}\`** : ${c.summary}${c.args?.length ? `. Arguments : ${c.args.join(' ; ')}` : ''}${c.flags?.length ? `. Options : ${c.flags.map((f) => `\`${f}\``).join(' ')}` : ''}`);
      for (const s of c.sub ?? []) p(`  - \`${c.name} ${s.name}\` : ${s.summary}`);
    }
    p('');
  }
  p(
    '## HyperFrames : attributs, animation, effets',
    '',
    `Animation : ${hf.adapters.trim() || 'non trouvé dans docs/concepts/frame-adapters.mdx'}`,
    '',
    `Exemples de départ (\`hyperframes init --example <nom>\`) : ${hf.examples.map((e) => `\`${e}\``).join(', ')}.`,
    '',
    `Attributs \`data-*\` cités dans la documentation de la version (${hf.attrs.size}) :`,
    '',
    '| Attribut | Rôle | Page |',
    '|---|---|---|',
    ...[...hf.attrs.entries()].sort(([a], [b]) => a.localeCompare(b)).map(([k, x]) => `| \`${k}\` | ${(x.desc || '—').replace(/\|/g, '\\|')} | ${x.doc.replace(/^docs\//, '')} |`),
    '',
  );
  const byFamily = new Map();
  for (const item of hf.catalog) {
    const f = familyOf(item);
    if (!byFamily.has(f)) byFamily.set(f, []);
    byFamily.get(f).push(item);
  }
  const order = [...FAMILIES.map(([n]) => n), 'Autres'].filter((n) => byFamily.has(n));
  const vertical = hf.catalog.filter((i) => i.dimensions && i.dimensions.height > i.dimensions.width).length;
  p(
    '## HyperFrames : catalogue (blocs et composants)',
    '',
    `${hf.catalog.length} éléments (${hf.catalog.filter((i) => i.type === 'block').length} blocs = scènes complètes, ${hf.catalog.filter((i) => i.type === 'component').length} composants = effets à poser dans une scène), installables par \`npx hyperframes add <nom>\` dans \`hyperframes/<projet>/\`. Classés par famille (premier mot-clé reconnu). « 9:16 » = bloc déjà vertical (${vertical}).`,
    '',
  );
  for (const f of order) {
    const items = byFamily.get(f).sort((a, b) => a.name.localeCompare(b.name));
    p(`### ${f} (${items.length})`, '');
    for (const i of items) {
      const d = i.dimensions;
      const meta = i.type === 'block' ? `bloc${d ? ` ${d.width}×${d.height}` : ''}${d && d.height > d.width ? ' 9:16' : ''}${i.duration ? `, ${i.duration} s` : ''}` : 'composant';
      p(`- \`${i.name}\` (${meta}) : ${oneLine(i.description || i.title).replace(/\|/g, '\\|')}`);
    }
    p('');
  }
  p(
    '## Choisir le moteur par plan',
    '',
    '| Le plan demande | Moteur | Pourquoi |',
    '|---|---|---|',
    '| Gabarit répété avec des données (titre, prix, photo, couleurs) | les deux | props Remotion ou variables HyperFrames, même job |',
    '| Durée qui dépend des données (nombre de photos, texte) | Remotion | la durée se calcule depuis les props ; dans HyperFrames elle est fixe dans le HTML |',
    '| Transition prête entre deux plans | HyperFrames (catalogue) ou Remotion (`@remotion/transitions`) | HyperFrames a plus de transitions toutes faites, dont des shaders ; Remotion les assemble en code |',
    '| Effet GPU (liquide, verre, dissolution, lumière) | HyperFrames | blocs et composants WebGL/WebGPU prêts, `data-vfx-chain` |',
    '| Flou de bougé | les deux | `data-motion-blur` (HyperFrames) ou `@remotion/motion-blur` |',
    '| Sous-titres mot à mot sur une voix | les deux | `@remotion/captions` ou les blocs « Sous-titres » |',
    '| Animation écrite en GSAP | HyperFrames (natif) ou Remotion (`@remotion/gsap`) | GSAP est la langue d’HyperFrames |',
    '| Logique de composant (boucles, calculs, composants réutilisés) | Remotion | React et TypeScript |',
    '| 3D | les deux | `@remotion/three` ou les blocs 3D d’HyperFrames |',
    '| Contrôle du résultat image par image | les deux | rendu déterministe ; contrôle commun dans `scripts/render.mjs check` |',
    '',
  );
  return L.join('\n');
}

export function checkDoc() {
  const v = pinnedVersions();
  const text = readFileSync(DOC, 'utf8');
  if (!text.includes(versionLine(v))) throw new Error(`docs/fonctionnalites.md was not generated for "${versionLine(v)}": run node scripts/inventaire.mjs`);
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  try {
    if (process.argv.includes('--check')) {
      checkDoc();
      console.log('docs/fonctionnalites.md matches the pinned versions');
    } else {
      const v = pinnedVersions();
      const [rm, hf] = await Promise.all([remotion(v.remotion), hyperframes(v.hyperframes)]);
      writeFileSync(DOC, render(v, rm, hf));
      const missing = rm.published.filter((r) => !REEL_NOTES[r.name]).map((r) => r.name);
      console.log(`written ${path.relative(ROOT, DOC)}: ${rm.published.length} Remotion packages, ${hf.groups.flatMap((g) => g.commands).length} HyperFrames commands, ${hf.catalog.length} registry items, ${hf.attrs.size} data-* attributes`);
      if (missing.length) console.log(`packages without a reel note (listed as "à évaluer"): ${missing.join(', ')}`);
    }
  } catch (e) {
    console.error(`FAILED: ${e.message}`);
    process.exit(1);
  }
}
