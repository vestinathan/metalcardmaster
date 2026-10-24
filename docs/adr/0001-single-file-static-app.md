# ADR-0001 : App statique en un seul fichier HTML

## Statut
Accepté (choix initial du projet)

## Contexte
L'app devait être simple à déployer (Vercel, zéro configuration) et sans dépendance à un
backend, une base de données ou des clés API.

## Décision
Tout le code (HTML, CSS, JS) vit dans un unique `index.html`. Les données des 275 cartes
(tableau `CARDS`) sont codées en dur dans ce même fichier. Les images sont pré-téléchargées
et stockées dans `images/bands/`, sans appel réseau au runtime.

## Conséquences
- ✅ Déploiement trivial : push → Vercel sert le fichier statique, aucune build step.
- ✅ Aucune dépendance externe à l'exécution (pas de risque de service tiers down).
- ❌ Fichier volumineux (~460 Ko) et diffs bruyants dès qu'on touche aux données `CARDS`,
  qui représentent la majorité du poids du fichier.
- ❌ Pas de séparation données/logique : un changement de méthodologie de scoring (voir
  ADR-0002) doit patcher un tableau JS en ligne plutôt qu'un fichier de données dédié.

Si le volume de données ou la fréquence des changements de scoring continue de croître, une
extraction de `CARDS` vers un fichier JSON séparé (chargé en `fetch` au runtime, ou inliné au
build) serait à reconsidérer — mais casserait la contrainte "zéro build step".
