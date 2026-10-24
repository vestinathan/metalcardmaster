# Metal Card Master

App mobile de cartes à collectionner façon WikiMasters/Pokémon TCG Pocket, sur le thème du
metal. Projet 100% statique, déployé automatiquement sur Vercel à chaque push sur `main`
(repo GitHub `vestinathan/metalcardmaster`).

## Architecture

- **`index.html`** — l'app entière : HTML + CSS + JS dans un seul fichier (~460 Ko). Pas de
  build step, pas de framework. C'est un choix délibéré pour la simplicité de déploiement,
  mais ça veut dire que le fichier est gros et que les diffs peuvent être bruyants — voir
  "Conventions de travail" ci-dessous.
- **`images/bands/`** — photos/logos téléchargés une fois (TheAudioDB, repli Wikipedia),
  stockés localement. Pas d'appel réseau au runtime.
- Pas de backend, pas de base de données, pas de clé API, pas de variable d'environnement.

## Modèle de données (tableau `CARDS` dans `index.html`)

275 cartes au total (groupes + musiciens individuels). Chaque carte :
```js
{
  id, name, genre, country,
  rarity: "commune" | "rare" | "ultra_rare" | "legendaire",
  influence: 0-100,   // score numérique, détermine la rarity via des seuils
  views, photo, logo, founded,
  hit: { title, year }, bio,
  // pour un musicien individuel uniquement :
  type: "musician", band: "<id-du-groupe>"
}
```

**Seuils rarity ↔ influence** (empiriques, voir ADR-0002) :
`commune < 42` · `rare 42-63` · `ultra_rare 64-85` · `legendaire 86+`

## Deux mécanismes à NE JAMAIS confondre

1. **`influence` par carte** — doit refléter l'influence réelle de l'artiste/groupe dans le
   monde, de façon cohérente et reproductible. **Ne jamais l'ajuster pour équilibrer la
   distribution des packs.** Voir ADR-0002.
2. **`RARITY_DROP_WEIGHTS`** (ligne ~3181) et **`GUARANTEED_SLOT_RARITIES`** (ligne ~3182) —
   seul endroit où la distribution de rareté dans les packs doit être ajustée.
   `PACK_SIZE = 5`.

Ces deux sujets sont **strictement séparés**. Un score d'influence élevé qui "déséquilibre"
la pyramide de rareté n'est pas un problème à corriger sur la carte — voir ADR-0002 pour le
raisonnement complet.

## Conventions de travail

- **Toujours montrer un diff/récap avant de push** quand on touche au scoring des 275 cartes
  (`CARDS`) — changement sensible et difficile à auditer après coup dans un fichier de cette
  taille. Pour les fixes UI/UX ponctuels, une confirmation verbale explicite suffit.
- Tester avec un serveur local (`python3 -m http.server`, port libre) + Playwright
  (`executable_path='/opt/pw-browsers/chromium'`, viewport 420×860) pour vérifier visuellement
  avant de push, en particulier les animations de reveal de pack.
- Commits atomiques et messages en français, descriptifs (voir `git log` pour le style).
- Ne jamais committer de clé API ou credential, même de test — aucun n'est nécessaire pour ce
  projet (100% statique).

## Historique des décisions

Voir `docs/adr/` pour le détail des choix structurants et pourquoi certaines approches ont
été essayées puis rejetées (notamment la méthodologie de scoring d'influence, qui a connu
plusieurs itérations).
