# REVIEW — « Ton lustre est sûrement trop petit » v2 (vidéo à thème, 65 s, en boucle)

v2 refaite le 17/11 selon les règles d'Ali du jour : recherche propre au-delà de l'article, images faites pour le film, appel au guide du
site, 65 s pile, intonation dirigée phrase par phrase. Elle remplace la v1 : la v1 n'est plus le film (son dossier `Téléchargements/montage-lustre-trop-petit` est laissé tel quel).

## Ce qui a été fait
- 18 plans, 1080 x 1920, 30 images/s, 65,000 s (1 950 images). Trois règles : diamètre (L + l) × 8,3 (5 x 4 m → 75 cm, « presque la
  largeur d'une porte », « un minimum », plus grand sous un haut plafond) ; table : 2/3 de sa largeur au plus (90 cm → 60 cm, 30 de
  moins) ; hauteur : 1/5 à 1/4 de la hauteur sous plafond (2,50 m → 52 à 62 cm) mais 2,13 m de passage dessous, il reste 37 cm, la plus
  petite mesure l'emporte, sous un plafond bas un plafonnier. Puis « Le guide complet est sur L'Atelier du Lustre point com » et le
  raccord de boucle.
- Côté boutique : le plafonnier Orvane ouvre et ferme la boucle, Orvane allumé porte « le minimum », Domia montre la règle de la table,
  Tressa allumé porte « plafonnier » et l'appel au guide. Aucun prix, aucune cote de produit à l'écran.

## Recherche au-delà de l'article (`sources.md`, pages lues le 17/11)
- L'article donne le sujet. Chaque chiffre dit a deux sources ou plus (Visual Comfort, Kichler, Lamps.com, Lumens, Golden Lighting,
  Schoolhouse, Hörmann, Bricozor, Foncia, Qualitel), citées mot pour mot dans `sources.md`.
- Repris de l'article mais corrigé : « × 8 » devient « × 8,3 » (conversion exacte de la règle pieds → pouces des fabricants) ; « 2,15 m »
  de passage devient « 2,13 m » (7 pieds chez Kichler, Lumens, Visual Comfort).
- Abandonnés faute de source : le « × 10 » (90 cm) et la hauteur « plafond ÷ 5,5 » (45 cm). Remplacés par la règle sourcée du
  cinquième au quart (2,5 à 3 pouces par pied, trois sources).
