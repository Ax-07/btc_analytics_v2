# BTC Analytics V2 — P0 Canonical v5

> Source maître consolidée pour audit dans le projet ChatGPT.
> P0 reste non validé tant que D-001 à D-020 ne sont pas explicitement approuvées.


---

## SOURCE FILE: `README.md`

# BTC Analytics V2

BTC Analytics V2 est une plateforme d'analyse quantitative et structurelle du marché Bitcoin.

Le projet repart volontairement de zéro au niveau du code afin d'éviter d'hériter de la dette architecturale de la V1. La V1 reste figée comme prototype de référence et source de leçons, mais son code n'est pas copié par défaut.

## Objectif

Transformer des données de marché en primitives causales, structures, événements et contextes mesurables, puis étudier objectivement ce qui s'est produit après leurs occurrences historiques.

BTC Analytics V2 n'est pas un bot de trading, un moteur d'exécution, un gestionnaire de portefeuille ou un système de recommandations buy/sell.

## Principes

1. Causalité stricte pour toute information déclarée connue à T.
2. Primitives objectives avant interprétations humaines.
3. Toute hypothèse analytique doit pouvoir être mesurée.
4. Séparation stricte entre production et recherche.
5. Les dépendances externes fournissent des briques ; l'intelligence métier reste développée dans BTC Analytics.
6. Les chart patterns sont optionnels et ne sont pas une fondation du projet.
7. Les patterns de chandeliers sont traités comme des événements analytiques, jamais comme des signaux de trading.

## Point de départ

Lire dans cet ordre :

1. `P0_START_HERE.md`
2. `docs/00_PROJECT_CHARTER.md`
3. `docs/01_ARCHITECTURE.md`
4. `docs/02_TECH_STACK.md`
5. `docs/03_DOMAIN_MODEL.md`
6. `docs/04_CAUSALITY.md`
7. `docs/11_ROADMAP.md`

## Source de vérité

En cas de contradiction :

1. décisions validées dans `docs/10_DECISIONS.md`
2. document métier/technique le plus spécifique
3. `docs/00_PROJECT_CHARTER.md`
4. `README.md`

Aucun code de production ne doit être écrit avant validation explicite de P0. La révision candidate v5 reste en attente de validation utilisateur.


---

## SOURCE FILE: `P0_START_HERE.md`

# P0 — Start Here

## Goal

P0 turns the V2 vision into a development contract before production code.

## Required reading

1. `P0_AUDIT_RESOLUTION.md`
2. `docs/00_PROJECT_CHARTER.md`
3. `docs/01_ARCHITECTURE.md`
4. `docs/02_TECH_STACK.md`
5. `docs/03_DOMAIN_MODEL.md`
6. `docs/04_CAUSALITY.md`
7. `docs/05_MARKET_DATA.md`
8. `docs/15_TEMPORAL_CONVENTIONS.md`
9. `docs/16_OUTCOME_BASELINE_CONVENTIONS.md`
10. `docs/17_DEPENDENCY_ASSESSMENT.md`
11. `docs/10_DECISIONS.md`
12. `docs/11_ROADMAP.md`

## P0 validation criteria

P0 is validated only when:

- project scope and non-scope are explicit;
- temporal coordinates are unambiguous;
- `features/`, `outcomes/` and `research/` boundaries are stable;
- Market/Candle/Event/Occurrence/Context/Outcome/Experiment identities are stable enough for independent implementations to agree;
- outcome/baseline conventions are explicit;
- market-data gap/revision/native-timeframe policies are explicit;
- dependency roles are documented;
- Decision Log D-001 through D-020 is explicitly approved;
- no blocking question remains.

## Rule

Do not begin P1 before explicit P0 validation.


---

## SOURCE FILE: `CURRENT_STATE.md`

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


---

## SOURCE FILE: `LESSONS_FROM_V1.md`

# Lessons from BTC Analytics V1

La V1 ne doit pas être considérée comme un échec. Elle a servi de prototype permettant d'identifier des invariants importants pour la V2.

## Ce qui doit être conservé conceptuellement

### Causalité explicite

Un phénomène physique peut appartenir à une bougie T sans être connaissable à T.

La V2 doit séparer `event_time` / `pivot_time` du moment `confirmed_at` / `known_at`.

### Forward Analysis séparé de la détection

La détection ne doit jamais utiliser le futur. Les outcomes futurs peuvent utiliser le futur uniquement après qu'une occurrence a été figée comme connue à T.

### Backend comme source analytique

Le frontend ne recalcule pas la logique analytique.

### Inspection visuelle indispensable

Une métrique ou un score ne suffit pas à valider une représentation structurelle.

### Les chart patterns sont subjectifs

La V2 privilégie swings, amplitudes, durées, retracements, pentes, compression/expansion et HH/HL/LH/LL. Les chart patterns deviennent optionnels.

## Ce qui doit être évité

- introduire une feature parce qu'elle est populaire en analyse technique ;
- calibrer des seuils avant de prouver l'utilité d'une représentation ;
- mélanger code de recherche et code de production ;
- laisser un fournisseur de données imposer ses objets au domaine ;
- ajouter trop tôt des couches UI ou abstractions sophistiquées ;
- optimiser avant profiling ;
- utiliser une méthode offline comme si elle était causale ;
- transformer le projet en moteur de stratégie/backtest.

## V1 figée

Dernier jalon de référence : `p8b-pattern-calibration-frontend`.

La V1 peut être consultée pour comparer les résultats, pas comme base de code de la V2.


---

## SOURCE FILE: `P0_AUDIT_RESOLUTION.md`

# P0 Audit Resolution — Consolidated v5

## Status

`P0 — VALIDATION CANDIDATE v5`

This revision closes the final blocker reported by the v4 audit.
It does not validate P0 and does not authorize P1.

## Previously resolved blockers

The v4 candidate already closed:

- deterministic parameter/occurrence identity via schema normalization, RFC 8785 JCS and SHA-256;
- deterministic late-candle revision acceptance via same-venue native confirmation, quarantine on disagreement/unavailability, immutable snapshots and explicit knowledge modes.

These contracts remain unchanged except for the point-in-time acceptance timing clarified below.

## Final blocker R3 — accepted revision time

The v4 model recorded `observed_at`, but strict `observed_point_in_time` replay could not distinguish a newly observed revision candidate from a revision already confirmed and accepted.

Resolved candidate contract in v5:

- `CandleRevision.observed_at` remains the earliest time BTC Analytics observed the revision;
- accepted revisions additionally record `accepted_at`, the instant confirmation succeeds and the revision becomes accepted canonical state;
- invariant: `observed_at <= accepted_at` for every accepted revision;
- quarantined revisions have no `accepted_at` and are never eligible for point-in-time canonical replay;
- in `observed_point_in_time`, the revision applicable at T is the accepted revision for the candle with the greatest `accepted_at` such that `accepted_at <= T`;
- a candidate observed at 10:00 and accepted at 10:05 cannot influence a replay at 10:02;
- `accepted_at` is temporal provenance and does not participate in semantic candle or occurrence identity.

