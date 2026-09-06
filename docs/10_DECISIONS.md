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
| D-020 | Every canonical closed candle has an append-only revision lineage: first valid ingestion creates `revision_seq = 1` as `accepted_current` with `observed_at` and `accepted_at`; each later distinct observation allocates the next `revision_seq` at candidate creation and is persisted as `pending_confirmation` before native confirmation. Pending revisions have no `accepted_at`, are never PIT-eligible, survive interruption without implied acceptance, and are serialized to at most one unresolved pending candidate per candle lineage. Changed accepted candles are confirmed against the same venue's native authoritative endpoint; agreement transitions the same pending revision to `accepted_current` and supersedes the prior current revision, while disagreement/unavailability/validation failure transitions it to `quarantined` without renumbering. Accepted revisions satisfy `observed_at <= accepted_at`; `observed_point_in_time` selects only the latest accepted revision with `accepted_at <= T`; snapshots never retroactively claim a late correction was observed or accepted at historical T. | RECOMMENDED — AWAITING USER VALIDATION |

