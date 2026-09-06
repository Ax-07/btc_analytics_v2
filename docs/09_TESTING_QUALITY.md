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

- first valid ingestion creates `revision_seq = 1` as `accepted_current`;
- the initial accepted revision records `observed_at` and `accepted_at` with `observed_at <= accepted_at`;
- its exact revision reference is stable for DatasetSnapshot manifests;
- same-value re-fetch is idempotent and creates no new revision;
- changed source candle creates a persisted `pending_confirmation` revision with the next `revision_seq` before confirmation;
- pending candidate records `observed_at`, has no `accepted_at`, and is never PIT-eligible;
- same-value re-observation of the pending candidate is idempotent and allocates no new revision;
- at most one unresolved pending candidate exists per candle lineage and confirmation outcomes cannot be applied out of order;
- interruption/restart preserves pending state and never implies acceptance or quarantine;
- a quarantined candidate retains its allocated sequence and the next candidate does not reuse it;
- promotion preserves the candidate's already allocated `revision_seq`;
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