## Decision update

D-020 now explicitly includes acceptance timing and the `accepted_at <= T` point-in-time replay rule.

## Tests added to the contract

Data revision tests must verify:

- an observed-but-not-yet-accepted candidate does not influence PIT replay;
- after acceptance, the revision becomes eligible from `accepted_at` onward;
- a quarantined candidate is never selected in PIT replay;
- replay chooses the latest accepted revision satisfying `accepted_at <= T`.

## Gate

P0 remains non-validated until the v5 audit concludes `P0 — VALIDATION READY` and the complete Decision Log D-001 to D-020 is explicitly approved by the user.


---

## SOURCE FILE: `SOURCE_INTEGRITY.md`

# Source Integrity — P0 v5

## Canonical ChatGPT source

Use a single source file:

`BTC_ANALYTICS_V2_P0_CANONICAL_v5.md`

Do not keep earlier P0 master files simultaneously in the same project sources.

## Required v5 markers

The canonical v5 source must contain all of the following:

- Decision Log D-001 through D-020;
- `RFC 8785` and `parameter_fingerprint`;
- exact `occurrence-key.v1` payload;
- `DatasetSnapshot` with `knowledge_mode`;
- `CandleRevision` model;
- `observed_at`;
- `accepted_at`;
- invariant `observed_at <= accepted_at` for accepted revisions;
- `revision acceptance policy v1`;
- `reconstructed_latest`;
- `observed_point_in_time`;
- PIT eligibility rule `accepted_at <= T`;
- quarantined revisions have no `accepted_at` and are never PIT-eligible;
- same-venue native confirmation and no cross-exchange replacement;
- Pyright;
- Basic Contexts in P5;
- Advanced Contexts & Regimes in P8;
- PostgreSQL current canonical authority;
- immutable Parquet snapshots;
- generalized prefix-invariance tests;
- data-revision tests covering observation-before-acceptance.

If an audit reports that these markers are absent, it is not reading the canonical v5 source.


---

## SOURCE FILE: `docs/00_PROJECT_CHARTER.md`

# 00 — Project Charter

## Vision

BTC Analytics V2 est une plateforme d'analyse quantitative et structurelle du marché Bitcoin.

Le système doit permettre de collecter et valider des données de marché fiables, calculer des features causales, représenter objectivement la structure du marché, détecter des événements reproductibles, caractériser des contextes/régimes, retrouver les occurrences historiques et mesurer ce qui s'est produit après chaque occurrence.

## Objectif central

> Lorsqu'une condition observable X est connue à T, comment la distribution du comportement futur du marché diffère-t-elle de sa distribution de référence ?

## Non-objectifs

V2 n'est pas :

- un bot de trading ;
- un moteur d'ordres ;
- un système buy/sell ;
- un gestionnaire de portefeuille ;
- une plateforme de copy trading ;
- un optimiseur de stratégie ;
- une plateforme ML par défaut.

## Scope initial

### Marché

- Bitcoin spot ;
- provider initial : Binance ;
- accès principal : CCXT derrière une abstraction interne ;
- marché initial : BTC/USDC côté provider ;
- timeframes : `1h`, `4h`, `1d` ;
- UTC canonique.

### Analyses

- momentum ;
- volatilité ;
- volume ;
- tendance ;
- extrema ;
- swings ;
- HH/HL/LH/LL ;
- retracements ;
- durées ;
- pentes ;
- compression / expansion ;
- événements techniques ;
- événements chandeliers ;
- contextes ;
- forward outcomes.

### Chart patterns

Les figures chartistes ne sont pas un objectif central. Elles pourront être ajoutées comme interprétations optionnelles si elles démontrent une valeur analytique supplémentaire.

## Principes

- causalité stricte ;
- explicabilité ;
- reproductibilité ;
- mesurabilité ;
- séparation recherche/production.

## Définition du succès

Le succès n'est pas d'accumuler des indicateurs. Le succès est d'obtenir un système où les données sont fiables, les features sont causales, les occurrences comparables, les outcomes cohérents, les expérimentations reproductibles et les analyses inutiles rejetables objectivement.


---

## SOURCE FILE: `docs/01_ARCHITECTURE.md`

# 01 — Architecture

## Vue conceptuelle

```text
Exchange
   |
   v
Market Data Access
   |
   v
Normalization + Validation
   |
   v
Canonical Market Data
   |
   +-------------------+
   |                   |
   v                   v
Causal Feature      Research Dataset
Engine              (Parquet/DuckDB)
   |
   v
Market Structure
   |
   v
Event Engine
   |
   v
Context Engine
   |
   v
Occurrence Store
   |
   +------------------------+
   |                        |
   v                        v
Product API            Outcome Engine
                            |
                            v
                       Experiment Engine
```

## Frontières obligatoires

- `market_data/` : accès exchange, pagination, normalisation, validation, stockage ; aucune logique analytique.
- `features/` : calculs strictement causaux.
- `structure/` : pivots, swings, HH/HL/LH/LL, retracements, métriques de segments.
- `events/` : événements timestampés construits à partir d'informations causales.
- `contexts/` : état de marché à T.
- `occurrences/` : instances figées d'une définition satisfaite.
- `outcomes/` : seule couche analytique autorisée à lire après T.
- `experiments/` : comparaisons de définitions, paramètres, timeframes, périodes.
- `research/` : zone non canonique ; look-ahead/offline autorisé s'il est déclaré.

## Backend / frontend

FastAPI expose les contrats internes. Le frontend ne dépend jamais directement de CCXT, TA-Lib, DuckDB, VectorBT ou SciPy et ne recalcule pas les features métier.

## Structure cible

```text
btc_analytics_v2/
├── backend/
│   ├── src/btc_analytics/
│   │   ├── api/
│   │   ├── domain/
│   │   ├── market_data/
│   │   ├── features/
│   │   ├── structure/
│   │   ├── events/
│   │   ├── contexts/
│   │   ├── occurrences/
│   │   ├── outcomes/
│   │   ├── experiments/
│   │   ├── storage/
│   │   └── observability/
│   └── tests/
├── frontend/
├── research/
├── docs/
├── infra/
└── pyproject.toml
```


---

## SOURCE FILE: `docs/02_TECH_STACK.md`

# 02 — Tech Stack

## Policy

External libraries provide generic primitives. BTC Analytics owns domain semantics, causal contracts, versioning and reproducibility.

Exact package versions are pinned in lockfiles at repository bootstrap after compatibility checks.

## ADOPT — product/runtime

- Python
- NumPy
- Polars
- SciPy
- CCXT behind `MarketDataProvider`
- TA-Lib behind internal adapters for selected validated functions
- PostgreSQL
- FastAPI
- Pydantic
- Alembic

## ADOPT — development

