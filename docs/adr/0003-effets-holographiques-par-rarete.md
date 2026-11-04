# ADR-0003 : Effets holographiques des cartes, par rareté

## Statut
**En cours — non validé, non commité** (2026-11-04). Itérations testées par l'utilisateur sur iPhone via
un aperçu privé ; rien n'est poussé sur `main` tant qu'il n'a pas validé explicitement.

## Contexte
Les cartes révélées à l'ouverture d'un paquet (`.reveal-card`) doivent réagir à l'inclinaison au doigt
comme une vraie carte holographique (référence : poke-holo, `simeydotme/pokemon-cards-css`, MIT). Le
principe retenu est **physique** : les motifs sont **fixes dans la carte** et ne s'allument que lorsque
l'inclinaison les aligne avec la lumière — jamais partout à la fois, jamais sans mouvement.

## Décision : un effet par rareté
| Rareté | Effet |
|---|---|
| `commune` | aucun |
| `rare` | **uniquement** un motif d'éclairs très discret sous le texte (zone `.rc-move-top` → bas de la fenêtre) ; fenêtre photo laissée libre |
| `ultra_rare` | reflets pleine carte (acier, glare, liseré chrome sur la bordure, contour autour des musiciens) + motif fin d'éclairs en quinconce sur toute la carte |
| `legendaire` | mêmes reflets pleine carte, **sans motif d'éclairs**, + **cadre métal brossé / chrome** + **relief sur les musiciens détourés** (parallaxe + ombre) |

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
- Les motifs sont dessinés dans un canvas (`.rc-holo-glitter`), regroupés par couleur/alpha dans des
  `Path2D` (sinon ~67 ms/frame).

## Paramètres retenus
- **Éclairs ultra rare** : quinconce 15×19 px, éclair ~9.5×14 px, palette rouge / gris / noir brillants
  (en RGB, pas en HSL : l'interpolation de teinte passait par le violet), tache σ≈0.3, aucun pointillé sur
  les bordures.
- **Éclairs rare** : tuiles plus grandes (30×36 px, éclair 17×25), tache **étroite** σ≈0.17, `gR = 0` à plat,
  coupure `I < 0.1`, alpha ×0.42, mélange canvas `lighten` (garde le texte net). Palette métal
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
  confetti », pas assez sobre. Remplacés par le motif d'éclairs répété (comme les cartes Pokémon).
- Arc de cercle derrière les motifs : trop de bruit.
- Pointillés sur les bordures de carte, et motifs visibles partout dès qu'on incline : rejetés.
- Reflet façon « négatif » (color-dodge qui crame les photos claires) : opacité du shine réduite
  (×0.38 légendaire, ×0.32 ultra rare).
- **Feuille de métal sous le texte des rares** (balayage argenté + grain) : créait une bande horizontale
  grise avec un bord net en haut quand on incline. Supprimée ; seuls les éclairs restent.
- Éclairs sur les légendaires : retirés à la demande de l'utilisateur.

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
pas d'éclairs, aucun débordement de texte) et sur 4 ultra rares (éclairs, pas de relief). **Non testé** : performance sur téléphone réel, zoom depuis l'album
(utilise aussi `buildRevealCard`), cartes sans masque en conditions réelles.

## À faire / ouvert
- Validation par l'utilisateur, puis commit atomique (`index.html`, `images/masks/`, docs) ; décider du sort de
  `holo-lab.html` (page de test isolée, remplacée par l'intégration).
- Les cartes en miniature de l'album (`.mini-card`) n'ont pas ces effets (seulement l'aperçu agrandi / la révélation).
- Étendre éventuellement le relief aux ultra rares (elles ont déjà des masques).
- Option évoquée, non demandée : poser le motif des rares *derrière* le texte.
