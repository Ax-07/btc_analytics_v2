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
