#!/usr/bin/env node
// One render job, three steps, used by .github/workflows/render.yml (and runnable by hand):
//   node scripts/render.mjs prepare   job from $JOB_FILE (repo path) or $JOB_JSON (inline JSON):
//                                     validate it, stage its assets, write out/job.json + out/props.json
//   node scripts/render.mjs render    run the engine named by the job
//   node scripts/render.mjs check     probe the MP4, enforce the job's expectations, write out/<name>.json
// Any failure exits 1 with a line starting "FAILED:".
import {spawnSync} from 'node:child_process';
import {copyFileSync, cpSync, existsSync, mkdirSync, readFileSync, rmSync, statSync, writeFileSync, appendFileSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

export const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const OUT = path.join(ROOT, 'out');
const NAME_RE = /^[A-Za-z0-9][A-Za-z0-9._-]{0,80}$/;
const MAX_ASSET_BYTES = 300 * 1024 * 1024;

// Where each engine keeps its projects and serves staged files from.
export const ENGINES = {
  remotion: {
    composition: /^[A-Za-z][A-Za-z0-9-]{0,60}$/, // a <Composition id> in remotion/src/Root.tsx
    projectDir: () => path.join(ROOT, 'remotion'),
    stageDir: () => path.join(ROOT, 'remotion', 'public', 'assets', 'job'),
  },
  hyperframes: {
    composition: /^[a-z0-9][a-z0-9-]{0,60}$/, // a folder hyperframes/<name>/ with an index.html
    projectDir: (c) => path.join(ROOT, 'hyperframes', c),
    stageDir: (c) => path.join(ROOT, 'hyperframes', c, 'assets', 'job'),
  },
};
const JOB_KEYS = ['engine', 'composition', 'output', 'props', 'assets', 'cutouts', 'expect', 'note', 'theme'];
const EXPECT_KEYS = ['width', 'height', 'fps', 'minSeconds', 'maxSeconds', 'audio'];

const fail = (msg) => {
  throw new Error(msg);
};
const isObject = (v) => v !== null && typeof v === 'object' && !Array.isArray(v);

// Pure validation: returns the normalised job or throws with every problem found.
export function validateJob(job) {
  const errors = [];
  if (!isObject(job)) fail('the job must be a JSON object');
  for (const k of Object.keys(job)) if (!JOB_KEYS.includes(k)) errors.push(`unknown key "${k}" (allowed: ${JOB_KEYS.join(', ')})`);
  const engine = ENGINES[job.engine];
  if (!engine) errors.push(`engine must be one of ${Object.keys(ENGINES).join(', ')}`);
  if (typeof job.composition !== 'string' || (engine && !engine.composition.test(job.composition)))
    errors.push(`composition "${job.composition}" is not a valid ${job.engine} composition name`);
  if (typeof job.output !== 'string' || !/^[A-Za-z0-9][A-Za-z0-9._-]{0,80}\.mp4$/.test(job.output))
    errors.push('output must be a plain file name ending in .mp4 (letters, digits, . _ -)');
  const props = job.props ?? {};
  if (!isObject(props)) errors.push('props must be an object');
  const assets = job.assets ?? {};
  if (!isObject(assets)) errors.push('assets must be an object {fileName: https URL, or a path under library/ or jobs/}');
  else
    for (const [name, src] of Object.entries(assets)) {
      if (!NAME_RE.test(name)) errors.push(`asset name "${name}" must be a plain file name`);
      if (typeof src !== 'string' || !(/^https:\/\//.test(src) || isRepoFile(src)))
        errors.push(`asset "${name}" must be an https:// URL or a path under library/ or jobs/`);
    }
  // cutouts: {"lamp.png": "photo.jpg"} = a transparent PNG of the product, cut out of a staged photo.
  const cutouts = job.cutouts ?? {};
  if (!isObject(cutouts)) errors.push('cutouts must be an object {fileName.png: asset name}');
  else
    for (const [name, from] of Object.entries(cutouts)) {
      if (!NAME_RE.test(name) || !name.endsWith('.png')) errors.push(`cutout "${name}" must be a plain file name ending in .png`);
      if (isObject(assets) && name in assets) errors.push(`cutout "${name}" has the name of an asset`);
      if (!isObject(assets) || !(from in assets)) errors.push(`cutout "${name}" must name an asset of this job, not "${from}"`);
    }
  if (job.theme !== undefined && !(isObject(job.theme) && Array.isArray(job.theme.lignes) && job.theme.lignes.length))
    errors.push('theme must be an object with a non-empty "lignes" list (see AGENTS.md, theme videos)');
  const expect = job.expect ?? {};
  if (!isObject(expect)) errors.push('expect must be an object');
  else
    for (const k of Object.keys(expect)) if (!EXPECT_KEYS.includes(k)) errors.push(`unknown expect key "${k}" (allowed: ${EXPECT_KEYS.join(', ')})`);
  // A prop that points at a staged file must name an asset of this job.
  // Nested props (objects, lists) are checked too: a Remotion job may group them.
  if (isObject(assets) && isObject(cutouts))
    for (const [k, v] of stringLeaves(props))
      if (v.startsWith('assets/job/') && !(v.slice(11) in assets) && !(v.slice(11) in cutouts))
        errors.push(`prop "${k}" points to ${v} but the job has no asset named "${v.slice(11)}"`);
  if (errors.length) fail(`invalid job:\n  - ${errors.join('\n  - ')}`);
  return {...job, props, assets, cutouts, expect, name: job.output.replace(/\.mp4$/, '')};
}

// Every string inside props, with its path ("produit.plans.0.titre.1").
export function stringLeaves(value, at = '') {
  if (typeof value === 'string') return [[at, value]];
  if (value === null || typeof value !== 'object') return [];
  return Object.entries(value).flatMap(([k, v]) => stringLeaves(v, at ? `${at}.${k}` : k));
}

// library/ holds shop-neutral files; jobs/<shop>/ holds a shop's own files (logo, music).
function isRepoFile(p) {
  const abs = path.resolve(ROOT, p);
  return ['library', 'jobs'].some((dir) => p.startsWith(`${dir}/`) && abs.startsWith(path.join(ROOT, dir) + path.sep));
}

async function download(url, file) {
  for (let attempt = 1; ; attempt++) {
    try {
      const res = await fetch(url, {signal: AbortSignal.timeout(90_000), redirect: 'follow'});
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const buf = Buffer.from(await res.arrayBuffer());
      if (buf.length === 0) throw new Error('empty body');
      if (buf.length > MAX_ASSET_BYTES) fail(`${url} is larger than ${MAX_ASSET_BYTES} bytes`);
      writeFileSync(file, buf);
      return buf.length;
    } catch (e) {
      if (attempt === 3) fail(`download failed after 3 tries: ${url} (${e.message})`);
      await new Promise((r) => setTimeout(r, attempt * 3000));
    }
  }
}

function setOutput(key, value) {
  if (process.env.GITHUB_OUTPUT) appendFileSync(process.env.GITHUB_OUTPUT, `${key}=${value}\n`);
  console.log(`${key}=${value}`);
}

async function prepare() {
  const {JOB_FILE = '', JOB_JSON = ''} = process.env;
  if (!!JOB_FILE.trim() === !!JOB_JSON.trim()) fail('give exactly one of the inputs "job" (a file in jobs/) or "job_json"');
  let raw;
  if (JOB_FILE.trim()) {
    const file = path.resolve(ROOT, JOB_FILE.trim());
    if (!file.startsWith(ROOT + path.sep) || !existsSync(file)) fail(`job file not found in the repo: ${JOB_FILE}`);
    raw = readFileSync(file, 'utf8');
  } else raw = JOB_JSON;
  let parsed;
  try {
    parsed = JSON.parse(raw);
  } catch (e) {
    fail(`the job is not valid JSON: ${e.message}`);
  }
  const job = validateJob(parsed);
  const engine = ENGINES[job.engine];
  const project = engine.projectDir(job.composition);
  if (job.engine === 'hyperframes' && !existsSync(path.join(project, 'index.html')))
    fail(`no HyperFrames project at hyperframes/${job.composition}/index.html`);

  const stage = engine.stageDir(job.composition);
  rmSync(stage, {recursive: true, force: true});
  mkdirSync(stage, {recursive: true});
  for (const [name, src] of Object.entries(job.assets)) {
    const dest = path.join(stage, name);
    if (src.startsWith('https://')) console.log(`asset ${name}: ${await download(src, dest)} bytes from ${src}`);
    else {
      const from = path.resolve(ROOT, src);
      if (!existsSync(from)) fail(`repo file not found: ${src}`);
      copyFileSync(from, dest);
      console.log(`asset ${name}: ${statSync(dest).size} bytes from ${src}`);
    }
  }
  mkdirSync(OUT, {recursive: true});
  const cutouts = Object.entries(job.cutouts).map(([name, from]) => ({from: path.join(stage, from), to: path.join(stage, name)}));
  writeFileSync(path.join(OUT, 'cutouts.json'), JSON.stringify(cutouts, null, 2));
  writeFileSync(path.join(OUT, 'props.json'), JSON.stringify(job.props, null, 2));
  writeFileSync(path.join(OUT, 'job.json'), JSON.stringify(job, null, 2));
  setOutput('engine', job.engine);
  setOutput('name', job.name);
  setOutput('cutout', cutouts.length ? 'true' : 'false');
  setOutput('theme', job.theme ? 'true' : 'false');
}

function run(cmd, args, cwd, env = {}) {
  console.log(`$ (cd ${path.relative(ROOT, cwd) || '.'}) ${cmd} ${args.join(' ')}`);
  const r = spawnSync(cmd, args, {cwd, stdio: 'inherit', env: {...process.env, ...env}, shell: process.platform === 'win32'});
  if (r.status !== 0) fail(`${cmd} exited with ${r.status ?? r.signal}`);
}

function readJob() {
  const file = path.join(OUT, 'job.json');
  if (!existsSync(file)) fail('out/job.json is missing: run "prepare" first');
  return JSON.parse(readFileSync(file, 'utf8'));
}

function render() {
  const job = readJob();
  const out = path.join(OUT, job.output);
  const props = path.join(OUT, 'props.json');
  const project = ENGINES[job.engine].projectDir(job.composition);
  const bin = (dir, name) => path.join(dir, 'node_modules', '.bin', name);
  rmSync(out, {force: true});
  const started = Date.now();
  if (job.engine === 'remotion')
    run(bin(project, 'remotion'), ['render', 'src/index.ts', job.composition, out, `--props=${props}`, '--codec=h264', '--log=info'], project);
  else {
    // A script error is only reported after every frame was captured (6 min for 60 s, seen on
    // 2026-11-09): check the page in headless Chrome first, it fails in seconds.
    // "validate" has no variables option: it checks a copy whose declared defaults are the job's props.
    const copie = path.join(OUT, 'validation');
    rmSync(copie, {recursive: true, force: true});
    cpSync(project, copie, {recursive: true});
    const html = readFileSync(path.join(copie, 'index.html'), 'utf8');
    const values = JSON.parse(readFileSync(props, 'utf8'));
    const patched = html.replace(/data-composition-variables='([\s\S]*?)'/, (_, decl) => {
      const vars = JSON.parse(decl).map((v) => (v.id in values ? {...v, default: values[v.id]} : v));
      return `data-composition-variables='${JSON.stringify(vars).replace(/'/g, '&#39;')}'`;
    });
    writeFileSync(path.join(copie, 'index.html'), patched);
    run(bin(path.join(ROOT, 'hyperframes'), 'hyperframes'), ['validate', '--no-contrast', '--timeout', '20000'], copie,
      {HYPERFRAMES_NO_TELEMETRY: '1', DO_NOT_TRACK: '1', HYPERFRAMES_NO_UPDATE_CHECK: '1', HYPERFRAMES_SKIP_SKILLS: '1'});
    run(
      bin(path.join(ROOT, 'hyperframes'), 'hyperframes'),
      ['render', '--output', out, '--variables-file', props, '--strict-variables', '--strict', '--quality', 'looks'],
      project,
      {HYPERFRAMES_NO_TELEMETRY: '1', DO_NOT_TRACK: '1', HYPERFRAMES_NO_UPDATE_CHECK: '1', HYPERFRAMES_SKIP_SKILLS: '1'},
    );
  }
  const timing = {renderStartedAt: started / 1000, renderSeconds: Math.round((Date.now() - started) / 100) / 10};
  writeFileSync(path.join(OUT, 'timing.json'), JSON.stringify(timing));
  console.log(`render took ${timing.renderSeconds} s`);
}

const tool = (name) => process.env[name.toUpperCase()] || name;
function capture(cmd, args) {
  const r = spawnSync(tool(cmd), args, {encoding: 'buffer', maxBuffer: 64 * 1024 * 1024});
  if (r.status !== 0) fail(`${cmd} failed: ${r.stderr?.toString().slice(-600)}`);
  return r;
}

// Grey 36×64 thumbnail of the frame at t seconds, as raw bytes.
function thumb(file, t) {
  return capture('ffmpeg', ['-v', 'error', '-ss', String(t), '-i', file, '-frames:v', '1', '-vf', 'scale=36:64,format=gray', '-f', 'rawvideo', '-']).stdout;
}
const stdev = (b) => {
  const m = b.reduce((s, x) => s + x, 0) / b.length;
  return Math.sqrt(b.reduce((s, x) => s + (x - m) ** 2, 0) / b.length);
};
const meanDiff = (a, b) => a.reduce((s, x, i) => s + Math.abs(x - b[i]), 0) / a.length;

// Pure: compare probed facts with the job's expectations. Returns the list of problems.
export function compare(facts, expect) {
  const problems = [];
  if (!facts.video) return ['no video stream'];
  if (!(facts.duration > 0)) problems.push('duration is 0');
  if (expect.width && facts.width !== expect.width) problems.push(`width ${facts.width}, expected ${expect.width}`);
  if (expect.height && facts.height !== expect.height) problems.push(`height ${facts.height}, expected ${expect.height}`);
  if (expect.fps && Math.abs(facts.fps - expect.fps) > 0.01) problems.push(`fps ${facts.fps}, expected ${expect.fps}`);
  if (expect.minSeconds && facts.duration < expect.minSeconds) problems.push(`duration ${facts.duration} s, expected at least ${expect.minSeconds}`);
  if (expect.maxSeconds && facts.duration > expect.maxSeconds) problems.push(`duration ${facts.duration} s, expected at most ${expect.maxSeconds}`);
  if (expect.audio === true && !facts.audio) problems.push('no audio stream');
  if (expect.audio === true && facts.audio && !(facts.audioMaxDb > -50)) problems.push(`audio is silent (max ${facts.audioMaxDb} dB)`);
  if (expect.audio === false && facts.audio) problems.push('unexpected audio stream');
  if (facts.frameContrast < 2) problems.push(`the picture is flat (contrast ${facts.frameContrast}): blank or missing media`);
  if (facts.motion < 0.5) problems.push(`first and last frames are identical (difference ${facts.motion}): nothing moves`);
  return problems;
}

function check() {
  const job = readJob();
  const file = path.join(OUT, job.output);
  if (!existsSync(file) || statSync(file).size === 0) fail(`output missing or empty: out/${job.output}`);
  const probe = JSON.parse(capture('ffprobe', ['-v', 'error', '-show_streams', '-show_format', '-of', 'json', file]).stdout.toString());
  const v = probe.streams.find((s) => s.codec_type === 'video');
  const a = probe.streams.find((s) => s.codec_type === 'audio');
  const [num, den] = (v?.avg_frame_rate ?? '0/1').split('/').map(Number);
  const duration = Math.round(Number(probe.format.duration) * 1000) / 1000;
  const facts = {
    bytes: Number(probe.format.size),
    duration,
    video: v ? v.codec_name : null,
    width: v?.width,
    height: v?.height,
    fps: den ? Math.round((num / den) * 1000) / 1000 : 0,
    frames: v?.nb_frames ? Number(v.nb_frames) : null,
    audio: a ? a.codec_name : null,
  };
  if (a) {
    const log = capture('ffmpeg', ['-v', 'info', '-i', file, '-map', '0:a:0', '-af', 'volumedetect', '-f', 'null', '-']).stderr.toString();
    facts.audioMaxDb = Number(log.match(/max_volume: (-?[\d.]+) dB/)?.[1] ?? -91);
    facts.audioMeanDb = Number(log.match(/mean_volume: (-?[\d.]+) dB/)?.[1] ?? -91);
  }
  if (v) {
    const first = thumb(file, 0);
    const middle = thumb(file, duration / 2);
    const last = thumb(file, Math.max(0, duration - 0.1));
    facts.frameContrast = Math.round(Math.min(stdev(first), stdev(middle), stdev(last)) * 10) / 10;
    facts.motion = Math.round(meanDiff(first, last) * 10) / 10;
  }
  const timingFile = path.join(OUT, 'timing.json');
  const timing = existsSync(timingFile) ? JSON.parse(readFileSync(timingFile, 'utf8')) : {};
  const startedAt = Number(process.env.JOB_STARTED_AT || 0);
  if (startedAt && timing.renderStartedAt) timing.setupSeconds = Math.round(timing.renderStartedAt - startedAt);
  const problems = compare(facts, job.expect);
  const result = {job: {engine: job.engine, composition: job.composition, output: job.output}, facts, timing, problems, ok: problems.length === 0};
  writeFileSync(path.join(OUT, `${job.name}.json`), JSON.stringify(result, null, 2));
  console.log(JSON.stringify(result, null, 2));

  if (process.env.GITHUB_STEP_SUMMARY) {
    const row = (k, val) => `| ${k} | ${val ?? '—'} |`;
    appendFileSync(
      process.env.GITHUB_STEP_SUMMARY,
      [
        `## ${problems.length ? 'FAILED' : 'OK'}: ${job.output}`,
        '',
        '| | |',
        '|---|---|',
        row('Engine / composition', `${job.engine} / ${job.composition}`),
        row('Size', `${(facts.bytes / 1048576).toFixed(2)} MB`),
        row('Picture', `${facts.width}×${facts.height}, ${facts.fps} fps, ${facts.video}`),
        row('Duration', `${facts.duration} s${facts.frames ? ` (${facts.frames} frames)` : ''}`),
        row('Sound', facts.audio ? `${facts.audio}, max ${facts.audioMaxDb} dB, mean ${facts.audioMeanDb} dB` : 'none'),
        row('Contrast / motion', `${facts.frameContrast} / ${facts.motion}`),
        row('Setup (checkout to render start)', timing.setupSeconds != null ? `${timing.setupSeconds} s` : null),
        row('Render', timing.renderSeconds != null ? `${timing.renderSeconds} s` : null),
        ...(problems.length ? ['', ...problems.map((p) => `- ${p}`)] : []),
        '',
      ].join('\n'),
    );
  }
  if (problems.length) fail(`the video does not match the job:\n  - ${problems.join('\n  - ')}`);
}

const steps = {prepare, render, check};
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const step = steps[process.argv[2]];
  if (!step) {
    console.error(`usage: node scripts/render.mjs ${Object.keys(steps).join('|')}`);
    process.exit(2);
  }
  try {
    await step();
  } catch (e) {
    console.error(`FAILED: ${e.message}`);
    // An annotation makes the reason readable from the API (check-runs/{job_id}/annotations).
    if (process.env.GITHUB_ACTIONS)
      console.log(`::error title=${process.argv[2]} failed::${e.message.replace(/%/g, '%25').replace(/\r/g, '%0D').replace(/\n/g, '%0A')}`);
    process.exit(1);
  }
}
