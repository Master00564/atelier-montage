# SPEC — « Ton lustre est sûrement trop petit » (film à thème, 65 s, boucle)

## Format
1080 x 1920, 30 fps, exactement 65,000 s (1 950 images ; règle d'Ali du 17/11 : une vidéo à thème dure 65 s). Boucle parfaite : l'image 1949 précède l'image 0 sans coupure visible.

## LOOK (profil atelier-du-lustre)
- Fonds : papier `#faf7f1` (schémas, formules), sombre `#14110e` (photo assombrie à 25 % sous un mot).
- Encre : `#14110e` sur fonds clairs ; `#faf7f1` sur fonds sombres.
- Accents : vif `#c9a15a` uniquement sur fond ou photo sombre ; sombre `#7d6128` sur fond clair (traits 6 px minimum).
- Gris secondaire `#4d463d` (graduations, légendes à 4,5:1 sur papier : 9,6:1).
- Familles : Fraunces (chiffres, mot héros, italique pour un seul mot par scène) ; Newsreader 600 (sous-titres, étiquettes).
- Matière : papier à 3 % de grain (tuile statique sur les fonds papier, pas de grain animé sur tout le film : le poids du fichier de 60 s), traits fins dans l'accent qui convient au fond, ombres douces, aucun halo sur les mots ni les traits.

## Le fil : le trait coté
Un trait doré à deux taquets (6 px, taquets 28 px, extrémités arrondies) mesure chaque chose : le plafonnier, le plan du salon,
la table, la hauteur sous plafond. Il se dessine (`strokeDashoffset`, 0,5 à 0,9 s, `power2.inOut`), une tête ronde de 14 px en tête de trait.

## Nombres
- Chiffre héros : Fraunces 600, 300 à 420 px (16 à 22 % de la hauteur) sur papier ; 150 à 220 px sur photo.
- Mot héros : Fraunces 600, 150 à 190 px ; mots secondaires 54 à 64 px.
- Sous-titres : Newsreader 600, 68 px, ligne de base y 1215 (haut du bloc 1150), marges x 96 à 984, groupes de 1 à 4 mots coupés aux pauses.
- Promesse « Le bon luminaire, du premier coup » : Newsreader italique 500, 44 px, y 1285, encre, uniquement sur le plan de la boucle (2 premières et 1,5 dernière seconde).

## Mouvement (moteur.md)
- Entrées 0,12 à 0,4 s `expo.out` / `power4.out` ; sorties 40 à 50 % plus courtes `power3.in` ; caméra `none` ou `power2.inOut`.
- Caméra jamais arrêtée : poussée de 4 à 8 % ou dérive de 20 à 40 px par plan, jamais remise à 1,0 à une coupe.
- Coup de zoom (punch) : 1 → 1,18 en 4 images, 0,4 s minimum entre deux mouvements forts.
- Écarts de cascade inégaux (table fixe : 0,07 / 0,09 / 0,06 / 0,1 s).
- Chiffres : comptage 0,8 à 1,2 s, arrêt sur le mot dit ; écrasement 130 → 100 % en 6 images quand le mot tombe moins de 0,9 s après le début de la scène.

## Boucle
- Images 0 et 1949 : même photo (salon de jour, plafonnier Orvane à sa vraie taille), même cadrage, même caméra (échelle 1,000 atteinte à 65,0 s en poussée linéaire de 0,0227/s, poursuivie de 1,000 à 1,05 de 0 à 2,2 s), même promesse en bas.
- Son : la musique (Happy Guitar, 126 BPM mesurés) est tournée : la piste est jouée de 45 à 78 s puis de 13 à 45 s (fondu enchaîné de 0,4 s au milieu, sous un mouvement), si bien que la fin (45 s de piste) se raccorde à son propre début ; ni fondu d'entrée ni fondu de sortie (seuil `fondu_fin_min_s` mis à 0 dans le manifeste, raison : boucle). La voix finit sur « que… » et reprend sur « Ton lustre ».
