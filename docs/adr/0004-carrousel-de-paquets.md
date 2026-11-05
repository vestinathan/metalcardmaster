# ADR-0004 : Carrousel de paquets et déchirure à l'ouverture

## Statut
**Validé et déployé** (2026-11-05). Les maquettes puis l'aperçu intégré ont été validés par l'utilisateur sur iPhone ; poussé sur `main`.

## Contexte
La vue Paquets affichait une étagère avec un seul paquet (image à plat, `images/packs/metalcardmaster-pack.webp`),
et l'ouverture passait par un écran « paquet fermé » (`#packClosed`) puis un tap. Objectif : un choix de paquet
plus vivant (carrousel), un paquet qui réagit à la lumière, et une vraie déchirure à l'ouverture, sans changer le
tirage ni le stock serveur.

## Décision
- **Carrousel 3D en CSS pur** (`.pk-stage` / `.pk-ring` / `.pk-slot`) : glisser avec inertie et calage sur le paquet le
  plus proche, tap sur un paquet de côté pour l'amener devant, points et flèches clavier. Pas de WebGL ni de build
  (ADR-0001). Un dépôt de référence (`qbaok62/gacha-card-game`, React + three.js) a été examiné et écarté : ~270 lignes de
  prototype (anneau de plans rouges), aucune logique de cartes, et une chaîne de build incompatible avec l'ADR-0001.
  Seule l'idée « anneau + inertie + calage » est reprise.
- **L'image réaliste du packshot reste la base** (plis du foil, forme, soudures). Une version entièrement redessinée en
  CSS a été essayée puis rejetée : trop « propre », moins réaliste que l'image. Les effets se posent par-dessus :
  - `.pk-fx-sheet` / `.pk-fx-spot` : feuille de métal (`overlay`) et tache de lumière (`soft-light`), **découpées selon
    l'alpha de l'image** avec `mask-image` (aucun débordement hors de la silhouette) ;
  - `.pk-win` : la photo de la fenêtre rejouée **au-dessus** des effets, pour qu'elle reste nette, avec un léger éclat de
    vitre (`.pk-glass`) ;
  - `.pk-logo` : un reflet rouge puis blanc qui traverse la silhouette du logo (`images/packs/pack-logo-mask.png`),
    transparent au repos pour ne pas doubler le logo de l'image.
- **Paquet vivant** : une seule boucle `requestAnimationFrame` (`pkFrame`) qui ne travaille que si la vue Paquets est
  affichée et l'écran d'ouverture fermé. Chaque paquet reçoit `--bx/--mx/--my/--o/--tx/--ty` selon sa position sur
  l'anneau ; le paquet de face se balance doucement (rien si `prefers-reduced-motion`).
- **Déchirure** : le paquet est rendu en deux copies de la même face (`.pk-bottom`, `.pk-top`), découpées par une ligne
  en dents de scie commune (`pkTear`, le haut descend de 0,3 % pour éviter un liseré). Séquence : tremblement (0,5 s,
  pendant l'appel `consume_pack`) → le haut s'envole + flash → trois dos de carte sortent → fondu vers l'écran
  d'ouverture (`#opening`) qui garde le flash et la révélation existants.
- **Écran « paquet fermé » supprimé** (`#packClosed`, `.pc-*`, éclats `.tear-spark`, reflet `--holo-x`) : plus
  atteignable. `#tearFlash` est conservé pour la transition vers la première carte.

## Ce qui n'a PAS changé
- Tirage (`pickPack`, `RARITY_DROP_WEIGHTS`, `GUARANTEED_SLOT_RARITIES`, `PACK_SIZE`) : intact. Ne jamais l'ajuster via
  `influence` (ADR-0002).
- Stock serveur (`refill_pack_stock`, `consume_pack`, `PACK_KINDS = ["all"]`, compte à rebours, refus à `-1`) :
  mêmes appels, mêmes textes (« 5 cartes · disponible », « Prochain paquet dans … », pastille « n/4 »).
  `renderPackStock(kind)` et `showPackRefusedMessage()` pilotent maintenant le carrousel au lieu de l'étagère.

## Éditions
`PACK_EDITIONS` (dans `index.html`) liste les paquets du carrousel. **Seul `metalcardmaster` (`kind: "all"`) s'ouvre.**
Black Metal, Thrash Metal et Heavy Metal sont des paquets **verrouillés « Bientôt disponible »** (`soon: true`), sans
stock ni tirage : Thrash et Heavy sont des exemples montés sur le packshot Metal Card Master (photo de groupe
`images/bands/*-photo.jpg` + titre et badge recomposés en CSS). Les rendre réellement ouvrables demande un `kind` connu
des RPC Supabase (`refill_pack_stock`, `consume_pack`), qui ne sont pas dans ce dépôt, et un filtre de pool dans
`pickPack`. Pour retirer les teasers : ne garder que la première entrée.

## Assets
`images/packs/` : `metalcardmaster-pack.webp`, `blackmetal-pack.webp` (bases), `metalcardmaster-window.webp` (photo de la
fenêtre, recadrée du packshot, 2 px à l'intérieur du cadre rouge), `pack-logo-mask.png` (silhouette du logo, alpha).
La géométrie fenêtre / logo (en % du paquet) est dans les règles `.pk-face[data-base="…"]` : **une nouvelle image de base
demande ses propres valeurs**.

## Pièges
- `ev.target` d'un `pointerup` est le conteneur après `setPointerCapture` : la cible du tap est mémorisée au
  `pointerdown` (`pkDownSlot`).
- `mix-blend-mode` d'un enfant d'un élément masqué ne fusionne qu'à l'intérieur du masque : les deux couches de reflet
  sont donc deux éléments masqués, chacun avec son propre `mix-blend-mode`.
- `.pk-carousel` utilise `overflow-x: clip` (Safari 16+) pour que les paquets de côté ne créent pas de défilement
  horizontal.

## Tests
Serveur local + Playwright (420×860, Supabase et Google Fonts bloqués, écran de connexion masqué) : sélection par glisser
et par tap, verrouillage des éditions « bientôt », ouverture complète (tremblement, déchirure, cartes, révélation des 5
cartes avec `window.__forcePack`), retour à l'album puis retour sur Paquets (paquet refermé, bouton actif), pas de
défilement horizontal. **Non testé** : iPhone réel (fluidité de la boucle avec les masques, `mask-image` sur Safari),
état « stock épuisé » avec un vrai serveur, polices Anton / Pirata One (bloquées pendant les tests).

## À faire / ouvert
- Les dos de carte qui sortent du paquet sont provisoires (logo sur fond sombre).
- La photo de la fenêtre Metal Card Master vient d'un packshot de 362 px de large : à remplacer par une version haute
  résolution si elle existe.
- Décider des éditions réelles (voir plus haut).
