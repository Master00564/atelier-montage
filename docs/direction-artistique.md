# Direction artistique des vidéos thème

Écrite une fois, appliquée par `hyperframes/theme-video` et `scripts/theme.py` à chaque vidéo thème
(art déco le 2026-11-09 ; art nouveau, scandinave, verre soufflé ensuite). Ce qui appartient à la
boutique (couleurs, logo, polices de marque) vient de `jobs/<boutique>/profil.json` ; ce qui
appartient au thème (géométrie, accents) vient du job. Rien de tout cela n'est écrit dans le code.

## Format

- 1080 × 1920, 30 images/s, **60,0 s exactement** (1 800 images), en **boucle** : la dernière phrase
  (« … et c'est pour ça que ») mène à la première, la dernière image coule dans la première, la
  musique boucle sur une mesure entière. Ni carte de fin, ni logo au début ou à la fin.
- Accroche dans la première seconde : le visuel le plus fort et un titre court sur le premier mot.

## Zones

| Zone | Pixels | Usage |
|---|---|---|
| Haut interdit | y < 270 (14 %) | rien d'important (interface Reels) |
| Bas interdit | y > 1536 (20 %) | images seulement, jamais de texte |
| Rail droit | x > 960, y 1050-1700 | pas de texte |
| Marges | 64 px de chaque côté (titres : 90 px) | |
| Monogramme | x 72, y 286, 70 × 70 px, or à 90 % | présent toute la vidéo, un reflet toutes les 14 s |
| Bande des titres | y 290-680 (jusqu'à 1 100 sur un plan sans image) | titres, compteurs |
| Fenêtre image | y 700-1680 (plein cadre : 560-1740, fondu haut et bas) | images, laisse les titres libres |
| Sous-titres | bas du bloc à y 1486, largeur 880 | toujours dans la zone sûre |

## Typographie

| Rôle | Police | Taille | Règle |
|---|---|---|---|
| Titre clé (mot en or) | affiche du thème (art déco : Josefin Sans 700, interlettrage 0,02 em) | **150 à 230 px** (hauteur de capitale ≥ 110 px) | un titre clé sous 150 px fait échouer le rendu : couper la ligne |
| Ligne secondaire (ivoire) | même police | 84 à 142 px | |
| Surtitre | même police, 600, capitales, interlettrage 0,42 em | 36 px | contexte (nom, lieu) |
| Compteur | même police, 700 | 160 à 230 px, ajusté à 900 px | |
| Sous-titres | police texte de la boutique (Poppins SemiBold) | 58 px, interligne 1,22 | 2 lignes, ≤ 24 signes par ligne, équilibrées (dernière ligne ≥ 60 % de la première), 1 à 2 mots clés en or par ligne parlée |

## Couleurs

- Boutique (profil) : `encre`, `ivoire`, `or`.
- Thème (job, `theme.palette`) : `fond` (noir chaud), `fond2` (art déco : vert profond `#0e2a24`),
  `or_clair` (reflets). Accents d'un ornement : `orne_opts.couleurs` (ex. couleurs « joyaux »).
- Contraste : texte ivoire sur voile sombre (dégradé bas `#scrim`), ombre portée douce.

## Rythme et mouvement

- **Coupes** : sur le temps de musique juste avant le premier mot de la ligne (0,02 à 0,36 s avant),
  jamais après la voix.
- **Texte** : chaque mot des sous-titres apparaît à son temps parlé (Whisper, −0,03 s) ; un titre
  arrive sur son mot (`sur`, −0,06 s), lettres en 0,42 s, puis dérive lentement et sort en 0,24 s
  avant la coupe suivante.
- **Jamais immobile** : chaque plan dérive (poussée, recul, glissé, montée), le détourage bouge plus
  que le fond (parallaxe), un balayage de lumière toutes les 2 s, une pulsation d'ornement toutes
  les 4 temps, le grain change à chaque image.
- **Punch-in** : +6 % en 0,4 s sur le mot du titre.
- **Transitions** (0,42 s, finies à la coupe) : volet doré, iris, éventail, persienne, fouet (flou
  de bougé), zoom, éclat, coupe sèche ; **profondeur** (la caméra traverse trois arches dorées) entre
  les deux parties. Un changement de sujet prend une transition différente de la précédente.
- **Flou de bougé** : vrai flou HyperFrames sur toute la composition (obturateur 220°, 10 échantillons).

## Courbes nommées

| Nom | Courbe GSAP | Pour |
|---|---|---|
| `entree` | `expo.out` | tout ce qui arrive : rapide puis se pose |
| `sortie` | `power3.in` | ce qui part |
| `glisse` | `power4.inOut` | volets, iris, fouets, cadres dessinés |
| `rebond` | `back.out(2.2)` | petits éléments (surtitres, ampoules, monogramme) |
| `derive` | `none` | mouvements continus (pour que la boucle raccorde) |

## Son

- Voix devant : musique baissée de 9 dB sous la voix (enveloppe 30 ms / 350 ms), −15 dB sous la voix
  à l'origine.
- Effets originaux synthétisés : souffle sur chaque transition (pic sur la coupe), clic sur les
  coupes sèches et les compteurs, coup sourd sur les titres, scintillement sur les ornements dorés,
  montée dans la dernière seconde et demie vers la boucle.
- Master : **−14 LUFS intégrés**, crête vraie ≤ −1 dBTP (limiteur circulaire), contrôlé après rendu.