- uv
- pytest
- Ruff
- **Pyright**
- GitHub Actions
- Docker Compose

## ADOPT — frontend

- Next.js
- TypeScript
- pnpm
- Lightweight Charts
- shadcn/ui

## ADOPT — research/data snapshots

- Parquet
- DuckDB

## RESEARCH / REFERENCE

- VectorBT: vectorized experimentation concepts, grids and walk-forward; not product portfolio engine.
- ruptures: offline change-point research only until a causal formulation is validated.
- statsmodels: only when a concrete statistical need exists.

## REJECT as product dependencies

- PatternPy
- TradingPatternScanner

## TA-Lib scoped decision

TA-Lib may execute selected standard indicators and candlestick functions only when each selected function has:

- documented inputs/lookback;
- causal verification under BTC Analytics closed-candle semantics;
- golden tests;
- a BTC Analytics definition/version wrapper.

TA-Lib can additionally serve as a reference oracle for primitives implemented internally.

## Performance rule

1. correct algorithm;
2. vectorized NumPy/Polars implementation;
3. profiling;
4. Numba/Rust only for demonstrated bottlenecks.


---

## SOURCE FILE: `docs/03_DOMAIN_MODEL.md`

# 03 — Domain Model

## Shared identity primitives

### Canonical parameter representation

Every canonical analytical definition owns a parameter schema.

Before identity calculation:

- all schema defaults are materialized explicitly;
- object member names and enum/string values use their canonical schema spelling;
- unordered collections are sorted according to their definition-specific schema rule before serialization;
- timestamps, when parameters, use integer Unix epoch milliseconds UTC;
- non-finite numbers (`NaN`, `+Inf`, `-Inf`) are forbidden;
- exact decimal semantics must be represented as normalized decimal strings, not binary floating-point values.

Canonical parameter bytes are the UTF-8 bytes of the parameter object serialized with **RFC 8785 JSON Canonicalization Scheme (JCS)**.

Normalized decimal strings use:

- no leading `+`;
- `-0` normalized to `0`;
- no unnecessary leading integer zeros;
- no trailing fractional zeros;
- no decimal point when the fractional part is empty;
- base-10 plain notation unless a definition explicitly versions another representation.

Examples:

```text
"001.2300" -> invalid input form; normalized semantic value -> "1.23"
"-0.000"   -> "0"
"2.500"    -> "2.5"
```

### DefinitionIdentity

Every canonical analytical definition has:

- `definition_key`: stable namespaced key;
- `definition_version`: changes whenever semantics change;
- `parameters`: normalized canonical parameter object;
- `parameter_fingerprint`.

`parameter_fingerprint` is exactly:

```text
"sha256:" + lowercase_hex(SHA-256(JCS(parameters)))
```

The hash covers the normalized parameters only. Definition key/version remain explicit identity fields.

### Provenance

Canonical derived artifacts must be traceable to:

- market;
- timeframe;
- source data identity or DatasetSnapshot when applicable;
- definition key/version;
- parameter fingerprint;
- computation software revision/run when material.

## Market

- venue
- base_asset
- quote_asset
- market_type
- canonical_symbol

`canonical_symbol` is a BTC Analytics domain identifier and is independent from CCXT/provider notation.

## Candle

Canonical closed OHLCV bar:

- market
- timeframe
- `open_time`
- `end_time`
- open
- high
- low
- close
- `base_volume`
- optional `quote_volume`
- optional `trade_count`
- source
- source_symbol
- `available_at`
- `ingested_at`
- current accepted revision metadata

Identity:

```text
(market, timeframe, open_time)
```

The canonical interval is `[open_time, end_time)` and `available_at = end_time` in the initial reconstructed closed-candle analytical model.

## CandleRevision

Every changed observation of an already-known candle is represented explicitly.

Minimum fields:

- candle identity `(market, timeframe, open_time)`;
- monotonically increasing local `revision_seq`;
- normalized OHLCV values;
- `observed_at`;
- optional `accepted_at`;
- `revision_status`: `accepted_current`, `accepted_superseded`, `quarantined`;
- primary provider provenance;
- confirmation provenance when required;
- before/after logical value fingerprints;
- reason/audit metadata.

A later revision never mutates an immutable DatasetSnapshot.

`observed_at` is the earliest time BTC Analytics observed that revision. A correction observed later must never be represented as having been actually observed by the system at the historical candle `end_time`.

`accepted_at` is the instant at which required validation/confirmation succeeds and the revision becomes accepted canonical state. It is present only for revisions that have been accepted at least once (`accepted_current` or `accepted_superseded`). A quarantined revision has no `accepted_at`.

For every accepted revision:

```text
observed_at <= accepted_at
```

`accepted_at` is temporal provenance. It does not participate in Candle identity, DefinitionIdentity, `occurrence_key`, or any other semantic identity unless a future versioned contract explicitly says otherwise.

## FeatureDefinition / FeatureValue

A FeatureValue includes definition identity, market/timeframe, `event_time`, `known_at`, values and provenance.

## StructuralPoint

- `physical_time`
- `known_at`
- price
- kind
- definition identity
- metrics
- provenance

`physical_time < known_at` is valid for confirmed historical structure.

## StructuralSegment

Links structural points and records direction, return, ATR-normalized amplitude, duration, slope, velocity and retracement relationships.

Its `known_at` cannot precede the latest required input `known_at`.

## EventDefinition / Event

An Event is a versioned causal occurrence with:

- definition identity;
- `event_time`;
- `known_at`;
- evidence/values;
- deterministic `instance_discriminator`;
- provenance.

For a given DefinitionIdentity, market, timeframe and anchor candle, the default rule is at most one canonical event with `instance_discriminator = "0"`.

If a definition can emit multiple distinct canonical events for the same anchor, its versioned schema must define a deterministic non-empty `instance_discriminator`.

## ContextDefinition / ContextSnapshot

A ContextSnapshot is a causal state evaluated at an anchor candle using only artifacts whose `known_at <= anchor.end_time`.

## Occurrence

The central historical analysis unit.

Minimum fields:

- deterministic `occurrence_key`;
- definition identity;
- market/timeframe;
- `event_time` when physically meaningful;
- `known_at`;
- anchor candle identity;
- `instance_discriminator`;
- context reference/snapshot when used;
- provenance/input references.

### Occurrence key payload

The exact v1 identity payload is:

```json
{
  "schema": "occurrence-key.v1",
  "definition_key": "<canonical definition_key>",
  "definition_version": "<canonical definition_version>",
  "parameter_fingerprint": "sha256:<hex>",
  "market": "<canonical market symbol>",
  "timeframe": "<canonical timeframe>",
  "anchor_open_time_ms": 0,
  "event_time_ms": 0,
  "instance_discriminator": "0"
}
```

Rules:

