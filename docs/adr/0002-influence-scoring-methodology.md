# ADR-0002 : Méthodologie de scoring de l'influence des cartes

## Statut
v5 appliquée (partiellement) le 2026-11-02 — voir "État actuel" pour le périmètre couvert et
ce qui reste à faire.

## Contexte
Chaque carte (groupe ou musicien) a un score `influence` (0-100) qui déterminine sa `rarity`
via des seuils fixes (`commune <42`, `rare 42-63`, `ultra_rare 64-85`, `legendaire 86+`).
À l'origine, ces 275 scores étaient entièrement saisis à la main, sans méthode reproductible
— ce qui a produit des incohérences visibles (ex: Corey Taylor, l'un des chanteurs metal les
plus reconnus depuis ~30 ans, noté "commune").

## Principe fondamental (non négociable)
**Le score `influence` d'une carte et la distribution de rareté dans les packs
(`RARITY_DROP_WEIGHTS`, `GUARANTEED_SLOT_RARITIES` dans `index.html`) sont deux mécanismes
strictement séparés.** Un score d'influence ne doit jamais être baissé ou monté pour obtenir
une pyramide de rareté "équilibrée" dans les packs — l'équilibrage des packs se fait
uniquement via les poids de tirage, jamais via le score intrinsèque d'une carte.

## Historique des itérations

- **v0 (origine)** — scores 100% manuels, aucune méthode. Rejeté : incohérent et non
  reproductible.
- **v1** — 25% Spotify / 45% Wikipedia / 30% ventes-certifications, pondéré vers le statut de
  "pionnier historique" (pour ne pas pénaliser les fondateurs de genre à faible succès
  commercial, ex: Bathory). **Rejeté par l'utilisateur** : sous-notait l'influence
  soutenue/actuelle au profit du seul statut de pionnier (Corey Taylor restait trop bas).
- **v2** — 45% Spotify (dominant) / 30% Wikipedia / 25% ventes, avec exception : pour un
  musicien décédé/retiré avant l'ère du streaming, utiliser le Spotify de son groupe
  d'origine comme proxy. A corrigé la sur-notation des pionniers cultes, mais n'a pas résolu
  le cas des frontmen vivants et actifs (proxy limité aux décédés/retraités).
- **v3** — ajout d'une règle de proxy pour tout frontman/chanteur principal vivant et actif,
  identifié à son groupe : score = 70% signal du groupe + 30% signal individuel propre.
  Validé en principe sur un pilote à 6 cas.
- **Blocage technique** — l'API Spotify a retiré les champs `popularity`/`followers`/`genres`
  pour les apps en mode gratuit (migration de mars 2026), rendant Spotify inutilisable comme
  signal, même avec des credentials valides. Spotify abandonné.
- **v4** — 60% Wikipedia/notoriété encyclopédique **actuelle** (pas seulement historique :
  activité récente, tournées, sorties, couverture presse) / 40% ventes-certifications-
  reconnaissance. Règle de proxy frontman conservée (70/30), exception 100%-proxy pour les
  musiciens décédés/retirés avant le streaming conservée. **Pilote validé** sur le cas Corey
  Taylor (36→78) et la distinction frontman/instrumentiste (Hetfield 89 vs Butler 52/Ulrich
  58), mais **rejeté par l'utilisateur à l'étape suivante** : il estime que Lars Ulrich,
  Corey Taylor et Phil Anselmo doivent tous être `legendaire` (86+), pas `ultra_rare`/`rare`.
- **v5 (en cours)** — deux changements validés par l'utilisateur :
  1. Le proxy n'est plus réservé au frontman/chanteur : tout membre **fondateur** toujours
     associé à son groupe en hérite, peu importe l'instrument.
  2. Ratio proxy porté à 85/15 (au lieu de 70/30).

  **Problème découvert au pilote v5** : la formule linéaire ne suffit pas. Même Lars Ulrich
  (le cas le mieux documenté) plafonne à 84.3, sous le seuil légendaire — parce que le score
  du groupe lui-même (Metallica=89) n'est pas assez haut pour que 85% de ce score dépasse 86.
  Pire, un fondateur peu médiatisé (Geezer Butler, score individuel 52) se retrouve presque
  au même niveau qu'Ulrich (85.1 vs 84.3) simplement parce que le score du groupe Black
  Sabbath (91) est plus élevé — le ratio 85/15 écrase quasiment toute variance individuelle
  entre fondateurs d'un même calibre de groupe.

