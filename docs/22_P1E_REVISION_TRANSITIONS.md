# P1E — Transitions et politique des révisions

Statut : `VALIDATION READY — VALIDATION UTILISATEUR EN ATTENTE`

P1E implémente la machine transactionnelle de révisions déjà fixée par D-020. Il ne redéfinit pas la sémantique de `CandleRevision` et ne réalise pas la confirmation réseau Binance elle-même.

## Sources canoniques

Ordre appliqué :

1. `docs/10_DECISIONS.md`, notamment D-003, D-005, D-011, D-016 et D-020 ;
2. `docs/03_DOMAIN_MODEL.md` ;
3. `docs/05_MARKET_DATA.md` ;
4. `docs/15_TEMPORAL_CONVENTIONS.md` ;
5. `docs/09_TESTING_QUALITY.md` ;
6. `docs/19_P1B_MARKET_DATA_DOMAIN.md` ;
7. `docs/21_P1D_POSTGRESQL_SCHEMA.md`.

## Validation du design

Le 7 septembre 2026, l’utilisateur a explicitement validé les choix C-1 à C-5 avant génération du code de production P1E. L’implémentation peut donc matérialiser ces choix sans modifier D-020.

Le candidat P1E introduit :

- `market_data/revisions.py` pour les DTO, résultats, erreurs de politique et le `RevisionStore` ;
- `storage/revisions.py` pour l’implémentation PostgreSQL avec verrous de ligne ;
- une horloge UTC injectable pour capturer `accepted_at`/`candles.ingested_at` uniquement lors d’une acceptation réelle ;
- des tests unitaires du contrat et des tests PostgreSQL des transitions, de la reprise et de la concurrence.

Aucune migration Alembic ni nouvelle dépendance n’est nécessaire pour ce candidat.

## Contrats D-020 à implémenter sans redéfinition

P1E doit garantir :

- première observation valide d'une bougie inconnue : création atomique de la `Candle`, de `revision_seq = 1` et de la révision `accepted_current` ;
- `observed_at` provient de l'observation normalisée ; `accepted_at` est fixé uniquement lorsqu'une révision devient acceptée ;
- une réobservation logiquement identique à la révision courante est idempotente ;
- toute observation distincte ultérieure alloue le prochain `revision_seq` au moment de la création et persiste immédiatement la candidate comme `pending_confirmation` ;
- une seule candidate `pending_confirmation` non résolue peut exister par lignée ;
- une réobservation identique à la candidate en attente est idempotente ;
- une observation distincte supplémentaire est bloquée tant que la candidate en attente n'est pas résolue ;
- un redémarrage conserve exactement l'état `pending_confirmation` ;
- une promotion transforme la même candidate en `accepted_current`, fixe `accepted_at`, supersède l'ancienne courante et met à jour `candles.current_revision_seq` dans une seule transaction ;
- une quarantaine transforme la même candidate en `quarantined`, conserve son `revision_seq`, laisse `accepted_at` absent et ne modifie pas l'état courant ;
- un `revision_seq` alloué n'est jamais réutilisé, y compris après quarantaine ;
- un résultat de confirmation ne peut pas être appliqué hors ordre ;
- les révisions acceptées satisfont toujours `observed_at <= accepted_at`.

## Frontière P1E

### Entrée normalisée

P1E reçoit une observation déjà normalisée et validée au niveau des invariants canoniques élémentaires. Le DTO d'application P1E doit contenir au minimum :

- `Market` ;
- `Timeframe` ;
- `open_time` / `end_time` / `available_at` ;
- OHLC, `base_volume`, `quote_volume`, `trade_count` ;
- `source` / `source_symbol` ;
- `observed_at` ;
- `after_values_fingerprint`.

P1E ne calcule pas encore le fingerprint : P1B l'a explicitement laissé opaque tant qu'un contrat de calcul n'est pas fixé. Le caller fournit donc le fingerprint déjà calculé. P1E vérifie seulement sa présence et sa cohérence minimale : deux observations aux valeurs logiques identiques ne doivent pas présenter deux fingerprints différents.

