# P1B — Domaine des données de marché

Statut : `VALIDATION READY — VALIDATION UTILISATEUR EN ATTENTE`

P1B implémente les contrats de domaine déjà validés en P0. Il ne redéfinit pas la sémantique des données de marché et n'ajoute aucune décision au journal `docs/10_DECISIONS.md`.

## Sources canoniques

Ordre appliqué conformément à la gouvernance du projet :

1. `docs/10_DECISIONS.md`, notamment D-003, D-011, D-012, D-015, D-016 et D-020 ;
2. `docs/03_DOMAIN_MODEL.md` ;
3. `docs/05_MARKET_DATA.md` ;
4. `docs/15_TEMPORAL_CONVENTIONS.md` ;
5. `docs/09_TESTING_QUALITY.md` ;
6. `docs/18_P1A_BACKEND_BOOTSTRAP.md` pour le découpage des sous-jalons P1.

## Matrice canon -> implémentation P1B

| Sujet | Contrat déjà validé | Implémentation P1B |
|---|---|---|
| `Market` | `venue`, `base_asset`, `quote_asset`, `market_type`, `canonical_symbol` | valeur de domaine immuable ; aucune dépendance CCXT |
| `canonical_symbol` | identifiant BTC Analytics indépendant du fournisseur | chaîne opaque ; aucun format supplémentaire inventé |
| `Timeframe` | `1h`, `4h`, `1d`, natifs en P1 | `StrEnum` fermé sur ces trois valeurs + durée canonique |
| Temps | UTC, `[open_time,end_time)`, `available_at=end_time` | `datetime` timezone-aware UTC + validation d'alignement |
| `Candle` | OHLCV clôturée, identité `(market,timeframe,open_time)` | valeur de domaine immuable + invariants OHLCV/temps |
| Volume | `base_volume` canonique ; `quote_volume` et `trade_count` optionnels | champs explicites, aucun champ ambigu `volume` |
| `CandleRevision` | lignée append-only et référence exacte `(market,timeframe,open_time,revision_seq)` | valeur de domaine immuable + statuts canoniques |
| Statuts | `pending_confirmation`, `accepted_current`, `accepted_superseded`, `quarantined` | `StrEnum` avec orthographe canonique exacte |
| Acceptation temporelle | révision acceptée : `observed_at <= accepted_at` ; pending/quarantined sans `accepted_at` | invariants d'état locaux |
| Transitions de révision | politique D-020 | **hors P1B**, implémentation en P1E |
| Gaps | frontières dures | **hors P1B**, implémentation en P1F |
| Fournisseur | CCXT derrière `MarketDataProvider` | **hors P1B**, implémentation en P1C |
| PostgreSQL | stockage produit canonique courant | **hors P1B**, implémentation en P1D |
| Cross-check | CCXT vs Binance native | **hors P1B**, implémentation en P1G |

## Choix d'implémentation P1B

Ces choix ne modifient pas les contrats P0 :

1. Les objets du domaine utilisent des `dataclass` standard immuables (`frozen=True`, `slots=True`) afin de ne dépendre ni de Pydantic, ni de SQLAlchemy, ni de CCXT.
2. Les prix et volumes canoniques utilisent `Decimal` dans le domaine. Ce choix évite d'introduire une sémantique de flottant binaire dans les valeurs canoniques et laisse aux couches analytiques futures la responsabilité des conversions vectorisées nécessaires.
3. Les timestamps de domaine utilisent des `datetime` timezone-aware avec offset UTC nul. Aucun timestamp naïf n'est accepté.
4. `market_type` et `canonical_symbol` restent des chaînes opaques validées uniquement comme non vides : P0 ne définit pas encore de vocabulaire exhaustif ni de format dérivé pour ces champs.
5. `CandleRevision` valide uniquement les invariants d'un état pris isolément. La création atomique, l'idempotence, la sérialisation des candidates et les transitions `pending_confirmation -> accepted_current/quarantined` restent strictement dans P1E.
6. Les fingerprints logiques de révision sont portés comme valeurs opaques dans P1B. Leur algorithme de calcul n'est pas inventé ici ; un contrat ultérieur doit le fixer avant génération automatique.

