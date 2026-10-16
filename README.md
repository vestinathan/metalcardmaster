# Metal Card Master

App de cartes à collectionner façon WikiMasters/Pokémon TCG Pocket, sur le thème du metal.

## Déploiement sur Vercel

1. Va sur [vercel.com/new](https://vercel.com/new) et importe ce repo GitHub.
2. Déploie — aucune configuration nécessaire. Vercel détecte automatiquement `index.html`
   (statique) et `api/bandimage.js` (fonction serverless).

Pas de clé API, pas de compte développeur, pas de variable d'environnement à configurer :
les images viennent de Wikipedia/Wikimedia, dont les endpoints sont publics.

## Développement local

```bash
npm i -g vercel
vercel dev
```

## Structure

- `index.html` — l'app complète (une seule page, HTML/CSS/JS)
- `api/bandimage.js` — fonction serverless qui cherche la page Wikipedia d'un groupe (FR puis
  EN en repli) et retourne son image d'infobox (photo ou logo selon la page)

## Notes sur les images

Les images viennent de l'infobox Wikipedia de chaque groupe, qui est le plus souvent la photo
ou le logo officiel utilisé sur la page. Le statut de licence exact de chaque image est visible
sur sa page Wikimedia Commons (lien généralement accessible depuis la page Wikipedia du groupe).
