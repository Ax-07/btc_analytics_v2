# 04 — Causality Contract

## Absolute rule

If BTC Analytics says an artifact is known at T, no information after T may have contributed to it.

## Initial cadence

P0–P8 canonical analytics operate on **closed candles**.

Derived artifacts therefore become known on canonical candle boundaries unless a future milestone defines an explicit intrabar contract.

## Time coordinates

- candle `open_time`: inclusive start;
- candle `end_time`: exclusive end;
- candle `available_at`: `end_time` in historical closed-bar semantics;
- derived `event_time`/`physical_time`: where the phenomenon belongs;
- derived `known_at`: earliest canonical time at which all required evidence is available;
- `ingested_at`: system observation time, not a substitute for analytical `known_at`.

## Layer rules

### market_data

Open/provider-in-progress bars are not eligible for canonical analytical computation.

### features

Strictly causal. Forbidden without an explicit delayed `known_at` formulation:

- `shift(-1)`;
- centered windows;
- global-fit smoothing;
- full-series parameter fitting;
- future-confirmed extrema assigned retroactively to physical time.

### structure

May refer to a past physical point, but confirmation latency must be represented by `known_at`.

### events / contexts / occurrences

`known_at` equals or exceeds every required input's `known_at`.

### outcomes

Future use is allowed only after occurrence selection is frozen.

### research

Look-ahead/offline methods are permitted only when explicitly labeled research and cannot be promoted without a causal production contract.

## Mandatory prefix-invariance testing

Applies to every artifact declared known at T:

- FeatureValue;
- StructuralPoint;
- StructuralSegment;
- Event;
- ContextSnapshot;
- derived Occurrence.

Test protocol:

1. compute on the full series;
2. compute on historical prefixes ending at multiple T;
3. compare artifacts whose `known_at <= T`;
4. adding future bars must not alter their canonical identity/value/state.

Any legitimate later revision must be modeled as a new explicitly timestamped state/version, not silent retroactive mutation.
