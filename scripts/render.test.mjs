// node --test scripts/*.test.mjs  (runs first in every render, takes about a second)
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readdirSync, readFileSync} from 'node:fs';
import path from 'node:path';
import {ROOT, compare, stringLeaves, validateJob} from './render.mjs';
import {checkDoc} from './inventaire.mjs';

const jobs = readdirSync(path.join(ROOT, 'jobs'))
  .filter((f) => f.endsWith('.json'))
  .map((f) => [f, JSON.parse(readFileSync(path.join(ROOT, 'jobs', f), 'utf8'))]);
const good = jobs.find(([f]) => f === 'test-remotion.json')[1];
const variant = (patch) => ({...structuredClone(good), ...patch});

test('every job in jobs/ is valid', () => {
  assert.ok(jobs.length >= 2);
  for (const [f, job] of jobs) assert.doesNotThrow(() => validateJob(job), f);
});

test('invalid jobs are refused with the reason', () => {
  const cases = [
    [variant({engine: 'blender'}), /engine must be one of/],
    [variant({outputs: 'x.mp4'}), /unknown key "outputs"/],
    [variant({output: '../x.mp4'}), /output must be a plain file name/],
    [variant({output: 'x.mov'}), /output must be a plain file name/],
    [variant({composition: 'Promo; rm -rf'}), /not a valid remotion composition/],
    [variant({assets: {'photo.jpg': 'http://example.com/a.jpg'}}), /https:\/\/ URL or a path under library/],
    [variant({assets: {'photo.jpg': 'library/../.github/workflows/render.yml'}}), /path under library/],
    [variant({assets: {'../photo.jpg': 'https://example.com/a.jpg'}}), /plain file name/],
    [variant({assets: {'music.m4a': 'library/audio/soft-pad.m4a'}}), /prop "image" points to assets\/job\/photo.jpg/],
    [variant({expect: {widht: 1080}}), /unknown expect key "widht"/],
    [variant({assets: {...good.assets, 'logo.png': 'jobs/../.github/workflows/render.yml'}}), /path under library\/ or jobs/],
    [variant({cutouts: {'lamp.jpg': 'photo.jpg'}}), /must be a plain file name ending in .png/],
    [variant({cutouts: {'lamp.png': 'missing.jpg'}}), /must name an asset of this job/],
    [variant({assets: {...good.assets, 'lamp.png': 'https://example.com/a.png'}, cutouts: {'lamp.png': 'photo.jpg'}}), /has the name of an asset/],
    [variant({props: {...good.props, scene: {pictures: ['assets/job/missing.jpg']}}}), /prop "scene.pictures.0" points to assets\/job\/missing.jpg/],
  ];
  for (const [job, re] of cases) assert.throws(() => validateJob(job), re);
});

test('a cut-out is a staged file props can point to; shop files may live under jobs/', () => {
  const job = variant({
    assets: {...good.assets, 'logo.png': 'jobs/any-shop/logo.png'},
    cutouts: {'lamp.png': 'photo.jpg'},
    props: {...good.props, scene: {cutout: 'assets/job/lamp.png'}},
  });
  assert.deepEqual(validateJob(job).cutouts, {'lamp.png': 'photo.jpg'});
});

test('the output check catches each kind of bad video', () => {
  const ok = {video: 'h264', width: 1080, height: 1920, fps: 30, duration: 5, audio: 'aac', audioMaxDb: -14, frameContrast: 30, motion: 9};
  const expect = good.expect;
  assert.deepEqual(compare(ok, expect), []);
  const bad = [
    [{video: null}, /no video stream/],
    [{width: 1920, height: 1080}, /width 1920, expected 1080/],
    [{fps: 25}, /fps 25, expected 30/],
    [{duration: 3}, /at least 4.9/],
    [{audio: null}, /no audio stream/],
    [{audioMaxDb: -91}, /audio is silent/],
    [{frameContrast: 0.4}, /picture is flat/],
    [{motion: 0}, /nothing moves/],
  ];
  for (const [patch, re] of bad) assert.match(compare({...ok, ...patch}, expect).join('\n'), re);
});

// Rule for every future shop: brand data lives in jobs only. Any text a job passes as a prop
// (names, slogans, colours) must never be written into engine code.
test('no job data is hard-coded in engine code', () => {
  const engineFiles = [
    ...readdirSync(path.join(ROOT, 'remotion', 'src'), {recursive: true}).map((f) => path.join('remotion', 'src', f)),
    ...readdirSync(path.join(ROOT, 'hyperframes'), {withFileTypes: true})
      .filter((d) => d.isDirectory() && d.name !== 'node_modules')
      .map((d) => path.join('hyperframes', d.name, 'index.html')),
    path.join('scripts', 'render.mjs'),
    path.join('.github', 'workflows', 'render.yml'),
  ].filter((f) => /\.(tsx?|html|mjs|yml)$/.test(f));
  const needles = new Set();
  // Theme jobs: their spoken and printed lines, headlines and kickers too.
  const themeTexts = (theme) =>
    (theme?.lignes ?? []).flatMap((l) => [l.dit, l.ecran, ...(l.plans ?? []).flatMap((p) => [...(p.titre?.lignes ?? []), p.titre?.kicker ?? '', p.compteur?.legende ?? ''])]);
  for (const [, job] of jobs) {
    for (const [, v] of stringLeaves(job.props)) if (v.length >= 4 && !v.startsWith('assets/job/')) needles.add(v.toLowerCase());
    // A one-word headline ("STYLE") is a common word: only phrases (two words, 8 characters or more) count.
    for (const v of themeTexts(job.theme)) if (v.length >= 8 && v.trim().includes(" ")) needles.add(v.toLowerCase());
  }
  for (const f of engineFiles) {
    const text = readFileSync(path.join(ROOT, f), 'utf8').toLowerCase();
    for (const n of needles) assert.ok(!text.includes(n), `${f} contains job data "${n}"`);
  }
});

test('docs/fonctionnalites.md was generated for the pinned engine versions', () => {
  assert.doesNotThrow(checkDoc);
});
