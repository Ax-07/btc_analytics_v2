# Current State

## Projet

BTC Analytics V2

## Phase

P0 — Foundation / documentation

## Statut

`P0 — VALIDATION CANDIDATE v5`

La v5 ferme le dernier blocage identifié lors de l’audit v4 : le moment d’acceptation d’une `CandleRevision` pour le replay `observed_point_in_time`.

Le contrat distingue désormais :

- `observed_at` : première observation de la révision par BTC Analytics ;
- `accepted_at` : instant où la révision est confirmée et devient admissible comme état canonique accepté.

En `observed_point_in_time`, une révision n’est utilisable à T que si `accepted_at <= T`.

P1 reste interdit tant que l’audit final v5 n’a pas conclu `P0 — VALIDATION READY` et que les décisions D-001 à D-020 ne sont pas explicitement approuvées.

## Source canonique ChatGPT recommandée

Utiliser en priorité le fichier unique :

`BTC_ANALYTICS_V2_P0_CANONICAL_v5.md`

Ne pas conserver simultanément l’ancien master v4 dans les sources actives du projet ChatGPT.

## Prochaine étape

Audit final ciblé du contrat `accepted_at` puis contrôle transversal court de la source canonique v5.
