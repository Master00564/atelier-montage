// Print what `hyperframes check --json` found, one line per finding, and fail a render that has errors.
//
//   node montage/outils/bilan.mjs out/controle.json
//
// In "controle" mode the run stays green whatever is found: the editor reads the findings and the
// sheets. In "rendu" mode an error stops the run before the render, so no minute goes to a broken film.
import { readFileSync } from 'node:fs';

let rapport;
try {
  rapport = JSON.parse(readFileSync(process.argv[2], 'utf8'));
} catch (e) {
  console.log(`::error::FAILED: check wrote no JSON (${e.message}); see controle.log in the artifact`);
  process.exit(1);
}

const lignes = [];
(function parcourir(noeud, chemin) {
  if (Array.isArray(noeud)) return noeud.forEach((x, i) => parcourir(x, `${chemin}[${i}]`));
  if (!noeud || typeof noeud !== 'object') return;
  const gravite = noeud.severity ?? noeud.level;
  if (typeof gravite === 'string' && (noeud.code || noeud.rule || noeud.message)) {
    lignes.push({ gravite, texte: `${noeud.code ?? noeud.rule ?? ''} ${noeud.message ?? ''} ${noeud.fix ? '| Fix: ' + noeud.fix : ''}`.trim(), chemin });
    return;
  }
  for (const [cle, valeur] of Object.entries(noeud)) parcourir(valeur, chemin ? `${chemin}.${cle}` : cle);
})(rapport, '');

const erreurs = lignes.filter((l) => /error/i.test(l.gravite));
console.log(`check ok=${rapport.ok} | findings ${lignes.length} | errors ${erreurs.length}`);
for (const l of lignes.slice(0, 60)) console.log(`${l.gravite.toUpperCase()} ${l.chemin.split('.')[0]}: ${l.texte}`.slice(0, 400));
if (process.env.MODE === 'rendu' && (rapport.ok === false || erreurs.length)) {
  console.log(`::error::FAILED: check has ${erreurs.length} error(s): ${erreurs.slice(0, 3).map((l) => l.texte).join(' ; ').slice(0, 300)}`);
  process.exit(1);
}
