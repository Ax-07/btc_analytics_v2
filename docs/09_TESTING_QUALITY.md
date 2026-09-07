# 09 — Tests et qualité

## Outils

- pytest
- Ruff
- Pyright
- GitHub Actions

## Classes de tests

### Unitaires

Normalisation, indicateurs, métriques structurelles, règles d'événements, métriques d'outcomes, sérialiseurs.

### Invariants/tests de propriétés

Validité OHLC, alignement des intervalles, fingerprints déterministes, timestamps monotones, règles de gaps, conventions MFE/MAE.

### Intégration

CCXT -> normalisation/validation -> PostgreSQL ; snapshot -> DuckDB/Polars ; feature -> structure/event/context -> occurrence -> outcome.

### Jeux de données de référence

Petites fixtures versionnées pour la normalisation de marché, la parité avec les fonctions TA-Lib sélectionnées, la structure causale et les outcomes.

### Causalité/invariance par préfixe

Obligatoire pour tout artefact déclaré connu à T : feature, point/segment structurel, événement, contexte et occurrence dérivée.

### Tests de révision des données

Vérifier :

- que la première ingestion valide crée `revision_seq = 1` comme `accepted_current` ;
- que la première révision acceptée enregistre `observed_at` et `accepted_at` avec `observed_at <= accepted_at` ;
- que sa référence exacte de révision est stable pour les manifestes DatasetSnapshot ;
- qu'une nouvelle récupération avec les mêmes valeurs est idempotente et ne crée aucune nouvelle révision ;
- qu'une bougie source modifiée crée une révision persistée `pending_confirmation` avec le prochain `revision_seq` avant confirmation ;
- que la candidate en attente enregistre `observed_at`, n'a pas d'`accepted_at` et n'est jamais éligible au PIT ;
- qu'une réobservation de mêmes valeurs de la candidate en attente est idempotente et n'alloue pas de nouveau `revision_seq` ;
- qu'au plus une candidate en attente non résolue existe par lignée de bougie et que les résultats de confirmation ne peuvent pas être appliqués hors ordre ;
- qu'une interruption/redémarrage préserve l'état pending et n'implique jamais acceptation ou quarantaine ;
- qu'une candidate mise en quarantaine conserve sa séquence allouée et que la candidate suivante ne la réutilise pas ;
- qu'une promotion préserve le `revision_seq` déjà alloué à la candidate ;
- qu'un accord avec la confirmation native promeut la révision et enregistre `accepted_at` ;
- que toute révision acceptée satisfait `observed_at <= accepted_at` ;
- qu'un désaccord/une confirmation indisponible met la révision en `quarantined`, laisse `accepted_at` absent et préserve l'état canonique courant ;
- qu'une candidate observée n'est pas éligible au PIT avant `accepted_at` ;
- que le replay PIT sélectionne la révision acceptée ayant le plus grand `accepted_at <= T` ;
- qu'une révision mise en quarantaine n'est jamais éligible au PIT ;
- qu'une correction acceptée ne modifie jamais un DatasetSnapshot existant ;
- que `reconstructed_latest` et `observed_point_in_time` ne portent pas la même affirmation de connaissance historique ;
- fixture temporelle de référence : une candidate observée à 10:00 et acceptée à 10:05 ne doit pas affecter le replay à 10:02 et peut l'affecter à 10:05 ou après.

### Tests de référence (`golden tests`) d'identité déterministe

Les fixtures de référence doivent figer :

- la normalisation canonique des paramètres ;
- les octets RFC 8785 JCS ;
- le `parameter_fingerprint` SHA-256 ;
- le payload exact d'`occurrence_key` et la clé résultante ;
- l'identité logique de DatasetSnapshot.

Au moins une représentation de fixture indépendante doit vérifier que des objets de paramètres sémantiquement identiques mais dont l'ordre des clés d'entrée diffère produisent les mêmes fingerprints.

## Définition de terminé

Un jalon est terminé uniquement lorsque les docs/contrats, tests, edge cases, contrôles de causalité, migrations/API/UI lorsque pertinentes, `CURRENT_STATE.md` et l'état du jalon Git ont été validés.

Aucun jalon n'est déclaré validé avant l'examen des sorties réelles des commandes locales/CI.