- Ajouts trouvés par la recherche : « l'une des erreurs les plus fréquentes, selon les pros de l'éclairage » (trois sources), « c'est un
  minimum » (Kichler, Golden Lighting), « plus grand sous un haut plafond » (Lumens, Visual Comfort ; le « 10 à 20 % » n'a qu'une source,
  il n'est pas dit), « presque la largeur d'une porte » (73 cm, norme NF P20-101, Hörmann et Bricozor), « 2,50 m, la hauteur standard
  en France » (Foncia, Qualitel 2021), « trente de moins que la table » (Chloe Winston : un pied de moins).

## Images faites pour le film
- Dessinés par code (aucune image de l'article, aucune image générée) : le salon vu de dessus et ses cotes, la formule, le compteur
  jusqu'à 75 et l'anneau de 75 cm à l'échelle, la porte et « porte standard : 73 cm », le contour pointillé qui grandit sur « plus
  grand », les repères de la table, la table de 90 cm et la coupole de 60 cm, le schéma de hauteur (plafond hachuré, sol, canapé,
  plafonnier, bande des 62 cm et trait des 52 cm, bande des 2,13 m, bande qui se rétracte à 37 cm), la liste finale.
- Photos des produits de la boutique (CDN Shopify) : Orvane-2 (découpé à la main pour rétrécir et grossir le plafonnier dans le
  salon), Orvane-3 (le soir), Domia-5 (coupole détourée pour la faire grossir), Tressa-3 (le soir). Les trois produits sont ACTIVE
  dans Shopify (vérifié le 17/11) ; aucun brouillon. Aucune personne visible.

## Voix
- Une seule prise Gemini (Algieba, ×1,2), dirigée par `voix.segments` : 12 segments, chacun avec un style court (accroche « punchy, a
  little teasing, a playful challenge », règles « clear and explanatory, warm, steady pace », résultats chiffrés « clear, with a small
  spark of surprise on the result », appel au guide « warm, friendly invitation, smiling », raccord « rising questioning tone, clear full
  voice »). Remise au rythme par `cadence` (pauses 0,30 s), sans nouvel appel voix. Aucune seconde prise : ni l'accroche ni la
  phrase de raccord n'étaient signalées plates.
- `intonation.json` (24 phrases, 20 « ok ») : accroche « ok » (écart 7,8 demi-tons) ; « Cinq mètres sur quatre ? » et « Une table de quatre-vingt-dix
  centimètres ? » jugées « pas assez vives » (elles montent bien en fin : +4,4 et +3,8 demi-tons ; gardées, ce ne sont pas des lignes clés) ;
  raccord « fin pas montante » : la mesure porte sur toute la phrase jusqu'à « petit », dont le film ne garde que « Et c'est pour ça
  que » ; sur la partie gardée, « ça » monte de 8,4 demi-tons et « que » redescend de 6,4.
- Limite de l'outil voix (non modifié) : le style se donne par segment, pas par mot ; la hauteur se mesure, elle ne se règle pas ;
  une phrase qui finit en suspens se dit en continuant la phrase puis en coupant la piste.

## Musique et niveaux
- « Happy Guitar » (edtijo, CC0 1.0, Freesound 207558) tournée pour la boucle : piste de 47,00 à 72,77 s puis de 7,77 à 47,00 s, fondu
  à puissance égale de 0,4 s caché sous le filé de 25,77 s ; la fin du film précède le début sur des échantillons consécutifs.
- Niveaux par une copie locale de `lit_musique.py` (cible 11,7 dB sous la voix, plancher 10 dB, écart entre groupes 3 dB), vérifiés
  par l'outil officiel `--verifier` : voix 10,6 à 17,8 dB au-dessus de la musique.
- 47 effets (banque earshot) placés par `place_effets.py` : aucun pic à moins de 0,15 s d'un autre, aucun pendant un nombre dit.
- Seuils réglés pour ce film dans le manifeste : `fondu_fin_min_s` = 0 (une boucle ne finit pas par un fondu) ;
  `sans_voix_sous_voix_max_db` = 11 (le passage sans voix final de 0,83 s est le souffle avant la reprise de la boucle ; mesuré 7,5 dB,
  la porte par défaut de 8 dB passerait aussi).

## Contrôles
- Contrôle 1 (commit fa0c60d053) : aucune erreur ; défauts vus sur les planches et corrigés en un lot : « 4 m » collé au calcul
  (plan 6), canapé dessiné sous les sous-titres (plans 11 et 13 : schémas déplacés), bord net du voile sombre au plan 15b,
  « porte standard : 73 cm » lu 1,07 s (seuil 1,27 s : il arrive avec la porte), « cm » traversé par le câble (plan 9).
- Contrôle 2 (commit e82f10e160) : aucune erreur, contraste 18/18. Quatre alertes de lecture (« Quelle taille de lustre pour un
  salon ? » et les trois lignes de la liste finale) viennent de trous de mesure : une image marquée absente au milieu d'un texte
  visible coupe la durée en deux ; les durées réelles sont de 1,4 à 2,5 s.
- Rendu 2 relu : « 2,13 m » touchait le bas de la bande hachurée, et le fond clair ajouté derrière les sous-titres se voyait sur le
  papier pointillé. Corrigés (texte descendu de 55 px, fond retiré : les schémas déplacés suffisent), rendu 3.
- Accroche : 7 images fortes dans les 2 premières secondes, énergie 31 (seuils 8 et 15).

## Rendu livré
- Run 43998743753, commit 2a9c60d47f, dépôt public Master00564/atelier-montage : 1 950 images, 65,000 s, 1080 x 1920, h264 ;
  −14,0 LUFS, crête −1,8 dBTP ; aucun blanc ; voix 10,6 à 17,8 dB au-dessus de la musique (médiane 11,7, portes 9 et 14) ; passage
  sans voix final 7,5 dB sous la voix ; plus grand mouvement de la voie de musique 3,1 dB en 0,2 s (porte 4) ; accroche 7 images
  fortes, énergie 31,5 ; aucun saut d'image ; 47 effets audités « clean » ; `echecs` vide.
- Les rendus 1 et 2 (runs 43995555311 et 43997160745) sont passés aussi ; seules des positions d'images ont changé depuis, le son
  est identique au millième près (mêmes pistes, mêmes mesures) : l'écoute earshot du rendu 1 vaut pour le fichier livré.

## Raccord de la boucle (mesuré sur le fichier livré)
- Image : dernière image (n° 1949) contre image 0 : écart moyen de 1,70 niveau de gris (1,94 au-dessus des sous-titres) ; deux
  images voisines dans le film diffèrent de 1,17. Même photo, même cadrage, caméra à l'échelle 1 sur la dernière image, même
  promesse « Le bon luminaire, du premier coup » en bas ; seul le sous-titre change (« Et c'est pour ça que… » puis « Ton lustre »).
- Son : saut de 0,0044 entre le dernier et le premier échantillon (pas moyen dans le film 0,0089) : pas de clic. Niveau −20,3 dB sur
  les 50 dernières ms, −22,9 dB sur les 50 premières : la musique continue (échantillons consécutifs de la piste).
- Voix : « que » ne retombe pas : la phrase a été dite d'une traite jusqu'à « petit » puis coupée avant « ton » ; « ça » monte de
  8,4 demi-tons.
- La voix laisse 1,26 s entre « que… » et « Ton » (1,04 s à la fin, 0,22 s au début) : un temps de suspens, la musique continue.

## Écoute (earshot, sur la copie de partage)
- Verdict « proche » des 7 films de référence : 20 mesures sur 23 dans la plage ; −14,1 LUFS, crête −1,6 dBTP ; musique présente
  100 % du temps, aucun trou, première note à 0,00 s, rien de mort à la fin. Effets sur leurs repères : 69 % à 40 ms près
  (hasard 47 %), 94 % à 100 ms. Tous les effets passent l'audit (« clean »).
- Remarques non bloquantes (la critique compare à des films de lancement, pas à un film narré) : « trop d'accents saillants »
  (1,97/s, plage des références jusqu'à 1,86/s : les consonnes de la voix rapide comptent) ; bas du spectre maigre (guitare, pas de
  basse) ; presque mono. Une coupe sans son propre : le filé vers le plan 11 (37,90 s), suivi de son déclic 0,15 s après.

## Ce que personne n'a vérifié
- La voix entendue : l'intonation est mesurée (hauteur, montées), pas écoutée ; earshot ne comprend pas les mots.
- Le mouvement entre deux images (planches à 2 images/s) et l'impression « haut de gamme ».
- Le raccord de boucle dans les lecteurs d'Instagram, Facebook et Pinterest (chacun peut ajouter un temps de chargement).
- L'humeur de la musique (earshot la dit « corporate » ou « funk » : ses étiquettes de genre se trompent souvent).

## Le plan le plus faible
- Plan 5 (la formule) : beaucoup de papier vide sous « (L + l) » pendant 1,5 s avant « × 8,3 ».
- Plan 13 : le schéma rapetisse pour laisser la place aux sous-titres ; la bande des 2,13 m reste lisible mais plus petite.

## À signaler (hors film)
- L'article de la boutique contient trois chiffres sans source trouvée : le « × 10 », la hauteur « plafond ÷ 5,5 » et les « 2,15 m » de
  passage (les fabricants disent 7 pieds, soit 2,13 m). Le film ne les reprend pas ; l'article mériterait la même correction.
- L'article dit d'Orvane « 16,5 cm de haut, 45 cm de diamètre » ; la fiche Orvane dit 50 x 17 cm (45 x 16,5 cm sont les cotes
  d'Ornela). Le film ne cite aucune cote de produit.
