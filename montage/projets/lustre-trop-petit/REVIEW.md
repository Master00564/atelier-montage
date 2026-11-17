# REVIEW — « Ton lustre est sûrement trop petit » v3 (vidéo à thème, 65 s, en boucle, ton ludique)

v3 refaite le 17/11 après le retour d'Ali sur la v2 : trop de chiffres d'un coup, pas assez ludique, deux secondes sans voix au raccord,
des mots techniques. Elle remplace la v2 (dossier `Téléchargements/montage-lustre-trop-petit-v2`, laissé tel quel).

## Ce que j'ai appris des deux shorts de Science Trash (transcriptions lues par Composio, images regardées dans le navigateur)
- « Pourquoi tes cheveux deviennent blancs ? » (54 s) : une question en « tu » dès la première seconde, une comparaison de la vie de tous
  les jours (« ton pote a trois ans de plus que toi »), le mot savant dit une fois puis remplacé par une image (« comme des cartouches
  d'encre »), trois chiffres en tout, des questions qui relancent (« Mais alors, on peut rien faire contre ? »), un conseil pratique, une
  chute drôle.
- « L'IA résout un problème du millénaire ? » (2 min 05) : phrases courtes, langage parlé (« c'est toujours le bordel », « des trucs
  chelous »), et la fin qui enchaîne sur le début sans pause : la dernière phrase s'arrête sur « Donc, » et le film repart sur sa première
  phrase. Première et dernière image différentes.
- Les deux : environ 3,4 mots par seconde ; une image nouvelle toutes les 2 à 3 s (images d'illustration plein cadre, un petit
  personnage dessiné qui réagit) ; sous-titres de 2 à 4 mots en gros, centrés, un mot en couleur.
- Ce que j'en ai repris : une idée par phrase, des objets à la place des formules, des questions qui relancent, des gags visuels, une image
  nouvelle toutes les 3 s, des sous-titres plus gros et centrés, et une fin qui enchaîne sur le début sans silence. Rien n'est recopié
  (ni texte, ni image, ni personnage).

## Ce qui change par rapport à la v2
- Deux chiffres dans tout le film, dits et montrés : « vingt mètres carrés » et « deux mètres ». Tout le reste passe par des objets :
  la largeur d'une porte, un bouton de chemise au plafond, des invités qui dînent « sous un parapluie », le copain qui joue au basket, un rond
  de carton scotché au plafond. Plus aucune formule, plus de « diamètre », « platine » ni « hauteur sous plafond ».
- Texte écrit comme on parle à un ami (tu, questions, petites blagues), passé au contrôle `style-humain` (aucun constat bloquant).
- Boucle : plus de silence à la fin. La voix dit « …je parie que ton lustre est sûrement trop petit » d'une traite ; la piste est coupée
  juste avant le second « ton » et le film repart sur « Ton lustre ». Raccord mesuré plus bas.
- Commercial : les produits de la boutique (Orvane, Tressa, Domia, Ornela, tous ACTIVE), « sur nos fiches, un schéma donne les mesures
  exactes de chaque luminaire » (vérifié : chaque fiche a son schéma), puis le guide gratuit sur latelierdulustre.com.

## Recherche (`sources.md`)
Chaque fait a deux sources ou plus ; nouveau en v3 : l'astuce du rond de carton (Montreal Lighting, Residence Supply) et la règle de la
table « moins large qu'elle » (Visual Comfort, Schoolhouse, Montreal Lighting).

## Images
- Faites pour le film (Codex, gpt-6.1-terra, effort élevé), hommes seulement, vérifiées en entier puis par zones (mains, visages) :
  l'homme perplexe sous une lumière minuscule, l'homme qui scotche le carton, les quatre amis sous la coupole géante, le basketteur,
  l'homme qui se cogne.
- Photos des produits de la boutique, tous ACTIVE dans Shopify le 17/11 : Orvane-2 (découpé, il rétrécit puis grossit), Tressa-2,
  Tressa-3, Tressa-7 (schéma recadré sans chiffres), Domia-5, Ornela-2.
- Dessinés par code : porte, salon vu de dessus, coupe avec plafond qui monte, homme de 2 m à l'échelle, téléphone, coches, cœurs,
  parapluie, étoile, soleil, lune, bouton, tampons.

## Voix
- Une seule prise Gemini (Algieba, ×1,2), 5 segments aux styles courts et peu nombreux pour éviter le côté « bizarre » signalé par Ali :
  accroche « punchy, a little teasing, a playful challenge » ; tout le corps « playful and chatty, like telling a friend a good tip » ;
  appel au guide « warm, friendly invitation, smiling » ; raccord « rising questioning tone, clear full voice » ; dernière phrase comme
  l'accroche. Erreur de lecture 3,7 %.
- Remise au rythme par le mode `cadence` (aucun nouvel appel voix) : pauses à 0,27 s (prise), 0,214 s (trop court pour la boucle),
  puis 0,240 s (gardé). Puis début de la piste coupé de 0,103 s pour que la fin du film tombe juste avant le second « ton ».
