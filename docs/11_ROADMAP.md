# 11 — Roadmap

## P0 — Foundation

Charter, architecture, stack, domain identity/provenance, temporal conventions, causal contract, Market Data semantics, outcome/baseline conventions, dependency assessment, quality policy and decision log.

## P1 — Market Data

Repo bootstrap, PostgreSQL, CCXT adapter, canonical closed Candle, native 1h/4h/1d ingestion, validation, gaps, revision audit, idempotence, CCXT-vs-native fixture.

## P2 — Analytics Core

Time alignment, feature interface/registry, versioning/fingerprints, Polars/NumPy conventions, materialization policy.

## P3 — Technical Features

Returns/range, ATR, RSI, volatility, momentum, volume and selected standard features with causal/golden tests.

## P4 — Market Structure

Causal extrema, prominence, pivots/swings, HH/HL/LH/LL, amplitude, duration, slope, retracement, compression/expansion.

## P5 — Events, Occurrences & Basic Contexts

Event definitions, occurrence identity, technical/structural events, validated candlestick shortlist, basic causal ContextDefinition/ContextSnapshot and context-filtered occurrences.

## P6 — Forward Outcomes

Versioned OutcomeDefinitions, forward returns, MFE, MAE, future-volatility definition, completeness/gap states and baseline populations.

## P7 — Experiment Engine

DatasetSnapshots, parameter grids, multi-timeframe batch evaluation, BaselineDefinition, walk-forward and robustness reports.

## P8 — Advanced Contexts & Regimes

Richer state combinations, regime research, offline change-point exploration and causal promotion rules.

## P9 — Analytical Workbench

API + chart + structure/event/context inspection + occurrence/outcome/experiment comparison.

## P10 — Optional Analytics

Chart patterns or other interpretive models only if incremental value is demonstrated. P10 may remain empty.
