# Source Integrity — P0 v7

## Canonical ChatGPT source

Use a single source file:

`BTC_ANALYTICS_V2_P0_CANONICAL_v7.md`

Do not keep earlier P0 master files simultaneously in the same project sources.

## Required v7 markers

The canonical v7 source must contain all of the following:

- Decision Log D-001 through D-020;
- `RFC 8785` and `parameter_fingerprint`;
- exact `occurrence-key.v1` payload;
- `DatasetSnapshot` with `knowledge_mode`;
- `CandleRevision` model;
- initial accepted revision with `revision_seq = 1`;
- stable exact revision reference `(market, timeframe, open_time, revision_seq)`;
- subsequent distinct observations allocate the next `revision_seq` at candidate creation;
- `revision_status` includes `pending_confirmation`, `accepted_current`, `accepted_superseded`, `quarantined`;
- pending candidates have `observed_at`, no `accepted_at`, and are never PIT-eligible;
- at most one unresolved pending candidate per candle lineage;
- pending confirmation survives interruption/restart without implying acceptance;
- quarantined candidates retain their allocated sequence and have no `accepted_at`;
- `observed_at`;
- `accepted_at`;
- invariant `observed_at <= accepted_at` for accepted revisions;
- `revision acceptance policy v1`;
- `reconstructed_latest`;
- `observed_point_in_time`;
- PIT eligibility rule `accepted_at <= T`;
- `observed_at <= T` alone is insufficient for PIT;
- quarantined revisions are never PIT-eligible;
- same-venue native confirmation for changed accepted candles and no cross-exchange replacement;
- initial ingestion does not require per-candle native confirmation;
- Pyright;
- Basic Contexts in P5;
- Advanced Contexts & Regimes in P8;
- PostgreSQL current canonical authority;
- immutable Parquet snapshots;
- generalized prefix-invariance tests;
- data-revision tests covering initial revision, pending confirmation, observation-before-acceptance, quarantine and recovery.

If an audit reports that these markers are absent, it is not reading the canonical v7 source.