- timestamps are integer Unix epoch milliseconds UTC;
- `event_time_ms` is the canonical physical/event attribution time; if the definition has no distinct physical attribution, it equals the anchor candle `end_time`;
- `instance_discriminator` defaults to `"0"`;
- context is **not** part of occurrence identity; contexts are attached analytical state and may be used for slicing without duplicating the occurrence;
- DatasetSnapshot is provenance, not occurrence identity, so the same semantic occurrence can be compared across snapshots/revisions.

`occurrence_key` is exactly:

```text
"sha256:" + lowercase_hex(SHA-256(JCS(occurrence_key_payload)))
```

Database insertion order, surrogate IDs and computation run IDs never participate in the key.

## OutcomeDefinition

Defines:

- metric key/version;
- horizon in bars;
- reference-price convention;
- future-window convention;
- gap policy;
- metric-specific parameters.

OutcomeDefinition parameter identity follows the same JCS/SHA-256 rule.

## Outcome

Attached to an Occurrence and OutcomeDefinition.

Outcome never changes the original occurrence and may be `complete`, `incomplete_gap` or `incomplete_end_of_dataset`.

## BaselineDefinition

Every experiment comparing conditional distributions must explicitly define its baseline population:

- market/timeframe;
- historical range;
- eligible anchor policy;
- context filter if any;
- same outcome/gap conventions;
- sampling policy/version.

BaselineDefinition identity follows the same DefinitionIdentity parameter canonicalization rules.

## DatasetSnapshot

Immutable experiment input identity containing at minimum:

- `snapshot_id`;
- source market/timeframes;
- temporal coverage;
- creation time;
- `knowledge_mode`;
- manifest/content hashes;
- gap summary;
- exact accepted CandleRevision references included in the snapshot.

Initial `knowledge_mode` values:

- `reconstructed_latest`;
- `observed_point_in_time` when sufficient observation/revision history exists.

The snapshot identity payload excludes creation time and includes:

- snapshot schema/version;
- market/timeframes;
- temporal coverage;
- knowledge mode;
- logical manifest hash of included candle identities + accepted revision identifiers.

`snapshot_id` is:

```text
"sha256:" + lowercase_hex(SHA-256(JCS(snapshot_identity_payload)))
```

Parquet is the initial physical format for immutable analytical snapshots. Physical Parquet byte layout is not used as the sole logical identity because different writers may encode equivalent logical data differently.

## ExperimentDefinition / ExperimentRun

A run freezes:

- DatasetSnapshot;
- analytical definition versions;
- parameter grid;
- OutcomeDefinitions;
- BaselineDefinition;
- split policy;
- software/config revision.


---

## SOURCE FILE: `docs/04_CAUSALITY.md`

# 04 — Causality Contract

## Absolute rule

If BTC Analytics says an artifact is known at T, no information after T may have contributed to it.

## Initial cadence

P0–P8 canonical analytics operate on **closed candles**.

Derived artifacts therefore become known on canonical candle boundaries unless a future milestone defines an explicit intrabar contract.

## Time coordinates

- candle `open_time`: inclusive start;
- candle `end_time`: exclusive end;
- candle `available_at`: `end_time` in historical closed-bar semantics;
- derived `event_time`/`physical_time`: where the phenomenon belongs;
- derived `known_at`: earliest canonical time at which all required evidence is available;
- `ingested_at`: system observation time, not a substitute for analytical `known_at`.

## Layer rules

### market_data

Open/provider-in-progress bars are not eligible for canonical analytical computation.

### features

Strictly causal. Forbidden without an explicit delayed `known_at` formulation:

- `shift(-1)`;
- centered windows;
- global-fit smoothing;
- full-series parameter fitting;
- future-confirmed extrema assigned retroactively to physical time.

### structure

May refer to a past physical point, but confirmation latency must be represented by `known_at`.

### events / contexts / occurrences

`known_at` equals or exceeds every required input's `known_at`.

### outcomes

Future use is allowed only after occurrence selection is frozen.

### research

Look-ahead/offline methods are permitted only when explicitly labeled research and cannot be promoted without a causal production contract.

## Mandatory prefix-invariance testing

Applies to every artifact declared known at T:

- FeatureValue;
- StructuralPoint;
- StructuralSegment;
- Event;
- ContextSnapshot;
- derived Occurrence.

Test protocol:

1. compute on the full series;
2. compute on historical prefixes ending at multiple T;
3. compare artifacts whose `known_at <= T`;
4. adding future bars must not alter their canonical identity/value/state.

Any legitimate later revision must be modeled as a new explicitly timestamped state/version, not silent retroactive mutation.


---

## SOURCE FILE: `docs/05_MARKET_DATA.md`

# 05 — Market Data

## Goal

Provide reliable exchange-independent closed candles for analytical use.

## Access architecture

```text
Exchange -> CCXT Adapter -> Provider DTO -> Normalizer -> Validator -> Canonical Candle
                                                     -> PostgreSQL current canonical store
                                                     -> Parquet immutable analytical snapshots
```

## Initial provider/market

- access library: CCXT;
- exchange: Binance Spot;
- provider symbol: `BTC/USDC`;
- internal canonical market identity is independent of CCXT notation.

The domain never imports CCXT types.

## Canonical candle semantics

- interval: `[open_time, end_time)`;
- UTC;
- P1 stores/uses closed candles for analytics;
- `available_at = end_time` describes historical market-time bar availability;
- provider-specific raw close timestamps may be retained as provenance only.

### Volume

Canonical `base_volume` is volume in the base asset (BTC for BTC/USDC).

If retained, quote activity is named `quote_volume`; trade count is `trade_count`. No ambiguous generic `volume` field is used in canonical domain contracts.

## Initial native timeframes

- `1h`
- `4h`
- `1d`

P1 fetches each timeframe natively from the provider. No canonical resampling is performed in P1.

Expected UTC alignment is validated.

If an exchange/provider does not support a required native timeframe, that market/timeframe is unsupported until a separate resampling contract is explicitly added.

## Validation

- timezone/interval alignment;
- OHLC invariants;
- non-negative volumes/counts;
- uniqueness;
- closed status/eligibility;
- monotonic ordering;
- duplicate detection;
- gap detection.

## Gap policy

A gap is never interpolated silently.

Canonical analytics treat gaps as hard continuity boundaries:

- rolling feature warm-up restarts after a gap when continuity is required;
- structural algorithms do not connect points across a gap by default;
- events/contexts depending on continuous history are unavailable until their requirements are satisfied again;
- an outcome horizon crossing a gap is `incomplete_gap`;
- ExperimentRun reports exclusions/incomplete counts.

## PostgreSQL authority

PostgreSQL is the **current canonical product store**.

Repeated observations that normalize to the same values are idempotent.

### Changed closed candle: revision acceptance policy v1

A different re-observation of an already stored closed candle never overwrites current state directly.

The deterministic flow is:

