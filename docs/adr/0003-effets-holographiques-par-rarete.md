# ADR-0003 : Effets holographiques des cartes, par rareté

## Statut
**Validé et déployé** (2026-11-04). Itérations testées par l'utilisateur sur iPhone via un aperçu privé, puis commit
et push sur `main` sur son feu vert explicite.

## Contexte
Les cartes révélées à l'ouverture d'un paquet (`.reveal-card`) doivent réagir à l'inclinaison au doigt
comme une vraie carte holographique (référence : poke-holo, `simeydotme/pokemon-cards-css`, MIT). Le
principe retenu est **physique** : les motifs sont **fixes dans la carte** et ne s'allument que lorsque
l'inclinaison les aligne avec la lumière — jamais partout à la fois, jamais sans mouvement.

## Décision : un effet par rareté
| Rareté | Effet |
|---|---|
| `commune` | aucun |
| `rare` | **uniquement** un motif de pentacles très discret sous le texte (zone `.rc-move-top` → bas de la fenêtre) ; fenêtre photo laissée libre |
| `ultra_rare` | reflets pleine carte (acier, glare, liseré chrome sur la bordure, contour autour des musiciens) + motif fin de pentacles en quinconce sur toute la carte |
| `legendaire` | mêmes reflets pleine carte, **sans motif de pentacles**, + **cadre métal brossé / chrome** + **relief sur les musiciens détourés** (parallaxe + ombre) |

