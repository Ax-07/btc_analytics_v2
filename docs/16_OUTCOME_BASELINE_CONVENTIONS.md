# 16 — Outcome & Baseline Conventions

## Anchor

Initial canonical occurrences are closed-candle anchored.

`Occurrence.known_at` corresponds to the `end_time` of an anchor candle A.

Default reference price:

```text
P0 = close(A)
```

The anchor candle itself is excluded from future excursion windows because its high/low occurred partly or entirely before the occurrence became known.

## Horizon H

Horizon `H` consists of the next H complete expected candles after A:

```text
A+1, A+2, ..., A+H
```

## Forward close return

```text
return_H = close(A+H) / P0 - 1
```

## MFE

```text
MFE_H = max(0, max(high(A+i) / P0 - 1)), i=1..H
```

Canonical MFE is therefore non-negative. If price never trades above P0 during the horizon, MFE is `0`.

## MAE

```text
MAE_H = min(0, min(low(A+i) / P0 - 1)), i=1..H
```

Canonical MAE is therefore non-positive. If price never trades below P0 during the horizon, MAE is `0`.

## Missing future

If the expected sequence A+1..A+H contains:

- a data gap -> `incomplete_gap`;
- end of available dataset -> `incomplete_end_of_dataset`.

No interpolation or shortening is allowed for a result labeled complete.

## Metric definitions

Future volatility and any additional metric require their own versioned OutcomeDefinition before canonical use.

## BaselineDefinition

Every comparative experiment stores an explicit baseline.

Default candidate baseline population:

- same DatasetSnapshot;
- same market/timeframe/date range;
- all eligible closed anchor candles;
- same gap/completeness rules;
- same OutcomeDefinitions;
- no condition/event filter unless explicitly declared.

A context-matched or regime-matched baseline is allowed only as a separate versioned BaselineDefinition.


## Dataset revision consistency

Conditional samples and their BaselineDefinition must use the same DatasetSnapshot and therefore the same:

- knowledge mode;
- candle revision set;
- gap state;
- temporal coverage.

A comparison between different snapshot revisions is a separate experiment/comparison dimension and must never be hidden inside a baseline.