1. normalize the new observation;
2. validate all canonical invariants;
3. compare it with the current accepted revision;
4. if values are identical, do nothing except optional observation metadata;
5. if values differ, create a revision candidate and record `observed_at`;
6. confirm the candidate against the configured native authoritative endpoint for the **same venue and market**;
7. promote the candidate only if the normalized native confirmation agrees on canonical OHLC and `base_volume`;
8. when confirmed, record `accepted_at` at the successful promotion instant, mark the old revision `accepted_superseded`, the new revision `accepted_current`, increment `revision_seq`, and write the before/after audit entry;
9. if confirmation disagrees, is unavailable, or validation fails, mark the candidate `quarantined`, leave `accepted_at` absent, and leave PostgreSQL current canonical values unchanged.

For the initial Binance provider, the confirmation source is Binance native klines.

No observation from another exchange/venue can automatically replace the canonical Binance candle.

### Revision temporal semantics

Two notions must not be conflated:

- `available_at = end_time`: market-time availability of the completed candle in the reconstructed closed-bar model;
- `CandleRevision.observed_at`: when BTC Analytics first observed a particular revision candidate;
- `CandleRevision.accepted_at`: when validation/confirmation completed successfully and that revision became accepted canonical state.

For every accepted revision, `observed_at <= accepted_at`. A quarantined revision has no `accepted_at`.

A correction discovered later is never claimed to have been **system-observed** or **accepted** at the original `end_time`.

## Dataset knowledge modes

### `reconstructed_latest`

Default mode for historical analytical research.

The snapshot uses the accepted current revision for each candle at snapshot creation.

Causal feature/event sequencing is anchored to candle `end_time`, but the run must be described as a **reconstructed-latest historical analysis**. It must not claim that later provider corrections were actually known to BTC Analytics or a market participant at the original historical T.

This mode is appropriate for “analyse the best currently available reconstruction of history”.

### `observed_point_in_time`

Strict replay mode.

A candle revision may influence an anchor T only if it had already become accepted canonical state no later than T.

For a given candle, point-in-time replay selects the accepted revision with the greatest `accepted_at` satisfying:

```text
accepted_at <= T
```

`observed_at <= T` alone is insufficient: an observed candidate that had not yet passed confirmation at T cannot influence the replay. A quarantined revision is never eligible because it has no `accepted_at`.

Example: if a candidate is observed at 10:00 and accepted at 10:05, replay at 10:02 uses the previously accepted revision; replay at or after 10:05 may use the new accepted revision.

This mode is only valid for periods with sufficient continuous observation/revision provenance. Historical backfill predating BTC Analytics observation coverage cannot be silently treated as point-in-time observed history.

P0 defines the semantics; P1 does not need to implement a full live point-in-time replay engine unless explicitly scheduled.

## Parquet snapshots

Parquet snapshots are immutable derived datasets for reproducible analytics/research, not a second mutable authority.

Each DatasetSnapshot freezes:

- candle identities;
- exact accepted revision identifiers;
- knowledge mode;
- gaps;
- logical manifest/content hashes.

A later PostgreSQL candle correction never modifies an existing snapshot.

## Idempotence

Repeated fetches that normalize to the same canonical candle create no new semantic state.

## Cross-check P1

A bounded fixture/range compares CCXT Binance OHLCV with Binance-native kline data for timestamp/OHLC/base volume after normalization.

The same native path is used as confirmation only when a changed historical observation requires revision validation.

## Real-time

Out of P1. WebSocket/open-candle handling requires a later explicit intrabar/live contract.


---

## SOURCE FILE: `docs/06_ANALYTICS_METHODOLOGY.md`

# 06 — Analytics Methodology

## Hiérarchie

```text
OHLCV
  -> Primitive Features
  -> Market Structure
  -> Events
  -> Contexts
  -> Occurrences
  -> Forward Outcomes
```

## Features initiales

### Prix

returns, range, gaps, position dans range.

### Volatilité

true range, ATR, realized volatility, expansion/compression.

### Momentum

RSI, ROC, MACD seulement si justifié.

### Trend

slope, ADX, structure.

### Volume

volume brut, normalisé, changements relatifs.

### Structure

extrema, prominence, swings, HH/HL/LH/LL, amplitude ATR, duration, retracement, slope, compression/expansion.

## Events

Causaux, versionnés, timestampés, explicables, testables.

## Candlestick patterns

Shortlist à étudier :

- Doji
- Hammer
- Inverted Hammer
- Shooting Star
- Bullish Engulfing
- Bearish Engulfing
- Morning Star
- Evening Star
- Three White Soldiers
- Three Black Crows

Ils sont des événements, jamais des recommandations.

## Chart patterns

Optionnels. Une figure ne devient canonique que si sa définition est objective, causale, inspectable, stable et apporte une information supplémentaire mesurable.

## Mesure d'utilité

- nombre d'occurrences
- stabilité temporelle
- distribution conditionnelle des outcomes
- différence vs baseline
- robustesse multi-timeframe
- sensibilité aux paramètres
- robustesse walk-forward

## Langage

Éviter `buy`, `sell`, `entry`, `exit`, `take profit`, `stop loss` dans les contrats canoniques.


---

## SOURCE FILE: `docs/07_EXPERIMENT_ENGINE.md`

# 07 — Experiment Engine

## Goal

Compare analytical hypotheses using batch/vectorized parameter grids, without trading or portfolio simulation.

## Required frozen inputs

Every ExperimentRun records:

- DatasetSnapshot, including its `knowledge_mode` and exact CandleRevision manifest;
- historical range;
- timeframes;
- definition keys/versions;
- normalized parameter grid;
- OutcomeDefinitions;
- BaselineDefinition;
- split/walk-forward policy;
- software/config revision.

## Parameter dimensions

Examples: timeframe, feature parameters, structure parameters, context definition, outcome horizon.

## Outcome metrics

Initial standard metrics:

- forward close return;
- MFE;
- MAE;
- future volatility when its metric definition is versioned.

Exact temporal semantics live in `16_OUTCOME_BASELINE_CONVENTIONS.md`.

## Baseline

No experiment may rely on an implicit phrase such as “relevant baseline”. A BaselineDefinition is mandatory for comparative claims.

Default candidate baseline: all eligible anchor candles in the same market/timeframe/snapshot/date range, applying the same data-quality, gap and outcome-completeness rules as the conditional sample.

Alternative baselines must be explicit and versioned.

## Walk-forward

Calibration and evaluation periods are temporally separated. The run stores split boundaries and whether parameters were selected using earlier folds.

## Anti-overfitting

Require where relevant:

- out-of-sample evaluation;
- temporal stability;
- multi-timeframe robustness;
- parameter sensitivity;
- sample-size reporting.


## Identity reproducibility

Normalized experiment parameters use the canonical parameter representation defined in `03_DOMAIN_MODEL.md`:

- schema normalization;
- RFC 8785 JCS serialization;
- SHA-256 lowercase hex fingerprints.

ExperimentRun must record the exact parameter fingerprints used.

