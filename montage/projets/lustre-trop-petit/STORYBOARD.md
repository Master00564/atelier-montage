# STORYBOARD — « Ton lustre est sûrement trop petit »

Film à thème (genre `theme`), 1080 x 1920, 30 fps, **65 s exactement** (règle d'Ali du 17/11, profil `formats.theme`),
en **boucle parfaite** (règle d'Ali du 17/11 transmise par la session principale : la dernière image redevient la première,
la dernière phrase inachevée se raccorde à la première). Voix Algieba ×1,2, texte relu par `style-humain`.
Sujet : l'article de la boutique (taille-lustre-salon). **v2, règles d'Ali du 17/11** : chaque chiffre dit est vérifié sur deux sources ou plus (`sources.md`), toutes les images qui portent la voix sont faites pour le film (dessin animé par code) sauf les photos des produits de la boutique ; une phrase envoie vers le guide du site avant le raccord de boucle.

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
À la fin de « Il te reste alors », la bande hachurée des 62 cm sous le plafond se rétracte à 37 cm en 0,18 s (`power4.out`),
caméra à l'échelle 2,0 sur le schéma dessiné (x 1,02 sur le plan), « 37 cm » à 300 px claque 2 images avant « trente-sept ».
Montée (`riser`) puis impact (`hit`) sur la rétraction, entre deux mots. Battement calme déclaré juste avant : la caméra presque
immobile (+2 % sur tout le plan) pendant 0,5 à 0,9 s après l'entrée.

## Courbe d'énergie
Pic d'entrée (0-6 s : rétrécit, écrase, mètre ruban), règle 1 claire et chiffrée (9-31 s), règle 2 (31-45 s, la suspension qui
déborde), règle 3 qui monte (45-58 s) jusqu'au plan signature vers 85 % du film, puis rappel des trois calculs et retour au salon
de l'image 0 (la boucle).

## Matériel (chaque pièce vue en entier puis par zones)
| Fichier | Source | Vérifié | Verdict |
|---|---|---|---|
| `jour-lampe.png`, `jour-plaque.png` (+ copies `-2`) | photo produit Orvane-2 (CDN Shopify), découpe tracée à la main, plafond rebouché par code | diffuseur gardé entier ; plaque jamais vue nue | gardé |
| `orvane-soir.webp` | photo produit Orvane-3 (soir, séjour) | fixture entier, aucune personne, aucun texte | gardé |
| `tressa-soir.webp` | photo produit Tressa-3 (raphia, soir, séjour) | idem | gardé |
| `domia.webp`, `domia-dome.png` | photo produit Domia-5, coupole détourée à la main | coupole entière | gardé |
| schéma de hauteur | **dessiné par code** (plafond hachuré, sol, ligne des 2,13 m, canapé, plafonnier), plus aucune image de l'article | aperçu vérifié avant envoi | gardé |
| `musique-boucle.mp3` | « Happy Guitar », edtijo, CC0 1.0, tournée pour la boucle (47,00→72,77 s puis 7,77→47,00 s, fondu 0,4 s sous le filé de 25,77 s) | licence dans `CATALOGUE.md` | gardé |

Aucune image générée par IA : les dessins (plan, formules, table, schéma de hauteur, porte, contours) sont faits par code ; les photos sont celles des produits de la boutique.
Musique : aucun palmarès lu ce soir (temps donné à la voix) : piste choisie sur l'humeur (guitare acoustique enjouée, conseil
dynamique) et sur sa régularité de niveau, nécessaire à la boucle.


## Les plans (temps copiés de `assets/mots.json`, prise v2 en 12 segments, pauses 0,30 s)

