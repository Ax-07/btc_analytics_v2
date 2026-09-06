# P0 Audit Resolution — Consolidated v4

## Status

`P0 — VALIDATION CANDIDATE v4`

This revision directly closes the two remaining blockers reported by the v3 audit.
It does not validate P0 and does not authorize P1.

## Remaining blocker R1 — deterministic identity

Resolved candidate contract:

- parameter defaults/schema normalization are explicit;
- exact decimals are canonical decimal strings;
- canonical serialization is RFC 8785 JSON Canonicalization Scheme;
- `parameter_fingerprint = sha256(JCS(parameters))`;
- `occurrence_key.v1` has an exact field set and canonical JCS/SHA-256 calculation;
- DatasetSnapshot identity is logical/content addressed rather than tied to Parquet writer bytes;
- golden identity fixtures are mandatory.

## Remaining blocker R2 — late candle revisions

Resolved candidate contract:

- changed historical observation creates a revision candidate;
- same-value refetch is idempotent;
- candidate is confirmed against the same venue's native authoritative endpoint;
- promotion occurs only on normalized OHLC/base-volume agreement;
- disagreement/unavailable confirmation -> quarantine; current canonical store unchanged;
- accepted revisions are append-only audited and snapshots never mutate;
- `reconstructed_latest` explicitly means best current historical reconstruction and cannot claim late corrections were known at historical T;
- `observed_point_in_time` may only use revisions actually observed by T and is valid only where observation provenance exists.

## Editorial cleanup

The stale `candidate v2` wording in README has been replaced with v4.

## New candidate decisions

- D-019 — deterministic identity convention;
- D-020 — candle revision acceptance and knowledge semantics.

## Gate

P0 remains non-validated until the complete Decision Log D-001 to D-020 is explicitly approved by the user after final audit.
