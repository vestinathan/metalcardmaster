# ADR-0005 : Fin de paquet — badge « New » et récap des cartes

## Statut
**Validé et déployé** (2026-11-05), après essais sur iPhone.

## Contexte
La révélation s'arrêtait sur la dernière carte avec un simple bouton « Retour à l'album ». Rien n'indiquait si une carte
était nouvelle ou un doublon (le compteur « x2 » n'apparaissait que plus tard dans l'album), et il n'y avait pas de vue
d'ensemble du paquet.

## Décision
- **Nouveau / doublon décidé avant l'ajout à l'inventaire.** `computePullInfo()` (appelé dans `proceedWithOpening`, juste
  après `pickPack`) mémorise pour chaque carte `{ isNew }` à partir de `ownedCount()` *avant* que
  `finalizePackIfDone()` n'appelle `addOwned()` (ce qui arrive dès que la dernière carte s'affiche). Deux exemplaires de la
  même carte dans un paquet : seul le premier est « new ». Le tirage et la sauvegarde ne changent pas.
- **Pastille sur la carte révélée** (`showCardTag`) : une seule pastille posée dans `.stage` (jamais dans `.reveal-card`,
  donc pas de canvas de plus ni d'interférence avec le tilt), en **coin haut-droit** de la carte, légèrement inclinée :
  « NEW » (orange, anneau qui s'étend), **uniquement pour une nouvelle carte** : un doublon ne porte aucune pastille (un
  badge « ×n » avec compteur qui roule a été essayé puis retiré à la demande de l'utilisateur).
  Elle apparaît après le flip (~0,7 s ; ~1,5 s pour la fumée des légendaires) avec une légère vibration
  (`navigator.vibrate`, ignorée sur iOS). Le premier essai (« NOUVELLE CARTE » centré sur le bord haut) a été rejeté.
- **Récap** (`showRecap`) : un tap sur la dernière carte fait fondre la scène, puis les cartes du paquet arrivent en
  cascade, en grille 3 + 2, avec le badge NEW sur les nouvelles cartes. « Retour à l'album » reste disponible dès
  la dernière carte (on peut sauter le récap). Le bilan chiffré (« x nouvelles cartes · x doublons ») et le compteur
  « Collection x / total » ont été essayés puis retirés à la demande de l'utilisateur.
- **Vraies cartes dans le récap** : chaque tuile est un `buildRevealCard()` (même design que la révélation et le zoom), bâti
  à 300 px puis réduit par `transform: scale()` (`--sc`, calculé en JS). metallicss et `fitCardMoves` sont appliqués une
  fois la tuile dans le DOM. Le récap est statique (aucun tilt, `pointer-events: none`) et les animations infinies des
  reflets sont mises en pause (`.rcp-card *`) : 5 cartes complètes à l'écran, c'est le point à surveiller sur iPhone (des
  cartes holographiques empilées ont déjà fait ramer, voire planter, Safari ; voir `populateMiniCard` /
  `revealCurrentCard`). Si ça pèse : repasser à des tuiles légères (photo + nom) pour les seules cartes sans holo.
- **Sortie du récap** : bouton « ✕ » fixe en haut à droite (`.rcp-x`, zone de sécurité respectée) en plus de « Retour à l'album ». Sur un écran trop court, l'overlay défile (`.opening.recap-mode { overflow-y: auto }`) au lieu de couper le bouton.
- `prefers-reduced-motion` : plus d'animation, la pastille s'affiche directement.

## Ce qui n'a PAS changé
Tirage (`pickPack`, `RARITY_DROP_WEIGHTS`, `GUARANTEED_SLOT_RARITIES`), stock serveur, ajout à l'inventaire et sauvegarde
(`finalizePackIfDone`), flip et fumée des cartes.

## Pièges
- `finalizePackIfDone()` s'exécute à l'affichage de la dernière carte, pas au tap suivant : tout calcul « avant / après »
  doit se faire avant (`pullInfo`).
- `nextCard()` incrémentait `pullIndex` au-delà de la dernière carte ; il est maintenant ramené sur la dernière carte.
- `clearRecap()` doit être appelé à la fermeture et au début d'une nouvelle ouverture (stage remis, fondu retiré, minuteries).

## Tests
Serveur local + Playwright (420×860) avec `window.__forcePack` : nouvelle carte, doublons sans pastille, indice
« Toucher pour voir le récap du paquet » sur la dernière carte, récap (éventail, badges, bilan, compteur de collection),
retour à l'album, deuxième ouverture normale. **Non testé** : iPhone réel (charge de 5 cartes complètes), paquet sans nouvelle carte.

## À faire / ouvert
- Tap sur une tuile du récap pour l'agrandir (réutiliser `openCardZoom`).
- Un bouton « Ouvrir un autre paquet » dans le récap.
- Son / vibration plus travaillés à l'ouverture.
