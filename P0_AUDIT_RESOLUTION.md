# Résolution de l'audit P0 — Consolidée v7

## Statut

`P0 — VALIDATED`

Cette révision ferme le dernier blocage signalé par l'audit indépendant de la v6. Deux audits finaux indépendants de la v7 ont ensuite conclu `P0 — VALIDATION READY`. Le 6 septembre 2026, l'utilisateur a explicitement approuvé D-001 à D-020 en bloc. P0 est donc validé et P1 est autorisé à démarrer à partir de ces contrats figés.

## Blocages v6 précédemment résolus

La candidate v6 avait déjà fermé :

- la règle point-in-time obsolète `observed_at <= T` dans les conventions temporelles, remplacée par la règle canonique `accepted_at <= T` ;
- le cycle de vie de la première `CandleRevision` acceptée, notamment `revision_seq = 1`, les références locales stables de révision et l'allocation monotone de séquence à la création d'une candidate.

Ces contrats restent inchangés.

## Blocage R6 — état non résolu d'une candidate de révision

Le modèle v6 créait une candidate de révision distincte et allouait son `revision_seq` avant la confirmation native de la même venue, mais les valeurs autorisées de `revision_status` étaient uniquement `accepted_current`, `accepted_superseded` et `quarantined`. Aucun statut ne représentait l'intervalle réel entre la création de la candidate et la résolution de la confirmation.

Contrat de candidate résolu en v7 :

- `revision_status` inclut en plus `pending_confirmation` ;
- une observation ultérieure distincte d'une bougie déjà acceptée crée une révision durable `pending_confirmation` avec le prochain `revision_seq`, `observed_at` et sans `accepted_at` ;
- `pending_confirmation` n'est jamais éligible à `observed_point_in_time` ;
- une confirmation native réussie fait passer cette même révision à `accepted_current`, enregistre `accepted_at` et fait passer l'ancienne révision courante acceptée à `accepted_superseded` ;
- un désaccord, une confirmation indisponible ou un échec de validation fait passer cette même révision à `quarantined`, en conservant sa séquence et sans renseigner `accepted_at` ;
- une promotion ou une mise en quarantaine ne renumérote jamais la révision ;
- au plus une révision `pending_confirmation` non résolue peut exister à la fois pour une lignée de bougie ; le traitement d'une autre candidate distincte pour cette bougie est sérialisé jusqu'à résolution de la révision en attente ;
- une observation de mêmes valeurs correspondant à la candidate en attente est idempotente et n'alloue pas une nouvelle séquence ;
- après interruption/redémarrage, une révision en attente non résolue reste pending et non éligible au PIT jusqu'à ce que la confirmation soit retentée/résolue ; elle n'est jamais silencieusement considérée comme acceptée ou quarantined.

## Mise à jour de décision

D-020 inclut désormais explicitement l'état `pending_confirmation`, sa non-éligibilité au PIT et la règle de sérialisation des transitions par candle.

## Tests ajoutés au contrat

Les tests de révision de données doivent en plus vérifier :

- qu'une observation modifiée est persistée comme `pending_confirmation` avant le retour de la confirmation ;
- qu'une révision en attente possède `observed_at`, n'a pas d'`accepted_at` et n'est jamais éligible au PIT ;
- qu'une confirmation réussie fait passer la même révision/séquence à `accepted_current` ;
- qu'une confirmation échouée ou indisponible fait passer la même révision/séquence à `quarantined` ;
- qu'une réobservation de mêmes valeurs d'une candidate en attente est idempotente ;
- qu'une bougie ne peut pas avoir deux candidates en attente non résolues et que les résultats de confirmation ne peuvent pas être appliqués hors ordre ;
- qu'un redémarrage/recovery conserve l'état pending sans impliquer une acceptation.

## Critère de validation — satisfait

- Audit final indépendant A : `P0 — VALIDATION READY`.
- Audit final indépendant B : `P0 — VALIDATION READY`.
- Approbation utilisateur : D-001 à D-020 explicitement approuvées en bloc le 6 septembre 2026.

Résultat : `P0 — VALIDATED`. P1 peut démarrer, mais les décisions P0 validées sont des contrats historiques à ajouts uniquement (append-only) et ne doivent jamais être réécrites silencieusement.
