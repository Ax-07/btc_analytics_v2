# P0 Audit Resolution — Consolidated v5

## Status

`P0 — VALIDATION CANDIDATE v5`

This revision closes the final blocker reported by the v4 audit.
It does not validate P0 and does not authorize P1.

## Previously resolved blockers

The v4 candidate already closed:

- deterministic parameter/occurrence identity via schema normalization, RFC 8785 JCS and SHA-256;
- deterministic late-candle revision acceptance via same-venue native confirmation, quarantine on disagreement/unavailability, immutable snapshots and explicit knowledge modes.

These contracts remain unchanged except for the point-in-time acceptance timing clarified below.

## Final blocker R3 — accepted revision time

The v4 model recorded `observed_at`, but strict `observed_point_in_time` replay could not distinguish a newly observed revision candidate from a revision already confirmed and accepted.

Resolved candidate contract in v5:

- `CandleRevision.observed_at` remains the earliest time BTC Analytics observed the revision;
- accepted revisions additionally record `accepted_at`, the instant confirmation succeeds and the revision becomes accepted canonical state;
- invariant: `observed_at <= accepted_at` for every accepted revision;
- quarantined revisions have no `accepted_at` and are never eligible for point-in-time canonical replay;
- in `observed_point_in_time`, the revision applicable at T is the accepted revision for the candle with the greatest `accepted_at` such that `accepted_at <= T`;
- a candidate observed at 10:00 and accepted at 10:05 cannot influence a replay at 10:02;
- `accepted_at` is temporal provenance and does not participate in semantic candle or occurrence identity.

## Decision update

D-020 now explicitly includes acceptance timing and the `accepted_at <= T` point-in-time replay rule.

## Tests added to the contract

Data revision tests must verify:

- an observed-but-not-yet-accepted candidate does not influence PIT replay;
- after acceptance, the revision becomes eligible from `accepted_at` onward;
- a quarantined candidate is never selected in PIT replay;
- replay chooses the latest accepted revision satisfying `accepted_at <= T`.

## Gate

P0 remains non-validated until the v5 audit concludes `P0 — VALIDATION READY` and the complete Decision Log D-001 to D-020 is explicitly approved by the user.
