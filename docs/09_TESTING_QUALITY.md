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
- native confirmation agreement promotes the revision;
- disagreement/unavailable confirmation quarantines it and preserves current canonical state;
- accepted correction never mutates an existing DatasetSnapshot;
- `reconstructed_latest` and `observed_point_in_time` do not make the same historical-knowledge claim.

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