### Égalité logique

L'idempotence compare les valeurs canoniques normalisées suivantes :

```text
(open, high, low, close, base_volume, quote_volume, trade_count)
```

La provenance `source` / `source_symbol` n'est pas une valeur de marché et ne crée pas, à elle seule, une nouvelle révision. Une divergence de provenance pour des valeurs identiques peut être auditée, mais ne change pas la lignée sémantique.

Pour une candidate ultérieure, `before_values_fingerprint` est copié depuis `after_values_fingerprint` de la révision courante acceptée.

## Choix d'implémentation à valider

### C-1 — Sérialisation par verrou de ligne PostgreSQL

**Option retenue :** isolation PostgreSQL `READ COMMITTED` avec `SELECT ... FOR UPDATE` sur la ligne `candles` de la lignée.

Pour une bougie encore absente, P1E :

1. résout/crée `markets.market_id` ;
2. constate l'absence de la `Candle` ;
3. verrouille la ligne `markets` correspondante ;
4. re-vérifie l'absence de la `Candle` sous verrou ;
5. crée atomiquement la `Candle` et `revision_seq = 1`.

Compromis :

- plus simple et testable que `SERIALIZABLE` avec politique de retry globale ;
- évite d'introduire des advisory locks et leur schéma de clé/collision ;
- sérialise temporairement les créations concurrentes de nouvelles bougies d'un même marché, compromis acceptable en P1 ; ne pas optimiser avant profiling ;
- une lignée déjà existante ne verrouille que sa propre ligne `candles`.

### C-2 — Confirmation réseau hors transaction

**Option retenue :** aucune requête Binance/native n'est exécutée sous verrou PostgreSQL.

Le flux est nécessairement en deux transactions :

```text
observation distincte
    -> transaction A : créer/committer pending_confirmation
    -> appel de confirmation native hors transaction P1E
    -> transaction B : promouvoir OU quarantiner la révision exacte
```

Cette forme respecte D-020 : la candidate existe avant confirmation et survit aux interruptions. Elle évite également de conserver un verrou de base pendant une latence réseau.

P1G fournira le mécanisme de confirmation native. P1E reçoit seulement un résultat terminal explicite appliqué à une référence exacte de révision.

### C-3 — Frontières de modules

**Option retenue :**

- `market_data/revisions.py` : DTO de commande/résultats, statuts d'opération et contrat applicatif sans type SQLAlchemy public ;
- `storage/revisions.py` : implémentation PostgreSQL/SQLAlchemy des transactions et verrous.

Le domaine P1B reste indépendant de SQLAlchemy. Les tables P1D restent détenues par `storage/schema.py`.

Cette séparation évite de faire recalculer la politique par le frontend ou par un caller et conserve PostgreSQL derrière une abstraction appartenant au projet.

### C-4 — Résultats explicites pour les états attendus

Les situations normales ne sont pas des exceptions :

- `initial_accepted` ;
- `current_unchanged` ;
- `pending_created` ;
- `pending_unchanged` ;
- `blocked_by_pending` ;
- `promoted` / `already_promoted` ;
- `quarantined` / `already_quarantined`.

Les exceptions sont réservées aux états impossibles/incohérents : pointeur courant invalide, tentative de promouvoir une révision quarantined, confirmation hors ordre, timestamp d'acceptation antérieur à `observed_at`, fingerprint incohérent pour des valeurs identiques.

### C-5 — Sémantique de `candles.ingested_at`

**Option retenue :** `candles.ingested_at` représente l'instant technique auquel la révision actuellement acceptée a été matérialisée comme état courant PostgreSQL.

- première ingestion : `ingested_at = accepted_at` de `revision_seq = 1` ;
- promotion : `ingested_at` est mis à jour au même instant que le nouvel `accepted_at` ;
- création/quarantaine d'une candidate : `ingested_at` ne change pas.