## Data revision semantics

An ExperimentRun never follows mutable PostgreSQL current state after launch.

It evaluates the immutable DatasetSnapshot it references.

If a later provider correction changes current canonical PostgreSQL values, a new snapshot/run is required. Results from different snapshots remain comparable through explicit snapshot identities and revision provenance.


---

## SOURCE FILE: `docs/08_RESEARCH_CATALOG.md`

# 08 — Research Catalog

This catalog is a decision index. Detailed evidence for structural dependencies is in `17_DEPENDENCY_ASSESSMENT.md`.

| Tool | Candidate status | Scope |
|---|---|---|
| NumPy | ADOPT | numerical arrays |
| Polars | ADOPT | dataframe/query engine |
| SciPy | ADOPT | scientific/signal primitives |
| CCXT | ADOPT | exchange access behind adapter |
| TA-Lib selected functions | ADOPT | validated standard indicators/candlesticks behind adapter |
| TA-Lib | REFERENCE | oracle/comparison where useful |
| PostgreSQL | ADOPT | current canonical product store |
| Parquet | ADOPT | immutable research snapshots |
| DuckDB | ADOPT research | analytical SQL over snapshots |
| FastAPI/Pydantic | ADOPT | API/contracts |
| uv | ADOPT dev | package/project management |
| Ruff | ADOPT dev | lint/format |
| Pyright | ADOPT dev | static typing |
| pytest | ADOPT dev | tests |
| VectorBT | RESEARCH/REFERENCE | vectorized experiment concepts |
| ruptures | RESEARCH | offline change-point research |
| statsmodels | RESEARCH / adopt-on-need | statistical methods |
| PatternPy | REJECT product | comparison only |
| TradingPatternScanner | REJECT product | comparison/research only |

## Mandatory evaluation dimensions

Function, method, causal implications, validation/testing, maintenance, performance fit, license, coupling, final scope.

A tool may have different statuses for different roles, but those roles must be explicit (e.g. TA-Lib execution vs oracle).


---

## SOURCE FILE: `docs/09_TESTING_QUALITY.md`

# 09 — Testing & Quality

## Tooling

- pytest
- Ruff
- Pyright
- GitHub Actions

## Test classes

### Unit

Normalization, indicators, structural metrics, event rules, outcome metrics, serializers.

### Invariants/property tests

OHLC validity, interval alignment, deterministic fingerprints, monotonic timestamps, gap rules, MFE/MAE conventions.

### Integration

CCXT -> normalize/validate -> PostgreSQL; snapshot -> DuckDB/Polars; feature -> structure/event/context -> occurrence -> outcome.

### Golden datasets

Versioned small fixtures for market normalization, selected TA-Lib parity, causal structure and outcomes.

### Causality/prefix invariance

Mandatory for every artifact declared known at T: feature, structural point/segment, event, context and derived occurrence.

### Data revision tests

Verify:

- same-value re-fetch is idempotent;
- changed source candle creates a revision candidate;
- native confirmation agreement promotes the revision and records `accepted_at`;
- every accepted revision satisfies `observed_at <= accepted_at`;
- disagreement/unavailable confirmation quarantines it, leaves `accepted_at` absent, and preserves current canonical state;
- an observed candidate is not PIT-eligible before `accepted_at`;
- PIT replay selects the accepted revision with greatest `accepted_at <= T`;
- a quarantined revision is never PIT-eligible;
- accepted correction never mutates an existing DatasetSnapshot;
- `reconstructed_latest` and `observed_point_in_time` do not make the same historical-knowledge claim;
- golden temporal fixture: candidate observed at 10:00 and accepted at 10:05 must not affect replay at 10:02 and may affect replay at 10:05 or later.

### Deterministic identity golden tests

Golden fixtures must lock:

- canonical parameter normalization;
- RFC 8785 JCS bytes;
- SHA-256 `parameter_fingerprint`;
- exact `occurrence_key` payload and resulting key;
- DatasetSnapshot logical identity.

At least one independent fixture representation must verify that semantically identical parameter objects with different input key ordering produce identical fingerprints.

## Definition of Done

A milestone is complete only when docs/contracts, tests, edge cases, causal checks, migrations/API/UI where applicable, CURRENT_STATE and Git milestone state are validated.

No milestone is called validated before actual local/CI command output is reviewed.


---

## SOURCE FILE: `docs/10_DECISIONS.md`

# 10 — Decision Log — P0 Candidate

Policy: decisions are append-only after validation. This candidate file does **not** mark them validated on behalf of the user.

| ID | Candidate decision | Status |
|---|---|---|
| D-001 | V2 is a greenfield repository; V1 code is not migrated automatically. | RECOMMENDED — AWAITING USER VALIDATION |
| D-002 | Product scope is analysis, not trading/portfolio/order/strategy execution. | RECOMMENDED — AWAITING USER VALIDATION |
| D-003 | Strict causality: no artifact known at T may use information after T. | RECOMMENDED — AWAITING USER VALIDATION |
| D-004 | CCXT is the initial exchange-access implementation behind an internal MarketDataProvider abstraction. | RECOMMENDED — AWAITING USER VALIDATION |
| D-005 | PostgreSQL is the current canonical product store; immutable Parquet snapshots serve reproducible research; DuckDB queries those snapshots. | RECOMMENDED — AWAITING USER VALIDATION |
| D-006 | Polars is the primary dataframe engine; NumPy/SciPy supply numerical/scientific primitives. | RECOMMENDED — AWAITING USER VALIDATION |
| D-007 | Selected TA-Lib functions may be ADOPTed only behind adapters after per-function causal/golden validation; TA-Lib can also serve as REFERENCE. | RECOMMENDED — AWAITING USER VALIDATION |
| D-008 | VectorBT is research/reference inspiration; its portfolio/trading engine is not a product dependency. | RECOMMENDED — AWAITING USER VALIDATION |
| D-009 | Candlestick patterns are analytical events, never trading signals. | RECOMMENDED — AWAITING USER VALIDATION |
| D-010 | Chart patterns are optional interpretation above market structure and require demonstrated incremental value. | RECOMMENDED — AWAITING USER VALIDATION |
| D-011 | Canonical Candle interval is `[open_time,end_time)` UTC; closed-bar analytical `available_at=end_time`; `ingested_at` is technical provenance. | RECOMMENDED — AWAITING USER VALIDATION |
| D-012 | P0–P8 canonical analytics operate on closed-candle cadence; intrabar semantics require a future explicit contract. | RECOMMENDED — AWAITING USER VALIDATION |
| D-013 | Outcome base price is anchor-candle close; horizon H uses the next H complete candles, excluding the anchor candle. | RECOMMENDED — AWAITING USER VALIDATION |
| D-014 | Every comparative ExperimentRun freezes an explicit BaselineDefinition. | RECOMMENDED — AWAITING USER VALIDATION |
| D-015 | P1 timeframes 1h/4h/1d are fetched natively; no canonical resampling; gaps are hard continuity boundaries. | RECOMMENDED — AWAITING USER VALIDATION |
| D-016 | Source candle corrections are audited; experiment reproducibility uses immutable DatasetSnapshots. | RECOMMENDED — AWAITING USER VALIDATION |
| D-017 | Pyright is the Python static type checker for V2. | RECOMMENDED — AWAITING USER VALIDATION |
| D-018 | Basic causal Context definitions move to P5; P8 is Advanced Contexts & Regimes. | RECOMMENDED — AWAITING USER VALIDATION |
| D-019 | Deterministic analytical identities use schema-normalized parameters, RFC 8785 JCS serialization and SHA-256 lowercase-hex fingerprints; `occurrence_key.v1` uses the exact canonical payload defined in the Domain Model. | RECOMMENDED — AWAITING USER VALIDATION |
| D-020 | Changed closed candles use revision-acceptance policy v1: validate, confirm against the same venue's native authoritative endpoint, promote only on agreement, otherwise quarantine; accepted revisions record `accepted_at` with `observed_at <= accepted_at`; `observed_point_in_time` selects only the latest accepted revision with `accepted_at <= T`; quarantined revisions are never PIT-eligible; snapshots never retroactively claim a late correction was observed or accepted at historical T. | RECOMMENDED — AWAITING USER VALIDATION |


