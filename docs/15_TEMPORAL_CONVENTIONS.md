# 15 — Temporal Conventions

This document is the canonical temporal coordinate contract for P0.

## Candle coordinates

For timeframe duration `Δ`:

```text
open_time = t
end_time  = t + Δ
interval  = [t, t + Δ)
available_at = end_time
```

All canonical timestamps are UTC.

Provider-specific close timestamps that use inclusive final milliseconds are normalized and never redefine the canonical interval.

## Closed-bar analytical model

Initial V2 analytics use only complete candles. `available_at=end_time` expresses market-time historical availability of the complete OHLCV bar.

`ingested_at` records when BTC Analytics observed/stored a version and is not used to shift historical analytical anchors.

A future real-time/intrabar subsystem may additionally model system-observation latency, but must not change P0 historical semantics retroactively.

## Derived artifact timing

### Feature on candle C

- `event_time = C.end_time` unless the definition documents a physical-time alternative;
- `known_at = C.end_time` if all required inputs are available by then.

### Confirmed structural point

A pivot may have:

```text
physical_time = candle_100.end_time
known_at      = candle_103.end_time
```

The point belongs physically to 100 but is not eligible for occurrence selection before 103.

### Multi-bar event

The definition must state:

- physical/event attribution rule;
- last required evidence candle;
- `known_at = end_time` of that last required candle.

## Joins

A causal join at anchor T may include only records with `known_at <= T`.

Joining a structural point by physical time while ignoring its later `known_at` is a causality violation.


## Candle revisions and historical claims

`available_at=end_time` belongs to the reconstructed closed-bar market-time model.

Every canonical candle has a revision lineage. Each revision records `observed_at`; every revision that becomes accepted additionally records `accepted_at`.

For accepted revisions:

```text
observed_at <= accepted_at
```

Therefore:

- `reconstructed_latest` analyses may use the latest accepted revision while anchoring analytical bar sequencing at `end_time`, but must not claim that a later correction was actually known or accepted at historical T;
- `observed_point_in_time` analyses may use only an accepted revision whose `accepted_at <= T`;
- `observed_at <= T` alone is insufficient when the candidate had not yet been accepted by T;
- for a given candle, PIT selects the accepted revision with the greatest `accepted_at <= T`;
- quarantined revisions have no `accepted_at` and are never PIT-eligible.

Example: a correction observed at 10:00 and accepted at 10:05 cannot influence replay at 10:02; it becomes eligible at 10:05.

Historical periods without sufficient observation **and acceptance** provenance cannot be labeled `observed_point_in_time`. Historical backfills created later are analyzed with `reconstructed_latest` unless genuine point-in-time revision provenance exists.
