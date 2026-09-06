# 10 — Decision Log — P0 Validated

Policy: D-001 through D-020 were explicitly approved by the user on 2026-09-06 and are now validated, append-only historical decisions. Any future semantic change requires an explicit new/versioned decision and must not silently rewrite these entries.

| ID | Validated decision | Status |
|---|---|---|
| D-001 | V2 is a greenfield repository; V1 code is not migrated automatically. | VALIDATED — USER APPROVED 2026-09-06 |
| D-002 | Product scope is analysis, not trading/portfolio/order/strategy execution. | VALIDATED — USER APPROVED 2026-09-06 |
| D-003 | Strict causality: no artifact known at T may use information after T. | VALIDATED — USER APPROVED 2026-09-06 |
| D-004 | CCXT is the initial exchange-access implementation behind an internal MarketDataProvider abstraction. | VALIDATED — USER APPROVED 2026-09-06 |
| D-005 | PostgreSQL is the current canonical product store; immutable Parquet snapshots serve reproducible research; DuckDB queries those snapshots. | VALIDATED — USER APPROVED 2026-09-06 |
| D-006 | Polars is the primary dataframe engine; NumPy/SciPy supply numerical/scientific primitives. | VALIDATED — USER APPROVED 2026-09-06 |
| D-007 | Selected TA-Lib functions may be ADOPTed only behind adapters after per-function causal/golden validation; TA-Lib can also serve as REFERENCE. | VALIDATED — USER APPROVED 2026-09-06 |
| D-008 | VectorBT is research/reference inspiration; its portfolio/trading engine is not a product dependency. | VALIDATED — USER APPROVED 2026-09-06 |
| D-009 | Candlestick patterns are analytical events, never trading signals. | VALIDATED — USER APPROVED 2026-09-06 |
| D-010 | Chart patterns are optional interpretation above market structure and require demonstrated incremental value. | VALIDATED — USER APPROVED 2026-09-06 |
| D-011 | Canonical Candle interval is `[open_time,end_time)` UTC; closed-bar analytical `available_at=end_time`; `ingested_at` is technical provenance. | VALIDATED — USER APPROVED 2026-09-06 |
| D-012 | P0–P8 canonical analytics operate on closed-candle cadence; intrabar semantics require a future explicit contract. | VALIDATED — USER APPROVED 2026-09-06 |
| D-013 | Outcome base price is anchor-candle close; horizon H uses the next H complete candles, excluding the anchor candle. | VALIDATED — USER APPROVED 2026-09-06 |
| D-014 | Every comparative ExperimentRun freezes an explicit BaselineDefinition. | VALIDATED — USER APPROVED 2026-09-06 |
| D-015 | P1 timeframes 1h/4h/1d are fetched natively; no canonical resampling; gaps are hard continuity boundaries. | VALIDATED — USER APPROVED 2026-09-06 |
| D-016 | Source candle corrections are audited; experiment reproducibility uses immutable DatasetSnapshots. | VALIDATED — USER APPROVED 2026-09-06 |
| D-017 | Pyright is the Python static type checker for V2. | VALIDATED — USER APPROVED 2026-09-06 |
| D-018 | Basic causal Context definitions move to P5; P8 is Advanced Contexts & Regimes. | VALIDATED — USER APPROVED 2026-09-06 |
| D-019 | Deterministic analytical identities use schema-normalized parameters, RFC 8785 JCS serialization and SHA-256 lowercase-hex fingerprints; `occurrence_key.v1` uses the exact canonical payload defined in the Domain Model. | VALIDATED — USER APPROVED 2026-09-06 |
| D-020 | Every canonical closed candle has an append-only revision lineage: first valid ingestion creates `revision_seq = 1` as `accepted_current` with `observed_at` and `accepted_at`; each later distinct observation allocates the next `revision_seq` at candidate creation and is persisted as `pending_confirmation` before native confirmation. Pending revisions have no `accepted_at`, are never PIT-eligible, survive interruption without implied acceptance, and are serialized to at most one unresolved pending candidate per candle lineage. Changed accepted candles are confirmed against the same venue's native authoritative endpoint; agreement transitions the same pending revision to `accepted_current` and supersedes the prior current revision, while disagreement/unavailability/validation failure transitions it to `quarantined` without renumbering. Accepted revisions satisfy `observed_at <= accepted_at`; `observed_point_in_time` selects only the latest accepted revision with `accepted_at <= T`; snapshots never retroactively claim a late correction was observed or accepted at historical T. | VALIDATED — USER APPROVED 2026-09-06 |

