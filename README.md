# Metal Card Master

App de cartes à collectionner façon WikiMasters/Pokémon TCG Pocket, sur le thème du metal.

## Déploiement sur Vercel

1. Va sur [vercel.com/new](https://vercel.com/new) et importe ce repo GitHub.
2. Déploie — aucune configuration nécessaire. Projet 100% statique (`index.html` +
   `images/bands/`), pas de fonction serverless, pas de clé API, pas de variable
   d'environnement.

## Développement local

Ouvre simplement `index.html` dans un navigateur, ou sers-le avec n'importe quel serveur
statique (`python3 -m http.server`, `npx serve`, etc.).

## Structure

- `index.html` — l'app complète (une seule page, HTML/CSS/JS)
- `images/bands/` — photos et logos de groupes, téléchargés une fois et stockés localement
  (voir ci-dessous)

## Images de groupe

Les photos et logos des groupes ont été récupérés une fois via [TheAudioDB](https://www.theaudiodb.com/)
(photo de groupe posée + logo vectoriel officiel), avec repli sur Wikipedia quand un groupe
n'y est pas référencé, puis stockés localement dans `images/bands/` — pas d'appel réseau au
runtime, donc pas de dépendance à la disponibilité de ces services pour les utilisateurs de
l'app.

Pour un groupe sans image trouvée nulle part (cas de groupes très confidentiels), l'app
retombe automatiquement sur un visuel généré (typographie stylisée + palette dérivée du style
musical) — voir `genBandLogo` dans `index.html`.

### Ajouter un nouveau groupe

1. Ajoute l'entrée dans le tableau `CARDS` (dans `index.html`), sans `photo`/`logo` pour
   l'instant.
2. Pour lui trouver une image : cherche l'artiste sur `https://www.theaudiodb.com/api/v1/json/123/search.php?s=NomDuGroupe`,
   récupère `strArtistThumb` (photo) et `strArtistLogo` (logo), télécharge-les et place-les
   dans `images/bands/<id>-photo.jpg` et `images/bands/<id>-logo.png`.
3. Ajoute les chemins dans l'entrée `CARDS` correspondante (`photo: "images/bands/<id>-photo.jpg"`, `logo: "images/bands/<id>-logo.png"`).
4. Si TheAudioDB ne trouve rien, essaie l'API REST Wikipedia (`https://fr.wikipedia.org/api/rest_v1/page/summary/NomDuGroupe`,
   champ `originalimage.source` ou `thumbnail.source`) pour au moins une photo.
5. Si rien n'est trouvé, laisse `photo`/`logo` absents : le fallback généré prendra le relais
   automatiquement.
