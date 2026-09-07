# P1D — Schéma PostgreSQL canonique

Statut : `VALIDATION READY — VALIDATION UTILISATEUR EN ATTENTE`

P1D matérialise dans PostgreSQL les contrats de données de marché déjà validés en P0 et implémentés côté domaine en P1B. Il n'implémente pas la machine transactionnelle des révisions de P1E.

## Sources canoniques

Ordre appliqué :

1. `docs/10_DECISIONS.md`, notamment D-003, D-005, D-011, D-015, D-016 et D-020 ;
2. `docs/03_DOMAIN_MODEL.md` ;
3. `docs/05_MARKET_DATA.md` ;
4. `docs/15_TEMPORAL_CONVENTIONS.md` ;
5. `docs/09_TESTING_QUALITY.md` ;
6. `docs/18_P1A_BACKEND_BOOTSTRAP.md` ;
7. `docs/19_P1B_MARKET_DATA_DOMAIN.md` ;
8. `docs/20_P1C_CCXT_PROVIDER.md`.

## Choix physiques P1D

Ces choix n'altèrent pas les identités canoniques :

1. `markets.market_id` est une clé technique PostgreSQL. L'identité métier reste portée par les cinq champs P0 et protégée par une contrainte d'unicité composite. `canonical_symbol` n'est pas déclaré unique isolément car P0 ne fixe pas cette contrainte.
2. `candles` porte l'identité canonique `(market, timeframe, open_time)`, les coordonnées temporelles et le pointeur exact `current_revision_seq`.
3. Les valeurs OHLCV et la provenance fournisseur ne sont pas dupliquées dans `candles` : `candle_revisions` en est la source unique. La `Candle` canonique courante se reconstruit par jointure sur la référence exacte `(market, timeframe, open_time, current_revision_seq)`.
4. Les deux clés étrangères circulaires nécessaires à cette référence exacte sont `DEFERRABLE INITIALLY DEFERRED`, afin que la première `Candle` et sa révision `revision_seq = 1` puissent être créées atomiquement dans une seule transaction P1E.
5. Les prix et volumes utilisent `NUMERIC` PostgreSQL sans précision/échelle arbitraire. Les valeurs spéciales `NaN` et ±`Infinity` sont interdites par contraintes.
6. Les timestamps utilisent `TIMESTAMPTZ`. PostgreSQL stocke l'instant ; l'application P1B conserve l'exigence d'entrées timezone-aware UTC.
7. Les timeframes restent des chaînes contraintes à `1h`, `4h`, `1d` plutôt qu'un enum PostgreSQL, afin de garder les migrations de vocabulaire explicites et simples.

## Tables

### `markets`

Champs métier :

- `venue` ;
- `base_asset` ;
- `quote_asset` ;
- `market_type` ;
- `canonical_symbol`.

La clé `market_id` est uniquement physique. Les cinq champs métier sont non vides et uniques en combinaison.

### `candles`

Clé primaire :

```text
(market_id, timeframe, open_time)
```

Champs :

- `end_time` ;
- `available_at` ;
- `ingested_at` ;
- `current_revision_seq`.

Contraintes :

- timeframe P1 natif ;
- alignement temporel sur la grille UTC par epoch ;
- `end_time = open_time + durée(timeframe)` ;
- `available_at = end_time` ;
- `current_revision_seq >= 1` ;
- référence différée vers la révision courante exacte.

### `candle_revisions`

Clé primaire exacte :

```text
(market_id, timeframe, open_time, revision_seq)
```

La table stocke les OHLCV normalisés, la provenance primaire, `observed_at`, `accepted_at`, `revision_status`, les fingerprints et les métadonnées d'audit.

Contraintes locales déjà déterminées par P0/P1B :

