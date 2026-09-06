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