---

## SOURCE FILE: `docs/11_ROADMAP.md`

# 11 — Roadmap

## P0 — Foundation

Charter, architecture, stack, domain identity/provenance, temporal conventions, causal contract, Market Data semantics, outcome/baseline conventions, dependency assessment, quality policy and decision log.

## P1 — Market Data

Repo bootstrap, PostgreSQL, CCXT adapter, canonical closed Candle, native 1h/4h/1d ingestion, validation, gaps, revision audit, idempotence, CCXT-vs-native fixture.

## P2 — Analytics Core

Time alignment, feature interface/registry, versioning/fingerprints, Polars/NumPy conventions, materialization policy.

## P3 — Technical Features

Returns/range, ATR, RSI, volatility, momentum, volume and selected standard features with causal/golden tests.

## P4 — Market Structure

Causal extrema, prominence, pivots/swings, HH/HL/LH/LL, amplitude, duration, slope, retracement, compression/expansion.

## P5 — Events, Occurrences & Basic Contexts

Event definitions, occurrence identity, technical/structural events, validated candlestick shortlist, basic causal ContextDefinition/ContextSnapshot and context-filtered occurrences.

## P6 — Forward Outcomes

Versioned OutcomeDefinitions, forward returns, MFE, MAE, future-volatility definition, completeness/gap states and baseline populations.

## P7 — Experiment Engine

DatasetSnapshots, parameter grids, multi-timeframe batch evaluation, BaselineDefinition, walk-forward and robustness reports.

## P8 — Advanced Contexts & Regimes

Richer state combinations, regime research, offline change-point exploration and causal promotion rules.

## P9 — Analytical Workbench

API + chart + structure/event/context inspection + occurrence/outcome/experiment comparison.

## P10 — Optional Analytics

Chart patterns or other interpretive models only if incremental value is demonstrated. P10 may remain empty.


---

## SOURCE FILE: `docs/12_CANDLESTICK_EVENTS.md`

# 12 — Candlestick Events

## Positionnement

Couche analytique prévue mais non fondamentale.

## Règles

Un candlestick pattern :

- est calculé sur candles clôturées ;
- possède `event_time` et `known_at` ;
- n'implique aucune recommandation ;
- est versionné ;
- utilise le même Outcome Engine que les autres événements.

## Shortlist initiale à étudier

Doji, Hammer, Inverted Hammer, Shooting Star, Bullish/Bearish Engulfing, Morning/Evening Star, Three White Soldiers, Three Black Crows.

## TA-Lib

Candidat principal pour implémentation et/ou oracle.

Avant adoption canonique : définition exacte, causalité, golden tests, conventions de sortie.

## Utilité

Mesurer le pattern seul puis conditionné par contexte : tendance, volatilité, structure, etc.


---

## SOURCE FILE: `docs/13_OPTIONAL_CHART_PATTERNS.md`

# 13 — Optional Chart Patterns

## Positionnement

Les chart patterns ne sont pas un objectif central.

## Ordre correct

```text
candles -> extrema -> swings -> structural metrics -> optional named pattern
```

## Conditions d'adoption

- définition objective
- causalité
- stabilité multi-timeframe
- qualité visuelle
- valeur incrémentale vs structure
- robustesse hors échantillon

Question centrale :

> Le label apporte-t-il une information supplémentaire par rapport aux swings, amplitudes, contexte et métriques de structure ?

Aucun milestone P0-P9 ne dépend des chart patterns.


---

## SOURCE FILE: `docs/14_OBSERVABILITY.md`

# 14 — Observability

## Minimum

Logs structurés avec component, operation, market, timeframe, run_id, duration, row counts et contexte d'erreur.

## Data quality metrics

candles fetched, duplicates rejected, gaps detected, invalid candles, latest closed candle, ingestion lag.

## Analytics metrics

feature rows, occurrences, experiment duration, parameter combinations, failures.

## Reproductibilité

Chaque batch significatif doit être relié à code version, config, dataset et timestamps.

Commencer simple ; ajouter OpenTelemetry/Prometheus uniquement en réponse à un besoin réel.


---

## SOURCE FILE: `docs/15_TEMPORAL_CONVENTIONS.md`

# 15 — Temporal Conventions

This document is the canonical temporal coordinate contract for P0.

## Candle coordinates

For timeframe duration `Δ`:

```text
open_time = t
end_time  = t + Δ
interval  = [t, t + Δ)
available_at = end_time
```

All canonical timestamps are UTC.

Provider-specific close timestamps that use inclusive final milliseconds are normalized and never redefine the canonical interval.

## Closed-bar analytical model

Initial V2 analytics use only complete candles. `available_at=end_time` expresses market-time historical availability of the complete OHLCV bar.

`ingested_at` records when BTC Analytics observed/stored a version and is not used to shift historical analytical anchors.

A future real-time/intrabar subsystem may additionally model system-observation latency, but must not change P0 historical semantics retroactively.

## Derived artifact timing

### Feature on candle C

- `event_time = C.end_time` unless the definition documents a physical-time alternative;
- `known_at = C.end_time` if all required inputs are available by then.

### Confirmed structural point

A pivot may have:

```text
physical_time = candle_100.end_time
known_at      = candle_103.end_time
```

The point belongs physically to 100 but is not eligible for occurrence selection before 103.

### Multi-bar event

The definition must state:

- physical/event attribution rule;
- last required evidence candle;
- `known_at = end_time` of that last required candle.

## Joins

A causal join at anchor T may include only records with `known_at <= T`.

Joining a structural point by physical time while ignoring its later `known_at` is a causality violation.