## État actuel — v5 appliquée le 2026-11-02 (périmètre partiel)

**Diagnostic confirmé** : les scores des groupes-ancres (Metallica 94, Pantera 92, Slipknot 88,
Black Sabbath 91, Iron Maiden 88...) étaient déjà corrects. Le vrai problème était un bloc de
~20 musiciens individuels ("renfort commune/rare du pool musiciens", ajouté pour rééquilibrer la
distribution du paquet "musicians") dont le score avait été **délibérément écrasé bas pour des
raisons de distribution de pack** — une violation directe du principe fondamental ci-dessus.
Cas le plus flagrant : Corey Taylor (chanteur de Slipknot, groupe à 88) noté 36 ; Lars Ulrich
(cofondateur de Metallica, groupe à 94) noté 52.

**Formule retenue pour un musicien individuel rattaché à un groupe** :
`score = max(score_hérité_statut, score_reconnaissance_propre)`
- Fondateur toujours actif/visible publiquement (médias, carrière solo, longévité au poste) →
  poids hérité élevé, proche du score du groupe.
- Fondateur discret, sans rayonnement personnel documenté → poids hérité modéré, le score reste
  nettement sous celui du groupe (ex: Geezer Butler 58 / Black Sabbath 91 ; Bill Ward 48, parti
  tôt et quasi absent publiquement depuis).
- Membre ayant rejoint après la fondation (pas de bonus fondateur) → score basé sur sa
  reconnaissance propre uniquement (ex: Kirk Hammett 68, a remplacé Mustaine en 1983).
- Un plancher de reconnaissance individuelle minimale s'applique : un fondateur sans visibilité
  propre documentée ne monte pas automatiquement au niveau du groupe.

**Corrections appliquées le 2026-11-02** (18 cartes, voir commit) : Lars Ulrich (52→89),
Kirk Hammett (49→68), Geezer Butler (47→58), Bill Ward (33→48), Steve Harris (55→78),
Dave Lombardo (46→68), Kerry King (48→70), Lemmy Kilmister (58→88), Glen Benton (29→40),
Randy Blythe (34→48), M. Shadows (32→50), Fenriz (27→35), Corey Taylor (36→84),
Robb Flynn (29→67), David Coverdale (36→70), Ritchie Blackmore (34→65),
Layne Staley (48→62), Chris Cornell (48→75), Robert Plant (58→85), Eddie Van Halen (62→80).

**Périmètre couvert** : le bloc "renfort" originel (20 cartes) intégralement revu, plus un
balayage ciblé des ~320 autres musiciens individuels du fichier à la recherche d'anomalies
flagrantes (sous-cotation nette d'une figure très reconnue). La grande majorité des ~320
autres entrées (musiciens de groupes de niche black/death/power metal, scores 9-45) s'est
avérée déjà cohérente avec leur statut réel — pas de pattern de compression artificielle
comme sur le bloc "renfort". Seules les anomalies ponctuelles clairement identifiables ont été
corrigées ; ce balayage n'est pas une relecture exhaustive bio-par-bio des ~320 cartes.

**Reste à faire si besoin** : signaler au fil de l'eau toute autre carte qui semble mal notée
(comme pour ce lot) plutôt que de tenter une repasse systématique à froid — le risque d'erreur
de jugement sur des figures moins connues augmente sans signal extérieur fiable (voir
"Blocage technique Spotify" ci-dessus, toujours valable).

## Conséquences / points de vigilance pour la suite
- Toujours valider une nouvelle méthodologie sur un petit pilote (6-10 cas de contrôle
  couvrant les cas limites : frontman actif, instrumentiste fondateur non-frontman, pionnier
  culte décédé/dissous, membre ayant rejoint après la fondation) avant de l'appliquer aux 275
  cartes.
- Toujours montrer le diff complet à l'utilisateur avant de push un recalcul de masse sur
  `CARDS`.
- Ne pas réintroduire Spotify comme signal : limitation structurelle de l'API, pas un
  problème de clé ou de quota.
