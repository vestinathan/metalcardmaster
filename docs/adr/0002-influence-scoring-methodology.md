# ADR-0002 : Méthodologie de scoring de l'influence des cartes

## Statut
En cours de révision (v5 en cours de calibration, non déployée — voir "État actuel")

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

## État actuel (non déployé)
Deux décisions validées par l'utilisateur pour la suite de la v5, pas encore implémentées ni
re-pilotées :
1. **Revoir à la hausse les scores des groupes eux-mêmes** (Metallica, Slipknot, Pantera
   semblent sous-cotés) plutôt que de pousser encore le ratio proxy.
2. **Ajouter un plancher de visibilité individuelle minimale** : un fondateur doit aussi avoir
   une reconnaissance publique propre minimale pour hériter du statut légendaire du groupe,
   sinon il reste sur son propre score individuel.

**Prochaine étape** : recalibrer les scores des groupes de référence (ancres), puis relancer
un pilote v5 avec le plancher de visibilité ajouté, avant tout recalcul des 275 cartes.
**Aucun changement n'a encore été appliqué à `index.html`** — seuls des pilotes en mémoire de
session ont été testés.

## Conséquences / points de vigilance pour la suite
- Toujours valider une nouvelle méthodologie sur un petit pilote (6-10 cas de contrôle
  couvrant les cas limites : frontman actif, instrumentiste fondateur non-frontman, pionnier
  culte décédé/dissous, membre ayant rejoint après la fondation) avant de l'appliquer aux 275
  cartes.
- Toujours montrer le diff complet à l'utilisateur avant de push un recalcul de masse sur
  `CARDS`.
- Ne pas réintroduire Spotify comme signal : limitation structurelle de l'API, pas un
  problème de clé ou de quota.