| Plan | Début (s) | Durée hôte (s) | Famille | Ce que le plan fait comprendre |
|---|---|---|---|---|
| s1 | 0.00 | 7.30 | A | le plafonnier de la boutique (Orvane) rétrécit à 38 % dans son salon ; « trop petit » ; son vrai contour en pointillé sur « erreurs » ; la caméra monte au plafond sur « plafond » |
| s2 | 7.30 | 1.87 | F | en haut le petit, en bas le même plafonnier ×2 qui écrase la pièce |
| s3 | 9.17 | 3.48 | B | le mètre ruban se déroule ; « 3 règles », « juste » |
| s4 | 12.20 | 3.77 | G | règle 1 : le salon vu de dessus se dessine, ses deux côtés se cotent |
| s5 | 15.97 | 2.71 | B | la formule : (L + l), en mètres, « × 8,3 », « = … cm » |
| s6 | 18.40 | 3.17 | E | 5 m et 4 m claquent, (5 + 4) × 8,3, compteur jusqu'à 75 ; l'anneau de 75 cm à l'échelle dans le plan |
| s7 | 21.00 | 5.37 | C | Orvane allumé le soir (photo boutique) : une porte dessinée, « porte standard : 73 cm » ; « minimum » ; sur « plus grand », un contour pointillé s'agrandit de 28 % et la caméra avance |
| s8 | 25.77 | 4.83 | G | règle 2 : Domia au-dessus de la table, son emprise en pointillé, « 2/3 de sa largeur » |
| s9 | 30.33 | 5.63 | E | la table de 90 cm dessinée, la coupole de 60 cm (2/3), « 60 cm max », « = 90 − 30 » |
| s10 | 35.97 | 2.34 | C | la même salle en miroir : la coupole grossit ×2,6 et déborde sur les chaises (anneaux sur « convives ») |
| s11 | 38.03 | 4.25 | G | règle 3 : le schéma dessiné (plafond, canapé, plafonnier), la hauteur 2,50 m se trace, « 1/5 à 1/4 » |
| s12 | 42.17 | 5.17 | E | zoom sous le plafond : « 2,50 m », « la hauteur standard en France », la bande de 62 cm (trait à 52 cm), « 52 à 62 cm » |
| s13 | 47.33 | 2.10 | G | recul, schéma en miroir : la bande des 2,13 m de passage monte du sol, les bandes se chevauchent |
| s14 | 49.43 | 3.13 | E | PLAN SIGNATURE : la bande de 62 cm se rétracte à 37 cm juste avant « trente-sept » ; « 37 cm », « platine comprise » |
| s15 | 52.57 | 2.67 | B | le noir envahit le schéma : « 62 cm » barré, « 37 cm » grossit ; montée puis impact sur « l'emporte » |
| s15b | 54.63 | 5.64 | K | Tressa allumé dans son salon (photo boutique) : « plafonnier », puis « Quelle taille de lustre pour un salon ? », « Le guide complet sur latelierdulustre.com » |
| s16 | 59.57 | 3.23 | H | les trois calculs en liste sur le salon flou, puis la mise au point revient sur le salon de l'image 0 |
| s17 | 62.80 | 2.20 | A | le salon de l'image 0, la caméra atteint l'échelle 1 à la dernière image, « Le bon luminaire, du premier coup » en bas |

## Coutures
Zoom traversant (s3, s5, s9, s12, s14), filés (s6, s8, s11, s15b), zoom inverse (s10, s13), inondation (s7 depuis l'anneau des 75 cm,
s15 couleur sur place, s16), rideau (s4), partage (s2), mise au point (s17), boucle (s1). Aucune coupe sèche, aucun fondu enchaîné.

## Son
Voix : prise v2 en 12 segments (accroche « punchy, a little teasing », règles « clear and explanatory », chiffres « small spark of
surprise », appel au guide « warm, friendly invitation », raccord « rising questioning tone, clear full voice »), coupée juste avant « ton »
(63,993 s). Musique en boucle, niveaux par `lit_musique.py` (copie locale : cible 11,7 dB, plancher 10 dB, écart 3 dB, passage sans voix
final à 11 dB, seuil reporté dans le manifeste) ; `--verifier` : voix 10,6 à 17,8 dB au-dessus de la musique. 47 effets, aucun pic à moins
de 0,15 s d'un autre ni sur un nombre dit.
