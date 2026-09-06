# 07 — Experiment Engine

## Goal

Compare analytical hypotheses using batch/vectorized parameter grids, without trading or portfolio simulation.

## Required frozen inputs

Every ExperimentRun records:

- DatasetSnapshot, including its `knowledge_mode` and exact CandleRevision manifest;
- historical range;
- timeframes;
- definition keys/versions;
- normalized parameter grid;
- OutcomeDefinitions;
- BaselineDefinition;
- split/walk-forward policy;
- software/config revision.

## Parameter dimensions

Examples: timeframe, feature parameters, structure parameters, context definition, outcome horizon.

## Outcome metrics

Initial standard metrics:

- forward close return;
- MFE;
- MAE;
- future volatility when its metric definition is versioned.

Exact temporal semantics live in `16_OUTCOME_BASELINE_CONVENTIONS.md`.

## Baseline

No experiment may rely on an implicit phrase such as “relevant baseline”. A BaselineDefinition is mandatory for comparative claims.

Default candidate baseline: all eligible anchor candles in the same market/timeframe/snapshot/date range, applying the same data-quality, gap and outcome-completeness rules as the conditional sample.

Alternative baselines must be explicit and versioned.

## Walk-forward

Calibration and evaluation periods are temporally separated. The run stores split boundaries and whether parameters were selected using earlier folds.

## Anti-overfitting

Require where relevant:

- out-of-sample evaluation;
- temporal stability;
- multi-timeframe robustness;
- parameter sensitivity;
- sample-size reporting.


## Identity reproducibility

Normalized experiment parameters use the canonical parameter representation defined in `03_DOMAIN_MODEL.md`:

- schema normalization;
- RFC 8785 JCS serialization;
- SHA-256 lowercase hex fingerprints.

ExperimentRun must record the exact parameter fingerprints used.

## Data revision semantics

An ExperimentRun never follows mutable PostgreSQL current state after launch.

It evaluates the immutable DatasetSnapshot it references.

If a later provider correction changes current canonical PostgreSQL values, a new snapshot/run is required. Results from different snapshots remain comparable through explicit snapshot identities and revision provenance.