- `intonation.json` (23 phrases) : 21 « ok ». Accroche « ok » (écart 7,2 demi-tons). « Pas besoin de calcul compliqué » « à surveiller »
  (écart 3,2 ; gardée, phrase courte). Raccord « fin pas montante » : la mesure porte sur toute la phrase jusqu'à « petit », dont le film
  ne garde que « …je parie que » ; ni plate ni chuchotée (écart 10,4), donc aucune seconde prise.
- Limite de l'outil voix (non modifié) : le style se donne par segment ; l'aligneur a mal placé « ta tête te dira merci » (même durée
  audio dans les deux réglages) : temps des cinq mots répartis à la main sur leur vrai intervalle pour les sous-titres.

## Musique et niveaux
- « Happy Guitar » (edtijo, CC0) tournée pour la boucle : piste 47,00→73,20 s puis 8,20→47,00 s, fondu de 0,4 s sous le filé de 26,2 s.
- Niveaux par la copie locale de `lit_musique.py` ; voie de volume réglée à la même valeur de part et d'autre du raccord (pas de saut).
- Seuils réglés pour ce film dans le manifeste : `fondu_fin_min_s` = 0 (une boucle ne finit pas en fondu) ; `souffle_min_s` = 0,7 : la
  pause de 0,63 s après « d'après les pros de la lumière » n'est pas mesurée comme un souffle (la musique ne pouvait y monter de 10 dB
  sans « pomper »).
- 45 effets (banque earshot), aucun pic à moins de 0,2 s d'un autre.

## Contrôles et rendus
- Contrôle 1 : aucune erreur ; corrigés en un lot : bande noire pendant chaque filé (le fond opaque du plan entrant cachait le plan
  sortant ; défaut présent aussi dans la v2), cadrage du plafond (plan 3), « 20 m² » qui débordait, tampon terne sur papier, téléphone
  sous les sous-titres, promesse finale trop brève, mouvements de caméra qui se chevauchaient.
- Rendu 1 refusé : deux effets à 0,10 s et le plan 6 vu 0,83 s ; le plan 6 commence désormais sur « d'une porte » (1,4 s).
- Contrôle final : aucune erreur, contraste sans alerte. Alerte gardée : « Le bon luminaire, du premier coup » mesurée 1,0 s alors qu'elle
  reste 2,2 s à l'écran (trou de mesure : un échantillon marqué absent au milieu).

## Rendu livré (run 44007759039, commit 689a0fd89e, dépôt public Master00564/atelier-montage)
- 1 950 images, 65,000 s, 1080 x 1920, h264 ; −14,0 LUFS, crête −1,8 dBTP ; aucun blanc ; voix 10,2 à 19,2 dB au-dessus de la musique
  (médiane 11,7) ; mouvement de la voie de musique 3,1 dB au plus en 0,2 s (porte 4) ; accroche 11 images fortes, énergie 56,5 ;
  aucun saut d'image ; 45 effets « clean » ; `echecs` vide.

## Raccord de la boucle (mesuré sur le fichier livré)
- Voix : la dernière syllabe (« que ») s'éteint à 64,86 s, le film finit à 65,00 s, « Ton » commence à 0,12 s : 0,26 s de silence au
  raccord, l'équivalent d'une pause ordinaire du film (0,24 s). En v2 : 1,26 s.
- Son : saut de 0,0019 entre le dernier et le premier échantillon (pas moyen dans le film 0,0096) : pas de clic ; la musique joue des
  échantillons consécutifs de la piste.
- Image : la fin revient sur le salon de l'image 0 (même photo, caméra à l'échelle 1, promesse en bas) ; écart de 2,73 niveaux de gris
  entre la dernière image et l'image 0 (deux images voisines : 1,35) ; seuls un cœur et le sous-titre diffèrent.

## Écoute (earshot, copie de partage)
- Verdict « proche » : 20 mesures sur 23 dans la plage ; −14,0 LUFS, crête −1,7 dBTP ; musique 100 % du temps, aucun trou, première
  note à 0,00 s, rien de mort à la fin ; effets sur leurs repères : 88 % des changements d'image ont un son à 100 ms près.
- Remarques non bloquantes (comparaison avec des films de lancement, pas des films narrés) : « trop d'accents saillants » (2,12/s : voix
  rapide et effets), bas du spectre maigre (guitare), presque mono.

## Ce que personne n'a vérifié
- La voix écoutée par une oreille humaine (intonation mesurée, pas écoutée) ; Ali la trouvait « un peu bizarre de temps en temps » en v2.
- Si les gags font sourire (parapluie, basketteur, homme qui se cogne) : jugement humain.
- La boucle dans les lecteurs d'Instagram, Facebook et Pinterest ; le mouvement entre deux images (planches à 2 images/s).

## Le plan le plus faible
- Plan 6 (la porte qui se replie) : la porte se replie et le luminaire apparaît pendant le filé de sortie ; on voit surtout la porte.
- Plan 19 (téléphone) : le schéma est recadré pour ne pas ajouter de chiffres, donc peu lisible comme schéma.