- `revision_seq >= 1` ;
- statuts exacts `pending_confirmation`, `accepted_current`, `accepted_superseded`, `quarantined` ;
- `revision_seq = 1` accepté uniquement ;
- `accepted_at` présent uniquement pour un état accepté ;
- `observed_at <= accepted_at` lorsqu'il existe ;
- OHLC cohérents ;
- volumes et `trade_count` non négatifs ;
- décimaux finis ;
- provenance/fingerprint obligatoire non vide.

## Indexes contractuels

- unicité partielle d'une seule `accepted_current` par lignée ;
- unicité partielle d'une seule `pending_confirmation` par lignée ;
- index PIT sur `(market_id, timeframe, open_time, accepted_at DESC)` pour les révisions acceptées.

Ces indexes imposent des invariants structurels mais ne réalisent pas les transitions : allocation du prochain `revision_seq`, idempotence, verrouillage/sérialisation, promotion et quarantaine restent P1E.

## Alembic

P1D introduit la première migration produit :

```text
0001_market_data_schema
```

`backend/alembic/env.py` référence désormais les métadonnées SQLAlchemy détenues par `btc_analytics.storage.schema`.

## Hors périmètre P1D

- normalisation `ProviderOHLCV -> Candle` ;
- orchestration transactionnelle des ingestions ;
- allocation monotone du prochain `revision_seq` ;
- comparaison/idempotence des observations ;
- machine `pending_confirmation -> accepted_current/quarantined` ;
- vérification que le pointeur courant référence effectivement un statut `accepted_current` au moment de chaque transition ;
- gaps et qualité complète P1F ;
- confirmation native / cross-check P1G ;
- snapshots Parquet.

## Gate local requis

Avec PostgreSQL 18.6 actif et `BTC_ANALYTICS_DATABASE_URL` défini :

```powershell
uv run alembic upgrade head
uv run alembic current
uv run alembic check
uv run ruff check backend
uv run ruff format --check backend
uv run pyright
uv run pytest

git diff --check
git status --short --branch
```

## Gate local exécuté — 7 septembre 2026

Les contrôles P1D ont été exécutés sur l’environnement local Python 3.14.7 avec PostgreSQL 18.6 :

- `docker compose -f .\infra\compose.yaml ps` : PostgreSQL `healthy` ;
- `uv run alembic upgrade head` : migration `0001_market_data_schema` appliquée avec succès ;
- `uv run alembic current` : `0001_market_data_schema (head)` ;
- `uv run alembic check` : `No new upgrade operations detected.` ;
- `uv run ruff check backend` : `All checks passed!` ;
- `uv run ruff format --check backend` : `17 files already formatted` ;
- `uv run pyright` : `0 errors, 0 warnings, 0 informations`, code de sortie `0` ;
- `uv run pytest` : `64 passed, 1 skipped` ;
- le seul test ignoré est le smoke Binance P1C protégé par `BTC_ANALYTICS_RUN_BINANCE_INTEGRATION` ;
- `git diff --check` : aucune erreur.

Les tests d’intégration PostgreSQL confirment en particulier :

- l’existence effective de `markets`, `candles` et `candle_revisions` après migration ;
- l’insertion atomique d’une première bougie avec `current_revision_seq = 1` et sa `CandleRevision` `accepted_current` grâce aux clés étrangères `DEFERRABLE INITIALLY DEFERRED` ;
- l’impossibilité de conserver deux révisions `pending_confirmation` simultanées pour une même lignée.

La revue finale distingue volontairement deux niveaux d’invariants : le DDL P1D garantit la référence exacte de révision et les contraintes structurelles locales ; la vérification transactionnelle qu’un `candles.current_revision_seq` pointe, après chaque transition, vers la révision au statut `accepted_current` reste P1E. L’imposer dès P1D exigerait une mécanique supplémentaire de trigger ou une redondance de statut sans valeur analytique propre. Ce choix ne modifie pas le contrat P0 : P1E devra maintenir cet invariant atomiquement lors des promotions/quarantaines.

Ces résultats placent P1D au statut **`VALIDATION READY`**. La validation finale du jalon reste soumise à l’approbation explicite de l’utilisateur après création et revue du commit candidat.
