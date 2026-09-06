# P0 Audit Resolution — Consolidated v7

## Status

`P0 — VALIDATED`

This revision closes the final blocker reported by the independent v6 audit. Two independent final v7 audits subsequently concluded `P0 — VALIDATION READY`. On 2026-09-06, the user explicitly approved D-001 through D-020 in block. P0 is therefore validated and P1 is authorized to begin from these frozen contracts.

## Previously resolved v6 blockers

The v6 candidate already closed:

- the stale `observed_at <= T` point-in-time rule in Temporal Conventions, replacing it with the canonical `accepted_at <= T` rule;
- the initial accepted `CandleRevision` lifecycle, including `revision_seq = 1`, stable local revision references and monotonic sequence allocation at candidate creation.

Those contracts remain unchanged.

## Blocker R6 — unresolved revision candidate state

The v6 model created a distinct revision candidate and allocated its `revision_seq` before same-venue native confirmation, but the allowed `revision_status` values were only `accepted_current`, `accepted_superseded`, and `quarantined`. No status represented the real interval between candidate creation and confirmation resolution.

Resolved candidate contract in v7:

- `revision_status` additionally includes `pending_confirmation`;
- a later distinct observation of an already accepted candle creates a durable `pending_confirmation` revision with the next `revision_seq`, `observed_at`, and no `accepted_at`;
- `pending_confirmation` is never eligible for `observed_point_in_time`;
- successful native confirmation transitions that same revision to `accepted_current`, records `accepted_at`, and moves the previous current accepted revision to `accepted_superseded`;
- disagreement, unavailable confirmation, or validation failure transitions the same revision to `quarantined`, retaining its sequence and leaving `accepted_at` absent;
- promotion/quarantine never renumbers the revision;
- at most one unresolved `pending_confirmation` revision may exist for a candle lineage at a time; processing of another distinct candidate for that candle is serialized until the pending revision resolves;
- a same-value observation matching the pending candidate is idempotent and does not allocate another sequence;
- after interruption/restart, an unresolved pending revision remains pending and PIT-ineligible until confirmation is retried/resolved; it is never silently treated as accepted or quarantined.

## Decision update

D-020 now explicitly includes the `pending_confirmation` state, its PIT ineligibility and serialized per-candle transition rule.

## Tests added to the contract

Data revision tests must additionally verify:

- a changed observation is persisted as `pending_confirmation` before confirmation returns;
- pending revision has `observed_at`, no `accepted_at`, and is never PIT-eligible;
- successful confirmation transitions the same revision/sequence to `accepted_current`;
- failed/unavailable confirmation transitions the same revision/sequence to `quarantined`;
- same-value re-observation of a pending candidate is idempotent;
- a candle cannot have two unresolved pending candidates and confirmation outcomes cannot be applied out of order;
- restart/recovery preserves pending state and does not imply acceptance.

## Gate — satisfied

- Final independent audit A: `P0 — VALIDATION READY`.
- Final independent audit B: `P0 — VALIDATION READY`.
- User approval: D-001 through D-020 explicitly approved in block on 2026-09-06.

Result: `P0 — VALIDATED`. P1 may begin, but validated P0 decisions are append-only historical contracts and must not be silently rewritten.