Tout est piloté **par rareté** (aucune liste d'ids) : `HOLO_RARITIES` dit quelles raretés ont un effet, et
`buildRevealCard` pose `data-frame="brushed"` sur toute carte légendaire. Une nouvelle carte hérite donc
automatiquement de l'effet de sa rareté. Code : `setupHolo()` dans `index.html` (CSS `.rc-holo-*` juste au-dessus
du flip d'apparition ; règles du cadre brossé dans la section « CADRE MÉTAL BROSSÉ »).

## Règles de physique (communes)
- Inclinaison normalisée `tx, ty ∈ [-1, 1]` (position du doigt dans la carte).
- La lumière accroche du côté **opposé** à l'inclinaison : incliné à gauche → visible à droite ; doigt
  en bas → haut. Tache de lumière gaussienne autour de `0.5 - t·k`.
- Apparition et disparition **progressives** : `--card-opacity` monte vite (0.07) et retombe lentement
  (0.035, ~1 s) ; l'intensité dépend aussi de l'amplitude de l'inclinaison (`smooth`). À plat : rien.
- **Éclairs = foil réfléchissant, comme les « reverse holo » de poke-holo** (`.rc-holo-bolts`) : le motif est un
  **masque fixe** (`--bolts-mask`, un PNG calculé une fois en JS par `buildBoltMask`) et, derrière, une **feuille de
  métal** (dégradé à bandes sombres / claires) qui glisse avec `--background-x/y`. Tous les pentacles reflètent la
  même feuille : leur éclat varie de façon cohérente (noir → rouge → blanc). Une tache de lumière
  (`--spot-x/y`, posée côté opposé à l'inclinaison) est intersectée avec le motif (`mask-composite: intersect`) ;
  `--tilt-amt` et `--card-opacity` font tout disparaître à plat. Aucun dessin à chaque image (CSS pur ensuite).
- **Ultra rare : le motif reste dans la fenêtre** (`.rc-window`), jamais sur le cadre : il s'arrête au bord intérieur de la
  bande rouge. La couche `.rc-holo-bolts` est donc posée sur la fenêtre (position + rayon de coin lus sur `.rc-window`) ;
  pour les rares c'est la zone texte.
- Le masque du motif retire les musiciens (`images/masks`), et le logo, la pastille de rareté, le badge « Artiste »,
  les PV et l'ATK (`collectHoles`, mesurés en `offsetLeft/Top`, recalculés au chargement du logo).

## Paramètres retenus
- **Pentacles ultra rare** : quinconce 27×31 px, rayon ~10,5 px avec une facette atténuée (volume), feuille rouge /
  gris / blanc / noir (stops en RGB), tache large (`--spot-r: 76%`, gain `0.25 + 0.75·smooth`), aucun pointillé sur
  les bordures.
- **Pentacles rare** : tuiles plus grandes (46×50 px, rayon ~19 px), zone texte seulement, tache **étroite**
  (`--spot-r: 37%`, nulle à plat), opacité ×0.78, `mix-blend-mode: lighten` (garde le texte net), feuille
  argent / acier / gunmetal.
- **Relief légendaire** (`buildRelief` / `drawRelief`) : les musiciens sont découpés de la photo avec le
  masque `images/masks/<id>.png` (même cadrage `object-fit: cover` + `object-position` que la photo).
  Calque décalé de `±7 px × (tx, ty)` (l'avant-plan suit l'inclinaison), ombre portée floutée du côté
  opposé, et zone sombre à l'emplacement d'origine pour éviter le liseré en double contour. Invisible à plat.
  Absent si la carte n'a pas de masque (le reste de l'effet est inchangé).
- **Masques** : `images/masks/<id>.png`, 116 cartes (les 21 légendaires + 95 des 98 ultra rares ; les 3 autres n'ont pas
  de photo : `musician-azagthoth`, `musician-cronos`, `musician-meine`) ; alpha = silhouette des musiciens. **Une nouvelle
  carte ultra rare / légendaire avec photo doit avoir son masque**, sinon pas de contour ni de relief. Servent au contour
  des reflets (ultra rare / légendaire) et au relief (légendaire).

## Approches essayées puis rejetées
- Étoiles, puis cailloux / écailles, puis paillettes de plus en plus fines et nombreuses : « trop
  confetti », pas assez sobre. Remplacés par le motif de pentacles répété (comme les cartes Pokémon).
- Arc de cercle derrière les motifs : trop de bruit.
- Pointillés sur les bordures de carte, et motifs visibles partout dès qu'on incline : rejetés.
- Reflet façon « négatif » (color-dodge qui crame les photos claires) : opacité du shine réduite
  (×0.38 légendaire, ×0.32 ultra rare).
- **Feuille de métal sous le texte des rares** (balayage argenté + grain) : créait une bande horizontale
  grise avec un bord net en haut quand on incline. Supprimée ; seuls les pentacles restent.
- Éclairs sur les légendaires : retirés à la demande de l'utilisateur.
- Motifs dessinés un par un dans un canvas à chaque image (opacité propre à chaque motif) : rendu « plat » et plus
  lourd ; remplacés par le masque fixe + feuille réfléchissante (principe poke-holo `reverse-holo.css`).

## Pièges techniques
- `.reveal-card` est en `preserve-3d` : `mix-blend-mode` n'y fusionne pas avec le contenu. Les couches sont
  donc posées dans `.rc-frame` (plat, `isolation: isolate`).
- Le fond de `.rc-frame` est retraité par le filtre `metallicss` : toute texture fine (stries du métal
  brossé) doit être un calque **séparé** en anneau (`.rc-holo-brushed`), pas un `background`.
- Utiliser `offsetLeft/Top` (pas `getBoundingClientRect`) pour placer les calques : il ignore le tilt 3D.
- Un `mouse.up` / `pointerup` sans déplacement compte comme un tap et passe à la carte suivante.

## Tests
Serveur local + Playwright (voir `CLAUDE.md`), viewport 420×860 : tenir le doigt appuyé, déplacer vers
gauche / droite / haut / bas, vérifier que la lumière apparaît du côté opposé, qu'elle disparaît à plat et
qu'aucune bande ne traverse la carte. Vérifié le 2026-11-04 sur les 21 légendaires (cadre brossé, relief présent,
pas de pentacles, aucun débordement de texte), sur 9 ultra rares et 6 rares (motif + masque en place, pas de relief). **Non testé** : comportement de `mask-composite` sur Safari, performance sur téléphone réel, zoom depuis l'album
(utilise aussi `buildRevealCard`), cartes sans masque en conditions réelles.

## À faire / ouvert
- `holo-lab.html` (page de test isolée, remplacée par l'intégration) est resté hors dépôt : à supprimer ou ignorer.
- Les cartes en miniature de l'album (`.mini-card`) n'ont pas ces effets (seulement l'aperçu agrandi / la révélation).
- Étendre éventuellement le relief aux ultra rares (elles ont déjà des masques).
- Option évoquée, non demandée : poser le motif des rares *derrière* le texte.


## Mise à jour (2026-11-05) : pentacles à la place des éclairs
Le motif répété n'est plus un éclair mais un **pentacle** : pentagramme inversé (une pointe vers le bas, deux cornes vers le haut) en traits fins **entrelacés**, dans un cercle (`drawPentacle` dans `index.html`). Il est dessiné directement dans le masque canvas : chaque trait est posé avec un halo qui coupe ceux déjà tracés (d'où l'effet dessus / dessous et les petites coupures du cercle aux pointes), et un raccord final ferme la boucle. Même mécanique de feuille réfléchissante et de facette atténuée (moitié haute-droite). Tailles : ultra rare, quinconce 27×31 px, rayon 10,5 px ; rare, quinconce 46×50 px, rayon 19 px. Les noms CSS/JS `bolts` sont conservés pour limiter le diff. Des étoiles pleines ont été essayées d'abord et rejetées : pas assez « pentagramme ».
