# atelier-video

L’atelier de montage vidéo de Claude, installé chez GitHub. Claude y fabrique les vidéos animées
(reels produit, 1080 × 1920) sur les ordinateurs gratuits de GitHub, pas sur ton PC.

## Ce que ça fait

1. Claude écrit une « commande de vidéo » : le texte, la photo, la musique, les couleurs.
2. Il demande à GitHub de la fabriquer. Ça prend environ 1 à 2 minutes pour une vidéo de 5 secondes.
3. GitHub vérifie la vidéo (bonne taille, son présent, image pas noire, ça bouge), puis la garde 3 jours.
4. Claude la télécharge où il veut : un ordinateur, ou une session Claude en ligne.

Deux moteurs, au choix pour chaque vidéo :

- **Remotion** : celui qu’on utilise déjà pour les reels (`projets\reels-atelier` sur ton PC).
- **HyperFrames** : le moteur gratuit de HeyGen, avec plus de 400 effets et transitions prêts.

La liste complète de ce que chaque moteur sait faire : [docs/fonctionnalites.md](docs/fonctionnalites.md).

## Ce que ça coûte

0 €. Le compte GitHub gratuit donne 2 000 minutes par mois pour tous les robots privés (le robot qui
transcrit la formation SMP en prend environ 30 par jour). Une vidéo de 5 secondes en coûte 1 à 2.
Aucun compte HeyGen, rien de payant, aucune donnée envoyée à HeyGen.

## Où regarder

- Les vidéos fabriquées : https://github.com/Master00564/atelier-video/actions (clique sur une ligne,
  puis tout en bas, « Artifacts »).
- Les commandes de vidéo enregistrées : dossier [jobs](jobs).

Le mode d’emploi technique pour Claude est dans [AGENTS.md](AGENTS.md).