Ce champ reste une provenance technique et ne participe jamais à l'ancrage causal historique, conformément à D-011.

## Algorithme transactionnel

### Observation d'une bougie

Sous verrou de lignée :

1. charger la `Candle` courante et la révision exacte pointée par `current_revision_seq` ;
2. vérifier que cette révision est `accepted_current` ;
3. charger l'éventuelle candidate `pending_confirmation` ;
4. si une candidate existe et que les valeurs observées lui sont identiques : retourner `pending_unchanged` ;
5. si une candidate existe et que les valeurs observées sont distinctes : retourner `blocked_by_pending` sans allocation ;
6. sinon, si les valeurs sont identiques à la courante : retourner `current_unchanged` ;
7. sinon calculer `next_revision_seq = max(revision_seq) + 1` sous le même verrou ;
8. insérer la candidate `pending_confirmation` avec `accepted_at = NULL` ;
9. committer puis retourner `pending_created`.

Pour une lignée inexistante, le chemin de création atomique insère directement `revision_seq = 1` en `accepted_current` et fixe le pointeur courant à `1`.

### Promotion

Sous verrou de la `Candle` :

1. charger la référence exacte candidate ;
2. si elle est déjà `accepted_current` et que `current_revision_seq` la pointe : retourner `already_promoted` ;
3. sinon exiger `pending_confirmation` ;
4. exiger que cette candidate soit l'unique pending de la lignée ;
5. charger la révision courante exacte et exiger `accepted_current` ;
6. exiger `accepted_at >= observed_at` ;
7. passer l'ancienne courante à `accepted_superseded` ;
8. passer la candidate à `accepted_current`, fixer `accepted_at` et la provenance de confirmation ;
9. mettre à jour `candles.current_revision_seq` et `candles.ingested_at` ;
10. committer atomiquement.

L'ancienne courante est supersédée avant de promouvoir la candidate afin de respecter l'index unique partiel `uq_candle_revisions_one_current` pendant la transaction.

### Quarantaine

Sous verrou de la `Candle` :

1. charger la référence exacte candidate ;
2. si elle est déjà `quarantined` : retourner `already_quarantined` ;
3. sinon exiger `pending_confirmation` ;
4. la passer à `quarantined` ;
5. conserver `accepted_at = NULL` ;
6. enregistrer la provenance/motif de confirmation ;
7. ne modifier ni `current_revision_seq` ni `candles.ingested_at` ;
8. committer.

## Reprise après interruption

P1E n'infère jamais un résultat terminal au démarrage.

Une opération de reprise doit pouvoir retrouver la candidate `pending_confirmation` exacte d'une lignée. Le caller peut alors redemander la confirmation native P1G et appeler la transition terminale P1E sur cette même référence.

Une nouvelle observation distincte reçue pendant cet état retourne `blocked_by_pending` ; elle n'est pas transformée en nouvelle révision.

## Causalité

- `observed_at` n'est jamais reconstruit depuis `end_time` ;
- `accepted_at` est capturé uniquement au succès de l'acceptation/promotion ;
- pending/quarantined restent sans `accepted_at` ;
- P1E n'implémente pas encore le moteur PIT, mais ses écritures doivent rendre possible la sélection `max(accepted_at) <= T` définie par P0 ;
- aucune transition P1E ne modifie un DatasetSnapshot existant.

## Tests requis

### Unitaires

- égalité logique et champs exclus de l'égalité ;
- stabilité attendue du fingerprint pour des valeurs identiques ;
- validation UTC des timestamps de commande/résultat ;
- mapping des résultats d'opération.

### Intégration PostgreSQL

