# REVIEW — « Ton lustre est sûrement trop petit » (vidéo à thème, 65 s, en boucle)

## Ce qui a été fait
- 18 plans, 1080 x 1920, 30 images/s, 65,000 s. Faits tirés de l'article de la boutique seulement
  (https://latelierdulustre.com/blogs/conseils-deco/taille-lustre-salon) : (L + l) × 8, ×10 pour 90 cm, diamètre hors tout bras compris,
  un modèle ouvert une taille au-dessus, table : 2/3 de sa largeur (90 cm → 60 cm), « si les deux règles divergent, suivez la table »,
  hauteur : plafond ÷ 5,5 (2,50 m → 45 cm), 2,15 m de passage, donc 35 cm platine comprise, la plus petite l'emporte.
- Fil conducteur : un trait coté doré qui mesure ce que la voix nomme. Images : photos de la boutique (Orvane-2, salon du soir de
  l'article, Domia-5, Orive-1) et le schéma de l'article recadré sans la personne dessinée (une femme : interdit par le profil).
- Boucle : la dernière image est l'image 0 (même photo, même cadrage, caméra qui atteint l'échelle 1 sur la dernière image, même promesse
  « Le bon luminaire, du premier coup » en bas) ; la voix finit sur « Et c'est pour ça que… » et le film repart sur « Ton lustre est
  sûrement trop petit ».

## Décisions prises
- **65 s et non 60 s** : le profil a été changé ce soir (`formats.theme`, règle d'Ali du 17/11 : une vidéo à thème dure exactement 65 s).
  Le texte a été allongé de deux faits de l'article.
- **Voix** : 4 prises Gemini sur la nouvelle clé (la toute première, sur l'ancien dépôt, a été perdue par le blocage du stockage).
  Les deux prises qui finissaient sur « que… » retombaient (−4 demi-tons mesurés) au lieu de rester en suspens. Solution retenue : la voix
  dit la phrase entière jusqu'à « ton lustre est sûrement trop petit » et le clip est coupé à 64,535 s, juste avant « ton » (fondu 30 ms) ;
  « que » garde l'intonation d'une phrase qui continue, comme au raccord de la boucle. Prise 4 gardée (aucun groupe pressé, 1,8 % d'erreur
  de lecture), remise au rythme par le mode `cadence` avec des pauses de 0,27 s après les points (au lieu de 0,30) pour que « que » tombe
  avant 65 s ; aucun nouvel appel à la voix pour cela.
- **Intonation** : l'outil voix de l'atelier n'accepte qu'une consigne de style par prise ; la consigne décrit le ton moment par moment
  (accroche piquante, règles claires, petite surprise sur chaque résultat, dernière phrase d'un seul souffle). Mesure `intonation.json` de
  l'atelier : 25 phrases « ok », aucune plate ; écart de hauteur 3,9 à 11,7 demi-tons selon les phrases ; « Cinq mètres sur quatre ? » et
  « Une table de quatre-vingt-dix centimètres ? » montent (+9,9 et +6,8 demi-tons).
- **Musique** : « Happy Guitar » (edtijo, CC0) tournée : piste de 47,00 à 77,87 s puis de 12,87 à 47,00 s, fondu de 0,4 s caché sous
  le filé de 30,87 s ; la fin du film rejoint le début sur des échantillons consécutifs de la piste. Encodée en MP3 320 kb/s (le proxy
  GitHub refuse un fichier de plus de ~3,5 Mo ; la source est un MP3 de 180 kb/s, rien n'est perdu à l'oreille).
- **Niveaux** : `lit_musique.py` refusait 2 groupes à 9,5 dB (seuil 9) ; copie locale réglée (cible 11,7 dB sous la voix, plancher 10 dB par
  groupe, écart entre groupes 3 dB, la règle du son en permet 3) puis vérification par l'outil officiel `--verifier` : voix 10,4 à
  15,6 dB au-dessus de la musique, médiane 11,7 dB, passage sans voix final 7,3 dB sous la voix (porte 8). La voie de volume finit à la
  valeur de l'image 0 (remontée de +6,4 dB en 0,46 s après « que », 13,9 dB/s) pour que la musique ne saute pas au raccord.
- **Effets** : 52, banque earshot, placés par `place_effets.py` ; aucun pic à moins de 0,15 s d'un autre ni pendant un nombre dit (les
  accents des chiffres vont dans les pauses). Une seule montée et un seul impact, sur « l'emporte » (plan 15).
- **Seuil réglé pour ce film** : `fondu_fin_min_s` = 0 (une boucle ne se termine pas par un fondu de musique).

## Contrôles
- Contrôle 1 : défauts corrigés en un lot (image noire au raccord en cercle de 21,6 s et sur les plans 4 et 16, voix et premier bruitage
  sur la même piste, bord clair au plan 16, titre « trop petit » à 2,4:1, « 4 m » collé à « 9 × 8 », cotes d'Orive sur les globes, bande
  sombre de 2-3 images avant chaque filé, liste des calculs trop brève, « 2 » à 1,88:1).
- Contrôle 2 : aucune erreur, aucune alerte de contraste ni de contrat ; accroche 9 images fortes, énergie 32,9 (seuils 8 et 15).
- Alertes gardées : « une taille au-dessus » 1,20 s (le titre est dit par la voix, il reste 0,5 s après son dernier mot, règle de
  `moteur.md`) ; « 2/3 de la table » 1,27 s (rappel d'un calcul déjà montré à l'écran) ; promesse finale 1,64 s : en boucle elle se
  prolonge dans l'image 0 (1,85 s de plus), soit 3,5 s d'affilée à chaque passage.
- Plans de plus de 3 s (s1, s4 à s12, s14, s16) : chacun a trois états ou plus sur des mots dits.

## Rendu livré (run 43989704237, commit 1c5ba05513, dépôt public Master00564/atelier-montage)
- 1 950 images, 65,000 s, 1080 x 1920, h264 ; −14,3 LUFS, crête −1,6 dBTP ; aucun blanc ; voix 10,0 à 15,2 dB au-dessus de la musique
  (médiane 11,3, portes 9 et 14) ; passage sans voix final 7,7 dB sous la voix (porte 8) ; mouvement de la voie de musique 3,4 dB au plus
  en 0,2 s (porte 4, à 64,54 s : la remontée de la boucle) ; accroche 9 images fortes, énergie 34,4 ; aucun saut d'image ; 52 effets
  audités « clean » ; `echecs` vide.
- Premier rendu (run 43987818744) refusé : une image noire à 52,267 s, un trou d'une image entre les plans 12 et 13 dû à l'arrondi des
  débuts et durées au millième. Plans désormais calés sur des images entières avec une image de recouvrement. Le son des deux rendus est
  identique (mêmes pistes au même endroit) : l'écoute earshot du premier vaut pour le second.

## Raccord de la boucle (vérifié sur le fichier livré)
- Image : dernière image (n° 1949) contre image 0 : écart moyen de 2,39 niveaux de gris sur toute l'image, 1,80 au-dessus de la bande des
  sous-titres ; deux images voisines dans le film diffèrent de 1,17. La seule chose qui change franchement au raccord est le sous-titre
  « Et c'est pour ça que… » qui laisse place à « Ton lustre est sûrement » 0,17 s plus tard, comme d'un groupe au suivant.
- Son : dernier échantillon contre premier : saut de 0,0014 (pas moyen entre deux échantillons du film : 0,0074) : pas de clic. Niveau :
  −23,4 dB sur les 50 dernières ms, −25,6 dB sur les 50 premières (−24,7 et −24,0 dB sur 250 ms) : la musique continue sans saut.
  La musique joue des échantillons consécutifs de la piste à travers le raccord ; la voix laisse 0,70 s entre « que… » et « Ton »
  (0,46 s à la fin, 0,24 s au début).

## Écoute (earshot, sur la copie de partage)
- Verdict « proche » des 7 films de référence : 20 mesures sur 23 dans la plage. Synchro des effets sur leurs repères : 72 % à 40 ms près
  (hasard 50 %), 94 % à 100 ms. Musique présente 100 % du temps, aucun trou, première note à 0,00 s, pas de silence à la fin.
- Remarques de la critique, non bloquantes (elle compare à des films de lancement, pas à un film narré) : « trop de coups saillants »
  (1,86/s, la plus haute des références 1,66/s : consonnes de la voix et effets réunis) ; bas du spectre maigre (guitare acoustique, pas de
  basse) ; presque mono (voix mono, musique peu large).

## Ce que personne n'a vérifié
- Le rendu réel des mouvements entre deux images (planches à 2 images/s seulement) et la sensation « premium ».
- La voix entendue : l'intonation a été mesurée (hauteur, montées), pas écoutée ; earshot ne comprend pas les mots.
- Le raccord de boucle dans les lecteurs d'Instagram, Facebook et Pinterest (chacun peut ajouter son propre temps de chargement).
- L'humeur de la musique (les étiquettes d'earshot la disent « corporate », souvent faux).

## Le plan le plus faible et ce que je changerais
- Plans 4 à 6 (formule et calcul) : beaucoup de papier vide sous les chiffres ; une prochaine fois, un dessin plus grand du salon ou une
  photo de la boutique en fond flou sous la formule.
- Plan 7b (Orive) : les étiquettes « hors tout, bras compris » croisent les câbles ; lisibles, mais un fond plus calme aiderait.

## À signaler (hors film)
- L'article publié dit d'Orvane « 16,5 cm de haut, 45 cm de diamètre » ; la fiche Orvane dit 50 x 17 cm, et 45 x 16,5 cm sont les cotes
  d'Ornela. Le film ne cite aucune cote de produit.
