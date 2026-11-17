# STORYBOARD — « Ton lustre est sûrement trop petit »

Film à thème (genre `theme`), 1080 x 1920, 30 fps, **65 s exactement** (règle d'Ali du 17/11, profil `formats.theme`),
en **boucle parfaite** (règle d'Ali du 17/11 transmise par la session principale : la dernière image redevient la première,
la dernière phrase inachevée se raccorde à la première). Voix Algieba ×1,2, texte relu par `style-humain`.
Faits : uniquement l'article de la boutique https://latelierdulustre.com/blogs/conseils-deco/taille-lustre-salon (lu le 16/11).

## Trois idées, une gardée

1. **Le trait coté** (gardée). Un trait doré à taquets, le mètre ruban, mesure tout ce que la voix nomme : le plafonnier
   rétrécit dans son salon, puis le trait mesure le plan du salon, devient l'anneau du diamètre à l'échelle, mesure la table,
   mesure la hauteur sous plafond, et la dernière image revient au salon de la première. Image : la photo de jour Orvane-2,
   le plafonnier ramené à 38 % avec son contour réel en pointillé.
   Test du concurrent : « le lustre est trop petit, mesure-le » vaut pour toute boutique ; ce qui ne vaut que pour nous :
   les chiffres et le schéma de NOTRE guide, nos photos, notre promesse. Phrase chaîne : le plafonnier trop petit devient
   un plan mesuré, qui devient un anneau à l'échelle, qui devient une table mesurée, qui devient une hauteur mesurée, qui
   redevient le plafonnier de départ.
2. **Le plan d'architecte** : tout le film en dessin coté sur papier. Écartée : aucune photo de la boutique, lu comme un diaporama de schémas.
3. **Trois pièces, trois règles** : un salon, une salle à manger, un plafond bas, chaque fois le luminaire redimensionné.
   Écartée : trois découpes et trois plaques, pas de fil commun d'un plan à l'autre.

Grammaire de référence (films conseils des plateformes, relevé sur nos propres films et l'étude prompt-motion du 14/11) :
plans de 1,2 à 3 s, changement d'état toutes les 0,3 à 0,65 s dans les plus réussis, premier mot lisible avant 0,5 s.

## Concept en trois lignes
- **Idée** : on mesure, règle après règle, ce qu'on aurait dû mesurer avant d'acheter, et on revient au salon du début.
- **Fil** : le trait coté doré (taquets, 6 px, tête ronde) ; il prend la forme de la chose mesurée : contour, côté, anneau, pied de table, bande de hauteur.
- **Grammaire** : chaque chiffre se pose sur un trait qui mesure la chose dont il parle, au mot où la voix le dit.

Ce que le film plante, dit par le spectateur : « je vais mesurer mon salon avant d'acheter ».

## Plan signature
À la fin de « Il ne reste alors que », la bande hachurée des 45 cm sous le plafond se rétracte à 35 cm en 0,18 s (`power4.out`),
caméra à l'échelle 2,0 sur le schéma de l'article (x 1,02 sur le plan), « 35 cm » à 300 px claque 2 images avant « trente-cinq ».
Un `whoosh` porte la rétraction (avant le nombre) ; la montée et l'unique impact vont sur « l'emporte » (plan 15), mot qui n'est pas un nombre. Battement calme déclaré juste avant : la caméra presque
immobile (+2 % sur tout le plan) pendant 0,5 à 0,9 s après l'entrée.

## Courbe d'énergie
Pic d'entrée (0-6 s : rétrécit, écrase, mètre ruban), règle 1 claire et chiffrée (9-31 s), règle 2 (31-45 s, la suspension qui
déborde), règle 3 qui monte (45-58 s) jusqu'au plan signature vers 85 % du film, puis rappel des trois calculs et retour au salon
de l'image 0 (la boucle).

## Matériel (chaque pièce vue en entier puis par zones)
| Fichier | Source | Vérifié | Verdict |
|---|---|---|---|
| `jour-lampe.png`, `jour-plaque.png` | photo boutique Orvane-2 (CDN Shopify, 1254 px), découpe tracée à la main (deux ellipses et un rectangle mesurés au pixel), plafond rebouché par moyenne poussée-tirée (code maison) | découpe sur fond sombre et clair : diffuseur allumé gardé entier (l'outil automatique le perd), liseré clair d'1 px à droite ; plaque : tache douce et claire à la place du luminaire, léger arc sombre en bas, jamais vue nue (le petit luminaire et son contour pointillé passent dessus) | gardé |
| `schema.png` | schéma de l'article `schema-hauteur-lustre-salon-plafond-2-50-m.webp`, recadré x ≥ 320 : **la personne dessinée est une femme, le profil l'interdit, elle est hors du fichier** ; libellés « 35 cm » et « 2,15 m » effacés (repeints au fond), flèche des 2,15 m retracée sur 59 px | canapé, plafonnier, flèches et pointillé intacts | gardé |
| `domia-dome.png` | photo boutique Domia-5, découpe de la coupole tracée à la main | coupole entière, câble coupé à 14 px au-dessus | gardé |
| `domia.webp`, `soir.webp`, `orive.webp` | photos boutique (CDN Shopify, URL dans le manifeste) | Domia-5 salle à manger de jour ; Ornela/Orvane le soir (photo de l'article) ; Orive-1 six globes sur fond neutre ; personne, aucun texte, aucune marque | gardé |
| `musique-boucle.flac` | « Happy Guitar », edtijo, CC0 1.0, https://freesound.org/people/edtijo/sounds/207558 (bibliothèque de l'atelier) ; une portée de 65 s de la piste tournée pour que la fin rejoigne le début (`gen/musique_boucle.py`) | licence lue dans `library/audio/CATALOGUE.md` ; niveau stable (écart 2,4 dB) | gardé |
| polices | Fraunces, Newsreader (fontsource, profil) | | gardé |

Aucune image fabriquée par le générateur : le concept tient sur les photos et le schéma de la boutique, plus le dessin par code.
Musique : aucun palmarès lu ce soir (temps donné à la voix) : piste choisie sur l'humeur (guitare acoustique enjouée, conseil
dynamique) et sur sa régularité de niveau, nécessaire à la boucle.


## Les plans (temps copiés de `assets/mots.json`, prise 4 remise au rythme, pauses 0,27 s)

Chaque plan démarre 4 images avant son premier mot ; chaque mot affiché tombe 2 images avant d'être dit ; les sous-titres
portent tous les autres mots (Newsreader 600, 68 px, ligne de base ≈ 1 215, encre claire avec voile sombre sur photo, encre
sombre sur papier). Plans de plus de 3 s : chacun a trois états ou plus sur des mots dits (s1 4,1 s : rétrécit, titre, montée
au plafond ; s5 5,0 s ; s7b 5,7 s : deux phrases sur le même objet ; s10 5,0 s : grossit, anneaux, noir et titre).

| Plan | Début (s) | Durée hôte (s) | Famille | Entrée | Ce que le plan fait comprendre |
|---|---|---|---|---|---|
| s1 | 0.00 | 4.10 | A | boucle (identique à la dernière image) | le plafonnier rétrécit à 38 % dans son salon, son vrai contour reste en pointillé : « trop petit » se voit avant d'être lu ; « trop petit » 170 px ; la caméra monte au plafond sur « plafond » |
| s2 | 4.10 | 1.87 | F | partage d'écran (le haut garde l'image de S1, le bas monte) | en haut le petit, en bas le même plafonnier ×2 qui écrase la pièce (×2,32 et la pièce tassée de 6 % sur « écrase ») |
| s3 | 5.97 | 3.45 | B | zoom traversant | le mètre ruban se déroule (6 px or vif, graduations) ; « 3 » à 420 px sur « trois », « juste » en italique, point d'or au milieu du mètre |
| s4 | 8.97 | 4.13 | G | rideau depuis la ligne du mètre | règle 1 : le salon vu de dessus se dessine trait par trait, ses deux côtés se cotent sur « longueur » et « largeur » |
| s5 | 13.10 | 4.98 | B | zoom traversant | la formule se construit sur les mots : (L + l), « en mètres », « × 8 » à 320 px sur « huit », « = … cm » |
| s6 | 17.80 | 4.28 | E | filé vertical | 5 m et 4 m claquent sur leurs mots, 9 × 8, le compteur s'arrête à 72 sur « soixante-douze » ; l'anneau de 72 cm se dessine à l'échelle dans le plan |
| s7 | 21.63 | 4.10 | C | inondation née de l'anneau des 72 cm | le salon du soir : la pièce s'assombrit autour du plafonnier sur « point fort », « × 10 » puis « 90 cm » |
| s7b | 25.73 | 5.73 | D | zoom traversant | Orive (six globes, structure ouverte) : le trait coté mesure hors tout, « bras compris », puis s'allonge de 12 % sur « une taille au-dessus » |
| s8 | 30.87 | 4.07 | C | filé horizontal (fondu musical de 0,4 s caché dessous) | règle 2 : Domia au-dessus de la table, l'emprise de la coupole tombe en pointillé sur la table, « 2/3 de sa largeur » |
| s9 | 34.93 | 4.37 | E | zoom traversant | la table de 90 cm dessinée, ses tiers, la coupole de 60 cm (2/3) se déploie sur « Soixante » ; « 60 cm max » |
| s10 | 39.30 | 5.04 | C | zoom inverse | la même salle en miroir : la coupole grossit ×2,6, son emprise déborde sur les chaises (anneaux sur « convives ») ; la pièce s'éteint à 26 %, « suis toujours la table » |
| s11 | 44.07 | 4.17 | G | filé vertical | règle 3 : le schéma de l'article (sans la personne), la hauteur 2,50 m se trace à droite, « ÷ 5,5 » |
| s12 | 48.23 | 4.03 | E | zoom traversant | zoom sous le plafond : « 2,50 m », la bande hachurée des 45 cm descend du plafond, compteur jusqu'à 45, « max » |
| s13 | 52.27 | 2.67 | G | zoom inverse | recul, schéma en miroir : la bande des 2,15 m de passage monte du sol ; les deux bandes se chevauchent |
| s14 | 54.93 | 3.17 | E | zoom traversant | PLAN SIGNATURE : la bande des 45 cm se rétracte à 35 cm (0,18 s) juste avant « trente-cinq » ; « 35 cm », « platine comprise » avec son trait vers la platine ; battement calme avant |
| s15 | 58.10 | 2.55 | B | inondation de couleur sur place | le noir envahit le schéma : « 45 cm » barré, « 35 cm » grossit ; montée puis impact sur « l'emporte » |
| s16 | 60.20 | 3.13 | H | inondation depuis le centre | les trois calculs en liste sur le salon flou et sombre, puis ils sortent et la mise au point revient sur le salon |
| s17 | 63.33 | 1.67 | A | mise au point (même image, coupe invisible) | le salon de l'image 0, plafonnier à sa vraie taille, la caméra atteint l'échelle 1 à la dernière image, la promesse « Le bon luminaire, du premier coup » en bas |

## Registre des coutures
Tous les plans s'enchaînent par un mouvement causé par l'écran ; aucune coupe sèche, aucun fondu enchaîné.
Zoom traversant 6 (s3, s5, s7b, s9, s12, s14 : 33 %), filés 3 (s6, s8, s11), zoom inverse 2 (s10, s13), inondation 3
(s7 depuis l'anneau, s15 couleur sur place, s16), rideau 1 (s4), partage 1 (s2), mise au point 1 (s17), boucle 1 (s1).
Un zoom répond à un zoom (s3→s4 rideau mis à part) ; la caméra n'est jamais ramenée à 1,0 sur une coupe (sauf l'image 0, qui
est la suite exacte de la dernière image).

## Son
- Voix : prise 4 (Algieba ×1,2), consigne d'intonation moment par moment ; mesure d'intonation de l'atelier : 25 phrases « ok »,
  aucune plate ; « Deux. » trop court pour être jugé. La voix dit la phrase jusqu'à « ton lustre est sûrement trop petit »
  et le clip est coupé à 64,535 s, juste avant « ton » (fondu de 30 ms) : « que » garde l'intonation d'une phrase qui continue.
- Musique : `musique-boucle.mp3`, piste jouée de 47,00 à 77,87 s puis de 12,87 à 47,00 s ; fondu de 0,4 s à 30,87 s sous le filé
  de s8 ; la dernière seconde rejoint la première sans couture. Niveaux écrits par `lit_musique.py` (cible 11,7 dB sous la voix,
  plancher 10 dB par groupe, écart entre groupes 3 dB, copie locale réglée : l'outil livré refusait deux groupes à 9,5 dB) puis
  vérifiés par `lit_musique.py --verifier` : voix 10,4 à 15,6 dB au-dessus de la musique, passage sans voix final 7,3 dB sous la
  voix (porte 8). La voie de volume finit à la valeur de l'image 0 (0,747) : remontée de 0,36 à 0,747 dans les 0,46 s après « que ».
- Effets : 53, banque earshot, placés par `place_effets.py` ; aucun pic à moins de 0,15 s d'un autre, aucun pendant un nombre dit
  (les accents des chiffres sont dans les pauses).
