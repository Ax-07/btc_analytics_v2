# Current State

## Projet

BTC Analytics V2

## Phase

P0 — Foundation / documentation

## Statut

`P0 — VALIDATION CANDIDATE v6`

La v6 ferme les deux blocages identifiés lors des audits indépendants de la v5 :

1. `docs/15_TEMPORAL_CONVENTIONS.md` utilisait encore `observed_at <= T` pour le replay `observed_point_in_time` au lieu de la règle canonique `accepted_at <= T` ;
2. le cycle de vie de la première `CandleRevision` acceptée lors de l’ingestion initiale d’une nouvelle candle n’était pas explicitement défini.

Le contrat définit désormais la première révision avec `revision_seq = 1`, puis alloue chaque `revision_seq` suivant à la création d’une nouvelle observation distincte, y compris si elle est ensuite quarantinée.

P1 reste interdit tant que l’audit final v6 n’a pas conclu `P0 — VALIDATION READY` et que les décisions D-001 à D-020 ne sont pas explicitement approuvées.

## Source canonique ChatGPT recommandée

Utiliser en priorité le fichier unique :

`BTC_ANALYTICS_V2_P0_CANONICAL_v6.md`

Ne pas conserver simultanément un ancien master P0 dans les sources actives du projet ChatGPT.

## Prochaine étape

Audit final ciblé des deux corrections v6, puis contrôle transversal court de la source canonique.