- première ingestion crée `revision_seq = 1`, `accepted_current`, `accepted_at` et le pointeur courant atomiquement ;
- deux ingestions identiques successives n'ajoutent aucune révision ;
- observation distincte crée exactement une `pending_confirmation` avec le prochain `revision_seq` ;
- réobservation identique au pending ne crée rien ;
- observation différente pendant un pending retourne `blocked_by_pending` et n'alloue rien ;
- redémarrage/nouvelle instance du store retrouve le pending inchangé ;
- quarantaine conserve le seq et la candidate suivante utilise `max(seq) + 1` ;
- promotion conserve le seq, supersède l'ancienne courante, fixe `accepted_at` et déplace le pointeur dans une transaction ;
- promotion rejouée est idempotente ;
- quarantaine rejouée est idempotente ;
- tentative de promouvoir une révision quarantined échoue ;
- tentative d'appliquer un résultat à une ancienne révision non pending échoue ;
- `candles.current_revision_seq` pointe toujours une `accepted_current` après chaque transaction réussie ;
- aucune transaction ne peut laisser deux `accepted_current` ou deux `pending_confirmation` ;
- un `accepted_at < observed_at` est refusé ;
- concurrence sur une même lignée ne peut pas allouer deux candidates pending ni réutiliser un seq.

## Hors périmètre P1E

- appel CCXT ou Binance natif ;
- logique de concordance de confirmation OHLC/base_volume : P1G ;
- normalisation brute `ProviderOHLCV ->` valeurs canoniques ;
- calcul/versionnement de `after_values_fingerprint` ;
- gaps/qualité complète : P1F ;
- moteur de replay PIT ;
- snapshots Parquet ;
- WebSocket/intrabar ;
- retry réseau ou ordonnanceur de reprise.

## Gate P1E

Avec PostgreSQL actif et `BTC_ANALYTICS_DATABASE_URL` défini :

```powershell
uv run alembic current
uv run alembic check
uv run ruff check backend
uv run ruff format --check backend
uv run pyright
uv run pytest

git diff --check
git status --short --branch
```

Aucune migration Alembic n'est attendue a priori : P1D expose déjà les colonnes, clés différées et indexes requis. Si l'implémentation révèle qu'une modification du schéma est réellement nécessaire, elle doit être justifiée dans ce document avant création d'une migration.

## Gate local exécuté — 7 septembre 2026

Les contrôles ont été exécutés sur Python 3.14.7 avec PostgreSQL 18.6 accessible via `BTC_ANALYTICS_DATABASE_URL` :

- `uv run ruff check backend` : `All checks passed!` ;
- `uv run ruff format --check backend` : `21 files already formatted` ;
- `uv run pyright` : `0 errors, 0 warnings, 0 informations`, code de sortie `0` ;
- `uv run alembic current` : `0001_market_data_schema (head)` ;
- `uv run alembic check` : `No new upgrade operations detected.` ;
- `uv run pytest backend/tests/integration/test_revision_transitions.py` : `11 passed` ;
- `uv run pytest` : `81 passed, 1 skipped` ;
- le seul test ignoré est le smoke Binance P1C protégé par `BTC_ANALYTICS_RUN_BINANCE_INTEGRATION` ;
- `git diff --check` : aucune erreur.

Les tests PostgreSQL couvrent notamment la création concurrente d’une lignée unique, la sérialisation de candidates distinctes, l’allocation monotone des séquences, l’idempotence des replays, la persistance/reprise d’un pending, la promotion atomique, la quarantaine, le rejet des résultats hors ordre et la causalité de `accepted_at`.

## Revue finale des edge cases

La revue finale a identifié puis corrigé un gap défensif : `quarantine()` doit, comme `observe()` et `promote()`, vérifier sous verrou que `candles.current_revision_seq` référence effectivement une révision `accepted_current`. Un test PostgreSQL corrompt volontairement ce pointeur, vérifie que la quarantaine est refusée et que le pending reste inchangé.

Après ce correctif, la suite complète repasse à `81 passed, 1 skipped`, sans migration ni dépendance supplémentaire. Aucun blocage P1E restant n’a été identifié.

Ces résultats placent P1E au statut **`VALIDATION READY`**. La validation finale du jalon reste soumise à l’approbation explicite de l’utilisateur après création et revue du commit candidat.