## Invariants couverts dans P1B

### `Market`

- les cinq composantes d'identité sont présentes et non blanches ;
- aucune notation CCXT n'est importée dans le domaine.

### `Timeframe`

- seules les valeurs P1 validées `1h`, `4h`, `1d` existent ;
- durée canonique respective : 1 heure, 4 heures, 1 jour ;
- alignement UTC : heure pleine pour `1h`, heure multiple de 4 pour `4h`, minuit UTC pour `1d`.

### `Candle`

- tous les timestamps sont UTC ;
- `open_time` est aligné sur le timeframe ;
- `end_time = open_time + timeframe.duration` ;
- `available_at = end_time` ;
- `high >= open`, `high >= close`, `high >= low` ;
- `low <= open`, `low <= close`, `low <= high` ;
- prix et volumes décimaux finis ;
- `base_volume >= 0` ;
- `quote_volume >= 0` lorsqu'il est présent ;
- `trade_count >= 0` lorsqu'il est présent ;
- `current_revision_seq >= 1` ;
- identité exacte `(market, timeframe, open_time)`.

### `CandleRevision`

- `revision_seq >= 1` ;
- `revision_seq = 1` ne peut être ni `pending_confirmation` ni `quarantined` : la première révision est créée comme `accepted_current` et peut ensuite devenir `accepted_superseded` ;
- valeurs OHLCV soumises aux mêmes invariants que `Candle` ;
- `open_time` UTC et aligné ;
- `observed_at` UTC ;
- `accepted_at` UTC lorsqu'il est présent ;
- `accepted_current` et `accepted_superseded` exigent `accepted_at` ;
- `pending_confirmation` et `quarantined` interdisent `accepted_at` ;
- toute révision acceptée satisfait `observed_at <= accepted_at` ;
- référence exacte `(market, timeframe, open_time, revision_seq)`.

## Ce que P1B ne fait pas

P1B ne réalise pas :

- l'accès réseau à Binance ou CCXT ;
- la normalisation d'un DTO fournisseur ;
- la persistance PostgreSQL ;
- l'allocation transactionnelle de `revision_seq` ;
- la machine de transitions des révisions ;
- le replay PIT ;
- la détection ou propagation des gaps ;
- le resampling ;
- le WebSocket ou les bougies ouvertes.

## Fichiers P1B

- `backend/src/btc_analytics/domain/market_data.py` ;
- `backend/src/btc_analytics/domain/__init__.py` ;
- `backend/tests/domain/test_market_data.py` ;
- `docs/19_P1B_MARKET_DATA_DOMAIN.md` ;
- `CURRENT_STATE.md`.

## Gate local exécuté — 7 septembre 2026

Les commandes requises ont été exécutées sur l'environnement local Python 3.14.7 après la correction finale de l'invariant `revision_seq = 1` :

- `uv run ruff check backend` : `All checks passed!` ;
- `uv run ruff format --check backend` : `11 files already formatted` ;
- `uv run pyright` : `0 errors, 0 warnings, 0 informations` ;
- `uv run pytest` : `26 passed` ;
- `git diff --check` : aucune erreur ;
- `git status --short --branch` : uniquement les cinq fichiers P1B attendus sont modifiés/ajoutés.

La suite comprend 24 tests du domaine P1B et les 2 tests déjà présents dans le socle P1A.

La revue finale des edge cases a vérifié explicitement que `revision_seq = 1` ne peut pas représenter une révision `pending_confirmation` ou `quarantined`, conformément à D-020.

Ces résultats placent P1B au statut **`VALIDATION READY`**. La validation finale du jalon reste soumise à l'approbation explicite de l'utilisateur après revue finale de l'état Git.
