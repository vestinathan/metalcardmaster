# Metal Card Master

App de cartes à collectionner façon WikiMasters/Pokémon TCG Pocket, sur le thème du metal.

## Déploiement sur Vercel

1. Va sur [vercel.com/new](https://vercel.com/new) et importe ce repo GitHub.
2. Avant de déployer (ou juste après, dans **Settings → Environment Variables**), ajoute :
   - `SPOTIFY_CLIENT_ID`
   - `SPOTIFY_CLIENT_SECRET`

   (les identifiants de ton app sur [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard))
3. Déploie. Vercel détecte automatiquement `index.html` (statique) et `api/spotify.js` (fonction serverless).

Aucune autre config nécessaire — pas de build step, pas de framework.

## Développement local

```bash
npm i -g vercel
vercel dev
```

Crée un fichier `.env.local` (non commité) à partir de `.env.example` avec tes identifiants Spotify.

## Structure

- `index.html` — l'app complète (une seule page, HTML/CSS/JS)
- `api/spotify.js` — fonction serverless qui interroge l'API Spotify (Client Credentials) et retourne la photo d'artiste ; garde le secret côté serveur
