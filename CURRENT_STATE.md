# Current State

## Projet

BTC Analytics V2

## Phase

P0 — Foundation / documentation

## Statut

`P0 — VALIDATION CANDIDATE v7`

La v7 ferme le dernier blocage identifié lors de l’audit indépendant de la v6 : une `CandleRevision` candidate existait entre sa création et sa confirmation native, mais `revision_status` ne possédait aucun état représentant cette phase intermédiaire.

Le contrat définit désormais `pending_confirmation` :

- la candidate reçoit son `revision_seq` et son `observed_at` dès sa création ;
- elle reste sans `accepted_at` et n’est jamais PIT-éligible tant que la confirmation n’a pas réussi ;
- confirmation réussie -> `accepted_current` et l’ancienne current devient `accepted_superseded` ;
- désaccord, indisponibilité ou échec de validation -> `quarantined` ;
- une seule candidate `pending_confirmation` est autorisée à la fois par lignée de candle afin de sérialiser les transitions et empêcher les acceptations hors ordre ;
- après interruption, une candidate pending reste durablement pending jusqu’à reprise/résolution et n’est jamais assimilée à une révision acceptée.

P1 reste interdit tant que l’audit final v7 n’a pas conclu `P0 — VALIDATION READY` et que les décisions D-001 à D-020 ne sont pas explicitement approuvées.

## Source canonique ChatGPT recommandée

Utiliser en priorité le fichier unique :

`BTC_ANALYTICS_V2_P0_CANONICAL_v7.md`

Ne pas conserver simultanément un ancien master P0 dans les sources actives du projet ChatGPT.

## Prochaine étape

Audit final ciblé de la machine d’état `CandleRevision`, puis contrôle transversal court de la source canonique.
