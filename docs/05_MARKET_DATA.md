# 05 — Market Data

## Goal

Provide reliable exchange-independent closed candles for analytical use.

## Access architecture

```text
Exchange -> CCXT Adapter -> Provider DTO -> Normalizer -> Validator -> Canonical Candle
                                                     -> PostgreSQL current canonical store
                                                     -> Parquet immutable analytical snapshots
```

## Initial provider/market

- access library: CCXT;
- exchange: Binance Spot;
- provider symbol: `BTC/USDC`;
- internal canonical market identity is independent of CCXT notation.

The domain never imports CCXT types.

## Canonical candle semantics

- interval: `[open_time, end_time)`;
- UTC;
- P1 stores/uses closed candles for analytics;
- `available_at = end_time` describes historical market-time bar availability;
- provider-specific raw close timestamps may be retained as provenance only.

### Volume

Canonical `base_volume` is volume in the base asset (BTC for BTC/USDC).

If retained, quote activity is named `quote_volume`; trade count is `trade_count`. No ambiguous generic `volume` field is used in canonical domain contracts.

## Initial native timeframes

- `1h`
- `4h`
- `1d`

P1 fetches each timeframe natively from the provider. No canonical resampling is performed in P1.

Expected UTC alignment is validated.

If an exchange/provider does not support a required native timeframe, that market/timeframe is unsupported until a separate resampling contract is explicitly added.

## Validation

- timezone/interval alignment;
- OHLC invariants;
- non-negative volumes/counts;
- uniqueness;
- closed status/eligibility;
- monotonic ordering;
- duplicate detection;
- gap detection.

## Gap policy

A gap is never interpolated silently.

Canonical analytics treat gaps as hard continuity boundaries:

- rolling feature warm-up restarts after a gap when continuity is required;
- structural algorithms do not connect points across a gap by default;
- events/contexts depending on continuous history are unavailable until their requirements are satisfied again;
- an outcome horizon crossing a gap is `incomplete_gap`;
- ExperimentRun reports exclusions/incomplete counts.

## PostgreSQL authority

PostgreSQL is the **current canonical product store**.

Repeated observations that normalize to the same values are idempotent.

### Changed closed candle: revision acceptance policy v1

A different re-observation of an already stored closed candle never overwrites current state directly.

The deterministic flow is:

1. normalize the new observation;
2. validate all canonical invariants;
3. compare it with the current accepted revision;
4. if values are identical, do nothing except optional observation metadata;
5. if values differ, create a revision candidate and record `observed_at`;
6. confirm the candidate against the configured native authoritative endpoint for the **same venue and market**;
7. promote the candidate only if the normalized native confirmation agrees on canonical OHLC and `base_volume`;
8. when confirmed, mark the old revision `accepted_superseded`, the new revision `accepted_current`, increment `revision_seq`, and write the before/after audit entry;
9. if confirmation disagrees, is unavailable, or validation fails, mark the candidate `quarantined` and leave PostgreSQL current canonical values unchanged.

For the initial Binance provider, the confirmation source is Binance native klines.

No observation from another exchange/venue can automatically replace the canonical Binance candle.

### Revision temporal semantics

Two notions must not be conflated:

- `available_at = end_time`: market-time availability of the completed candle in the reconstructed closed-bar model;
- `CandleRevision.observed_at`: when BTC Analytics actually observed a particular revision.

A correction discovered later is never claimed to have been **system-observed** at the original `end_time`.

## Dataset knowledge modes

### `reconstructed_latest`

Default mode for historical analytical research.

The snapshot uses the accepted current revision for each candle at snapshot creation.

Causal feature/event sequencing is anchored to candle `end_time`, but the run must be described as a **reconstructed-latest historical analysis**. It must not claim that later provider corrections were actually known to BTC Analytics or a market participant at the original historical T.

This mode is appropriate for “analyse the best currently available reconstruction of history”.

### `observed_point_in_time`

Strict replay mode.

A candle revision may influence an anchor T only if that revision was actually observed no later than T under the stored revision history.

This mode is only valid for periods with sufficient continuous observation/revision provenance. Historical backfill predating BTC Analytics observation coverage cannot be silently treated as point-in-time observed history.

P0 defines the semantics; P1 does not need to implement a full live point-in-time replay engine unless explicitly scheduled.

## Parquet snapshots

Parquet snapshots are immutable derived datasets for reproducible analytics/research, not a second mutable authority.

Each DatasetSnapshot freezes:

- candle identities;
- exact accepted revision identifiers;
- knowledge mode;
- gaps;
- logical manifest/content hashes.

A later PostgreSQL candle correction never modifies an existing snapshot.

## Idempotence

Repeated fetches that normalize to the same canonical candle create no new semantic state.

## Cross-check P1

A bounded fixture/range compares CCXT Binance OHLCV with Binance-native kline data for timestamp/OHLC/base volume after normalization.

The same native path is used as confirmation only when a changed historical observation requires revision validation.

## Real-time

Out of P1. WebSocket/open-candle handling requires a later explicit intrabar/live contract.
