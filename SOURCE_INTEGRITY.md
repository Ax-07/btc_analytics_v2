# Source Integrity — P0 v4

## Canonical ChatGPT source

Use a single source file:

`BTC_ANALYTICS_V2_P0_CANONICAL_v4.md`

Do not keep earlier P0 master files simultaneously in the same project sources.

## Required v4 markers

The canonical v4 source must contain all of the following:

- Decision Log D-001 through D-020;
- `RFC 8785` and `parameter_fingerprint`;
- exact `occurrence-key.v1` payload;
- `DatasetSnapshot` with `knowledge_mode`;
- CandleRevision model;
- `revision acceptance policy v1`;
- `reconstructed_latest`;
- `observed_point_in_time`;
- Pyright;
- Basic Contexts in P5;
- Advanced Contexts & Regimes in P8;
- PostgreSQL current canonical authority;
- immutable Parquet snapshots;
- generalized prefix-invariance tests.

If an audit reports that these markers are absent, it is not reading the canonical v4 source.
