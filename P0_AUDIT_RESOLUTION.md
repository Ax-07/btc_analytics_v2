# P0 Audit Resolution — Consolidated v6

## Status

`P0 — VALIDATION CANDIDATE v6`

This revision closes the two blockers reported by the independent v5 audits.
It does not validate P0 and does not authorize P1.

## Blocker R4 — stale point-in-time rule in temporal conventions

The v5 Market Data, Domain Model, Testing and D-020 contracts correctly used `accepted_at`, but `docs/15_TEMPORAL_CONVENTIONS.md` still allowed `observed_point_in_time` use when only `observed_at <= T`.

Resolved candidate contract in v6:

- `observed_at` records first system observation of a revision;
- `accepted_at` records when the revision becomes accepted canonical state;
- `observed_at <= T` alone is never sufficient for PIT eligibility;
- PIT selects the accepted revision with the greatest `accepted_at <= T`;
- quarantined revisions have no `accepted_at` and are never PIT-eligible.

## Blocker R5 — initial accepted CandleRevision lifecycle

The v5 contract described changed observations but did not explicitly define the first accepted revision of a newly ingested candle, while DatasetSnapshots require exact accepted CandleRevision references.

Resolved candidate contract in v6:

- the first valid observation of a new closed candle creates `CandleRevision` with `revision_seq = 1`;
- `observed_at` is the first time BTC Analytics observed that normalized candle;
- `accepted_at` is recorded when canonical validation succeeds and the revision becomes `accepted_current`;
- the initial revision does not require per-candle same-venue native confirmation; P1 provider correctness is instead covered by the bounded CCXT-vs-native validation fixture;
- each later distinct observation receives the next monotonically increasing `revision_seq` at candidate creation time;
- quarantined candidates retain their allocated `revision_seq` and have no `accepted_at`;
- promotion never renumbers a revision; it only changes acceptance state and records `accepted_at`;
- `(market, timeframe, open_time, revision_seq)` is the stable exact local revision reference used by snapshots/manifests.

## Decision update

D-020 now includes initial-revision creation, monotonic candidate numbering and the canonical PIT acceptance rule.

## Tests added to the contract

Data revision tests must verify:

- first valid ingestion creates revision 1 as `accepted_current`;
- initial accepted revision satisfies `observed_at <= accepted_at`;
- a later changed observation receives the next `revision_seq` before confirmation;
- quarantining does not reuse or renumber that sequence;
- promotion does not change the revision sequence;
- PIT uses only revisions with `accepted_at <= T`;
- exact snapshot revision references remain stable and reproducible.

## Gate

P0 remains non-validated until the v6 audit concludes `P0 — VALIDATION READY` and the complete Decision Log D-001 to D-020 is explicitly approved by the user.
