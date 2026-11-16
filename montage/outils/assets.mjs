// Stage the files a montage project declares, before any check or render.
//
//   node montage/outils/assets.mjs montage/projets/<name>
//
// montage.json lists them: {"assets": {"photo.jpg": "https://…", "pad.m4a": "library/audio/soft-pad.m4a"}}.
// An https source is downloaded, a repo path (library/, jobs/) is copied; each lands in
// <project>/assets/<name>. Files already committed in <project>/assets/ need no entry (the sound effects:
// earshot bank takes copied there by the skill's scripts/place_effets.py). HyperFrames
// forbids network media at render time, so every picture, font and sound goes through here.
// "detourages": {"lampe.png": "photo-1.jpg"} asks for the subject of a staged photo cut out on a
// transparent ground (assets/lampe.png); {"lampe.png": {"photo": "photo-1.jpg", "zone": [x0, y0, x1, y1]}}
// cuts only inside that box of photo pixels (a small subject in a wide room).
// "plaques": {"fond.jpg": "lampe.png"} asks for the photo of that cut-out with the subject removed and
// the hole filled (assets/fond.jpg), so the cut-out can move over its own background.
// The pairs are written to out/cutouts.json for scripts/detourer.py, and the step output
// "detourage" tells the workflow to run it.
import { appendFile, copyFile, mkdir, readFile, writeFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import path from 'node:path';

const NOM = /^[a-z0-9][a-z0-9._-]{0,80}$/i;
const DEPOT = ['library/', 'jobs/'];
const MAX = 40 * 1024 * 1024;

function fail(message) {
  console.log(`::error::FAILED: ${message}`);
  process.exit(1);
}

const projet = process.argv[2];
if (!projet || !existsSync(path.join(projet, 'montage.json'))) fail(`no montage.json in ${projet}`);
const manifeste = JSON.parse(await readFile(path.join(projet, 'montage.json'), 'utf8'));
const assets = manifeste.assets ?? {};
await mkdir(path.join(projet, 'assets'), { recursive: true });

await Promise.all(
  Object.entries(assets).map(async ([nom, source]) => {
    if (!NOM.test(nom)) fail(`asset name "${nom}": letters, digits, dot, dash, underscore only`);
    const cible = path.join(projet, 'assets', nom);
    if (typeof source === 'string' && source.startsWith('https://')) {
      let dernier = '';
      for (let essai = 1; essai <= 3; essai++) {
        try {
          const reponse = await fetch(source, { redirect: 'follow', signal: AbortSignal.timeout(60000) });
          if (!reponse.ok) throw new Error(`HTTP ${reponse.status}`);
          const octets = Buffer.from(await reponse.arrayBuffer());
          if (!octets.length || octets.length > MAX) throw new Error(`${octets.length} bytes`);
          await writeFile(cible, octets);
          console.log(`${nom}: ${octets.length} bytes downloaded`);
          return;
        } catch (e) {
          dernier = String(e.message ?? e);
          await new Promise((r) => setTimeout(r, essai * 2000));
        }
      }
      fail(`asset "${nom}" could not be downloaded (${dernier}): ${source}`);
    } else if (typeof source === 'string' && DEPOT.some((d) => source.startsWith(d)) && !source.includes('..')) {
      if (!existsSync(source)) fail(`asset "${nom}": ${source} is not in the repo`);
      await copyFile(source, cible);
      console.log(`${nom}: copied from ${source}`);
    } else {
      fail(`asset "${nom}": source must be https://… or a path under ${DEPOT.join(', ')}`);
    }
  }),
);
console.log(`${Object.keys(assets).length} assets staged in ${projet}/assets`);

const paires = Object.entries(manifeste.detourages ?? {}).map(([png, source]) => {
  if (!NOM.test(png) || !png.toLowerCase().endsWith('.png')) fail(`cut-out name "${png}": a flat .png name`);
  const { photo, zone } = typeof source === 'string' ? { photo: source } : source ?? {};
  if (typeof photo !== 'string' || !existsSync(path.join(projet, 'assets', photo))) fail(`cut-out "${png}": assets/${photo} is not staged`);
  if (zone !== undefined && !(Array.isArray(zone) && zone.length === 4 && zone.every(Number.isInteger)))
    fail(`cut-out "${png}": zone must be [x0, y0, x1, y1] in photo pixels`);
  return { from: path.join(projet, 'assets', photo), to: path.join(projet, 'assets', png), ...(zone && { zone }) };
});
for (const [plaque, png] of Object.entries(manifeste.plaques ?? {})) {
  if (!NOM.test(plaque) || !/\.(jpg|png)$/i.test(plaque)) fail(`plate name "${plaque}": a flat .jpg or .png name`);
  const paire = paires.find((p) => path.basename(p.to) === png);
  if (!paire) fail(`plate "${plaque}": "${png}" is not one of the "detourages"`);
  paire.plate = path.join(projet, 'assets', plaque);
}
if (paires.length) {
  await mkdir('out', { recursive: true });
  await writeFile(path.join('out', 'cutouts.json'), JSON.stringify(paires));
  console.log(`${paires.length} cut-outs asked`);
}
if (process.env.GITHUB_OUTPUT) await appendFile(process.env.GITHUB_OUTPUT, `detourage=${paires.length > 0}
`);