## Candle revisions and historical claims

`available_at=end_time` belongs to the reconstructed closed-bar market-time model.

A specific corrected `CandleRevision` additionally has `observed_at`.

Therefore:

- `reconstructed_latest` analyses may use the latest accepted revision while anchoring analytical bar sequencing at `end_time`, but must not claim that a later correction was actually known at historical T;
- `observed_point_in_time` analyses may use a revision at T only when its recorded `observed_at <= T`.

Historical periods without revision-observation provenance cannot be labeled `observed_point_in_time`.


---

## SOURCE FILE: `docs/16_OUTCOME_BASELINE_CONVENTIONS.md`

# 16 — Outcome & Baseline Conventions

## Anchor

Initial canonical occurrences are closed-candle anchored.

`Occurrence.known_at` corresponds to the `end_time` of an anchor candle A.

Default reference price:

```text
P0 = close(A)
```

The anchor candle itself is excluded from future excursion windows because its high/low occurred partly or entirely before the occurrence became known.

## Horizon H

Horizon `H` consists of the next H complete expected candles after A:

```text
A+1, A+2, ..., A+H
```

## Forward close return

```text
return_H = close(A+H) / P0 - 1
```

## MFE

```text
MFE_H = max(0, max(high(A+i) / P0 - 1)), i=1..H
```

Canonical MFE is therefore non-negative. If price never trades above P0 during the horizon, MFE is `0`.

## MAE

```text
MAE_H = min(0, min(low(A+i) / P0 - 1)), i=1..H
```

Canonical MAE is therefore non-positive. If price never trades below P0 during the horizon, MAE is `0`.

## Missing future

If the expected sequence A+1..A+H contains:

- a data gap -> `incomplete_gap`;
- end of available dataset -> `incomplete_end_of_dataset`.

No interpolation or shortening is allowed for a result labeled complete.

## Metric definitions

Future volatility and any additional metric require their own versioned OutcomeDefinition before canonical use.

## BaselineDefinition

Every comparative experiment stores an explicit baseline.

Default candidate baseline population:

- same DatasetSnapshot;
- same market/timeframe/date range;
- all eligible closed anchor candles;
- same gap/completeness rules;
- same OutcomeDefinitions;
- no condition/event filter unless explicitly declared.

A context-matched or regime-matched baseline is allowed only as a separate versioned BaselineDefinition.


## Dataset revision consistency

Conditional samples and their BaselineDefinition must use the same DatasetSnapshot and therefore the same:

- knowledge mode;
- candle revision set;
- gap state;
- temporal coverage.

A comparison between different snapshot revisions is a separate experiment/comparison dimension and must never be hidden inside a baseline.


---

## SOURCE FILE: `docs/17_DEPENDENCY_ASSESSMENT.md`

# 17 — Dependency Assessment

Verification date: 2026-09-06. Exact versions are pinned only at repository bootstrap.

## CCXT — ADOPT behind adapter

- Function: unified exchange/market-data access.
- Method: exchange-specific implementations exposed through a unified API including OHLCV retrieval.
- Causality: neutral; BTC Analytics must filter to closed bars and define its own temporal semantics.
- Validation: requires P1 cross-check against Binance-native klines.
- Maintenance: active project with Binance support and current unified OHLCV documentation.
- License: MIT.
- Coupling: medium if leaked; low when isolated behind `MarketDataProvider`.
- Decision: ADOPT as access layer, not domain model.

## Polars — ADOPT

- Function: dataframe/transformation engine.
- Method: Rust columnar engine, lazy query optimization, parallel execution and streaming.
- Causality: neutral; expressions must still obey BTC Analytics causal windows.
- Validation: strong project documentation and active development.
- Performance fit: excellent candidate for batch columnar analytics.
- License: MIT.
- Coupling: keep Polars objects inside computation/storage boundaries, not API/domain contracts.

## SciPy — ADOPT

- Function: scientific algorithms, statistics and signal primitives.
- Method: mature numerical/scientific implementations; `signal` can supply generic peak/prominence primitives.
- Causality: function-specific. Some filters/smoothers can be non-causal; each adopted use must be reviewed.
- Validation: mature project with extensive releases/tests.
- License: BSD-3-Clause.
- Coupling: low behind BTC Analytics feature/structure definitions.

## TA-Lib Python — scoped ADOPT + REFERENCE

- Function: standard technical indicators and candlestick pattern functions.
- Method: Python/Cython wrapper over TA-Lib core.
- Causality: function-specific; adoption requires per-function lookback/closed-bar validation.
- Validation: project classifies package as production/stable; wrappers/types are available for modern Python releases.
- Maintenance: active upstream in 2026.
- License: Python wrapper BSD-2-Clause; core uses BSD-family licensing.
- Coupling: medium if function names become domain contracts; mitigate with internal definition/adapters.
- Decision: selected validated functions ADOPT; oracle/reference use remains REFERENCE.

## DuckDB — ADOPT for research

- Function: local analytical SQL over Parquet/datasets.
- Method: in-process analytical database with direct Parquet scanning and pushdown.
- Causality: neutral; used after dataset construction.
- Validation: project documents extensive CI/testing, including millions of queries.
- Maintenance: active; project remains open source under independent foundation governance.
- License: MIT.
- Coupling: low because product API does not depend on DuckDB.

## FastAPI / Pydantic — ADOPT API boundary

- Function: typed HTTP API and schemas.
- Causality: neutral.
- License: FastAPI MIT; package versions/compatibility pinned at bootstrap.
- Coupling: intentionally limited to API/application layer; domain must remain framework-independent.

## uv — ADOPT development tooling

- Function: Python package/project/environment management.
- Method: Rust implementation and lock/project workflow.
- Causality/runtime: none.
- Maintenance: active and production-oriented.
- License: MIT OR Apache-2.0.
- Coupling: development only.

## Ruff — ADOPT development tooling

- Function: Python linting and formatting.
- Method: Rust implementation.
- Causality/runtime: none.
- License: MIT.
- Coupling: development only.

## Pyright — ADOPT development tooling

- Function: static Python type checking.
- Method: standards-based high-performance static checker.
- Causality/runtime: none.
- Maintenance: active project.
- License: MIT.
- Coupling: development only.

## pytest — ADOPT development tooling

- Function: test runner/framework.
- Causality/runtime: none in product; used to enforce causal invariants and integration contracts.
- License: MIT.
- Coupling: tests only.

## VectorBT — RESEARCH / REFERENCE

Use conceptual inspiration for vectorized parameter grids, broadcasting and walk-forward experimentation. Do not make product semantics or portfolio/trading abstractions depend on it.

## ruptures — RESEARCH

Offline change-point algorithms are research-only by default. Any production promotion requires a separately demonstrated causal formulation.

## PatternPy / TradingPatternScanner — REJECT product

Retain only as comparative/research references. They are not foundations of V2 market structure or chart-pattern semantics.
