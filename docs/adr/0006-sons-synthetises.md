# ADR-0006 : Sons synthétisés (Web Audio) — cinq moments

## Statut
**Validé et déployé** (2026-11-05), après essais sur iPhone.

## Contexte
L'ouverture de paquet (carrousel, déchirure, révélation, récap) était muette. Objectif : un retour sonore « satisfaisant »
sans alourdir le projet (100 % statique, ADR-0001), sans fichier audio à héberger ni licence à gérer.

## Décision
- **Tous les sons sont synthétisés au runtime avec Web Audio** (`<script>` « SONS », `window.MCMSfx`) : oscillateurs, bruit
  filtré, enveloppes exponentielles, un compresseur en sortie. Aucun asset, aucun appel réseau, ~250 lignes.
- **Cinq moments sonorisés, pas un de plus** (hooks `sfx(...)` dans `index.html`) :
  1. `tick` : un paquet passe devant dans le carrousel (claquement sec + choc sourd) ;
  2. `tear` : déchirure à l'ouverture du paquet (bruit qui balaie du grave à l'aigu, enveloppe en dents de scie, craquements,
     choc, puis le haut qui s'envole) ;
  3. `reveal` (communes, rares, ultra rares) : une carte apparaît (souffle du flip + choc à l'atterrissage), **sans accent
     de rareté** ;
  4. `swipe` : swipe d'une carte (suivante ou précédente), petit souffle rapide qui part du geste ;
  5. `reveal("legendaire")` : version « métal » (v2, après retour : trop peu rock/dark). Sur les 1,5 s de fumée : grosse caisse en double pédale qui
     s'emballe, grondement grave, drone en mi (41 Hz) saturé, cymbale inversée et larsen de guitare. Puis l'impact : grosse
     caisse + caisse claire + crash, sub, accord de puissance en mi saturé (scie + carré désaccordés, ampli et baffle simulés)
     et trois « chugs » étouffés. Toutes les couches passent par un bus dédié (×0,55) pour rester cohérent avec les autres sons.
  **Retirés** (essayés puis supprimés à la demande de l'utilisateur) : les « ding » (pastille NEW, cloche des rares,
  accord des ultra rares), les claquements du récap, les sons de tremblement / cartes qui sortent / flash / boutons.
- **Interrupteur** : bouton haut-parleur dans la vue Paquets et sur l'écran d'ouverture, état mémorisé dans
  `localStorage` (`mcm-sound`). Son activé par défaut.
- **iOS / Safari** : le contexte audio n'est créé et relancé qu'après un geste (`pointerdown` / `touchend`), suspendu quand
  l'onglet est caché. L'interrupteur « sonnerie » de l'iPhone coupe l'audio web : pas de son même sans bouton coupé.

## Ce qui n'a PAS changé
Tirage, stock serveur, animations, inventaire. Les sons ne bloquent jamais : si `AudioContext` est absent ou échoue, tout
continue en silence.

## Mixage
Mesuré en rendu hors ligne (`OfflineAudioContext`, un son à la fois) : tick ~0,11 ; swipe ~0,15 ; déchirure ~0,4 ; carte qui
apparaît ~0,35 ; légendaire ~0,85 (pas d'écrêtage).

## Tests
Playwright (Chromium, `AudioContext` réel) : le carrousel, la déchirure, l'apparition de chaque carte, le swipe et la
légendaire déclenchent leurs sons ; tremblement, récap et pastilles NEW restent silencieux ; aucun son quand le bouton
est coupé ; l'état est mémorisé. **Non testé** : l'oreille (rien n'a été écouté), iPhone réel, latence au premier geste,
volume absolu selon le haut-parleur.

## À faire / ouvert
- Régler le mixage à l'écoute sur iPhone (volume, durée de la déchirure et du légendaire).
- Éventuellement remplacer certains sons par de vrais échantillons (déchirure de papier alu, flip de carte, impact) s'ils sont libres de
  droits.
- Option « vibration » séparée du son.
