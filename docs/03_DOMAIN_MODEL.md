# 03 — Domain Model

## Shared identity primitives

### Canonical parameter representation

Every canonical analytical definition owns a parameter schema.

Before identity calculation:

- all schema defaults are materialized explicitly;
- object member names and enum/string values use their canonical schema spelling;
- unordered collections are sorted according to their definition-specific schema rule before serialization;
- timestamps, when parameters, use integer Unix epoch milliseconds UTC;
- non-finite numbers (`NaN`, `+Inf`, `-Inf`) are forbidden;
- exact decimal semantics must be represented as normalized decimal strings, not binary floating-point values.

Canonical parameter bytes are the UTF-8 bytes of the parameter object serialized with **RFC 8785 JSON Canonicalization Scheme (JCS)**.

Normalized decimal strings use:

- no leading `+`;
- `-0` normalized to `0`;
- no unnecessary leading integer zeros;
- no trailing fractional zeros;
- no decimal point when the fractional part is empty;
- base-10 plain notation unless a definition explicitly versions another representation.

Examples:

```text
"001.2300" -> invalid input form; normalized semantic value -> "1.23"
"-0.000"   -> "0"
"2.500"    -> "2.5"
```

### DefinitionIdentity

Every canonical analytical definition has:

- `definition_key`: stable namespaced key;
- `definition_version`: changes whenever semantics change;
- `parameters`: normalized canonical parameter object;
- `parameter_fingerprint`.

`parameter_fingerprint` is exactly:

```text
"sha256:" + lowercase_hex(SHA-256(JCS(parameters)))
```

The hash covers the normalized parameters only. Definition key/version remain explicit identity fields.

### Provenance

Canonical derived artifacts must be traceable to:

- market;
- timeframe;
- source data identity or DatasetSnapshot when applicable;
- definition key/version;
- parameter fingerprint;
- computation software revision/run when material.

## Market

- venue
- base_asset
- quote_asset
- market_type
- canonical_symbol

`canonical_symbol` is a BTC Analytics domain identifier and is independent from CCXT/provider notation.

## Candle

Canonical closed OHLCV bar:

- market
- timeframe
- `open_time`
- `end_time`
- open
- high
- low
- close
- `base_volume`
- optional `quote_volume`
- optional `trade_count`
- source
- source_symbol
- `available_at`
- `ingested_at`
- current accepted revision metadata

Identity:

```text
(market, timeframe, open_time)
```

The canonical interval is `[open_time, end_time)` and `available_at = end_time` in the initial reconstructed closed-candle analytical model.

## CandleRevision

Every canonical candle has an explicit append-only revision lineage, including its first accepted observation and every later distinct observation.

Minimum fields:

- candle identity `(market, timeframe, open_time)`;
- monotonically increasing local `revision_seq`;
- normalized OHLCV values;
- `observed_at`;
- optional `accepted_at`;
- `revision_status`: `pending_confirmation`, `accepted_current`, `accepted_superseded`, `quarantined`;
- primary provider provenance;
- confirmation provenance when required;
- before/after logical value fingerprints;
- reason/audit metadata.

The stable exact local revision reference is:

```text
(market, timeframe, open_time, revision_seq)
```

### Initial accepted revision

The first valid observation of a previously unknown closed candle creates the first revision immediately:

- `revision_seq = 1`;
- `observed_at` = earliest time BTC Analytics observed that normalized candle;
- `accepted_at` = instant canonical validation succeeds;
- `revision_status = accepted_current`.

Initial acceptance does not require a per-candle same-venue native confirmation. Provider-path correctness is validated separately by the bounded P1 CCXT-vs-native fixture.

### Later distinct observations

Every later observation that differs from the current accepted logical values creates a new revision candidate and receives the next monotonically increasing `revision_seq` **at candidate creation time**. Sequence numbers are never reused.

The newly created candidate is persisted with `revision_status = pending_confirmation`, has `observed_at`, and has no `accepted_at`. A `pending_confirmation` revision is never PIT-eligible.

For a given candle lineage, at most one unresolved `pending_confirmation` revision may exist at a time. Processing of another distinct candidate for that candle is serialized until the pending revision resolves. A same-value re-observation matching the pending candidate is idempotent and creates no additional revision. This prevents confirmation outcomes from being applied out of revision order.

If native confirmation succeeds, the **same** pending revision transitions to `accepted_current`: promotion never renumbers it, records `accepted_at`, and marks the previous current accepted revision `accepted_superseded`. If confirmation disagrees, is unavailable, or validation fails, the same pending revision transitions to `quarantined`, retains its allocated `revision_seq`, and keeps `accepted_at` absent.

An interruption/restart does not infer a terminal status: an unresolved pending revision remains `pending_confirmation`, remains PIT-ineligible, and must be retried/reconciled before another distinct candidate for the same candle is processed.

A same-value re-observation of the current accepted revision is idempotent and creates no new semantic revision when no conflicting pending candidate exists.

A later revision never mutates an immutable DatasetSnapshot.

`observed_at` is the earliest time BTC Analytics observed that revision. A correction observed later must never be represented as having been actually observed by the system at the historical candle `end_time`.

`accepted_at` is the instant at which required validation/confirmation succeeds and the revision becomes accepted canonical state. It is present only for revisions that have been accepted at least once (`accepted_current` or `accepted_superseded`). A quarantined revision has no `accepted_at`.

For every accepted revision:

```text
observed_at <= accepted_at
```

`accepted_at` is temporal provenance. It does not participate in Candle identity, DefinitionIdentity, `occurrence_key`, or any other semantic identity unless a future versioned contract explicitly says otherwise.

## FeatureDefinition / FeatureValue

A FeatureValue includes definition identity, market/timeframe, `event_time`, `known_at`, values and provenance.

## StructuralPoint

- `physical_time`
- `known_at`
- price
- kind
- definition identity
- metrics
- provenance

`physical_time < known_at` is valid for confirmed historical structure.

## StructuralSegment

Links structural points and records direction, return, ATR-normalized amplitude, duration, slope, velocity and retracement relationships.

Its `known_at` cannot precede the latest required input `known_at`.

## EventDefinition / Event

An Event is a versioned causal occurrence with:

- definition identity;
- `event_time`;
- `known_at`;
- evidence/values;
- deterministic `instance_discriminator`;
- provenance.

For a given DefinitionIdentity, market, timeframe and anchor candle, the default rule is at most one canonical event with `instance_discriminator = "0"`.

If a definition can emit multiple distinct canonical events for the same anchor, its versioned schema must define a deterministic non-empty `instance_discriminator`.

## ContextDefinition / ContextSnapshot

A ContextSnapshot is a causal state evaluated at an anchor candle using only artifacts whose `known_at <= anchor.end_time`.

## Occurrence

The central historical analysis unit.

Minimum fields:

- deterministic `occurrence_key`;
- definition identity;
- market/timeframe;
- `event_time` when physically meaningful;
- `known_at`;
- anchor candle identity;
- `instance_discriminator`;
- context reference/snapshot when used;
- provenance/input references.

### Occurrence key payload

The exact v1 identity payload is:

```json
{
  "schema": "occurrence-key.v1",
  "definition_key": "<canonical definition_key>",
  "definition_version": "<canonical definition_version>",
  "parameter_fingerprint": "sha256:<hex>",
  "market": "<canonical market symbol>",
  "timeframe": "<canonical timeframe>",
  "anchor_open_time_ms": 0,
  "event_time_ms": 0,
  "instance_discriminator": "0"
}
```

Rules:

- timestamps are integer Unix epoch milliseconds UTC;
- `event_time_ms` is the canonical physical/event attribution time; if the definition has no distinct physical attribution, it equals the anchor candle `end_time`;
- `instance_discriminator` defaults to `"0"`;
- context is **not** part of occurrence identity; contexts are attached analytical state and may be used for slicing without duplicating the occurrence;
- DatasetSnapshot is provenance, not occurrence identity, so the same semantic occurrence can be compared across snapshots/revisions.

`occurrence_key` is exactly:

```text
"sha256:" + lowercase_hex(SHA-256(JCS(occurrence_key_payload)))
```

Database insertion order, surrogate IDs and computation run IDs never participate in the key.

## OutcomeDefinition

Defines:

- metric key/version;
- horizon in bars;
- reference-price convention;
- future-window convention;
- gap policy;
- metric-specific parameters.

OutcomeDefinition parameter identity follows the same JCS/SHA-256 rule.

## Outcome

Attached to an Occurrence and OutcomeDefinition.

Outcome never changes the original occurrence and may be `complete`, `incomplete_gap` or `incomplete_end_of_dataset`.

## BaselineDefinition

Every experiment comparing conditional distributions must explicitly define its baseline population:

- market/timeframe;
- historical range;
- eligible anchor policy;
- context filter if any;
- same outcome/gap conventions;
- sampling policy/version.

BaselineDefinition identity follows the same DefinitionIdentity parameter canonicalization rules.

## DatasetSnapshot

Immutable experiment input identity containing at minimum:

- `snapshot_id`;
- source market/timeframes;
- temporal coverage;
- creation time;
- `knowledge_mode`;
- manifest/content hashes;
- gap summary;
- exact accepted CandleRevision references included in the snapshot.

Initial `knowledge_mode` values:

- `reconstructed_latest`;
- `observed_point_in_time` when sufficient observation/revision history exists.

The snapshot identity payload excludes creation time and includes:

- snapshot schema/version;
- market/timeframes;
- temporal coverage;
- knowledge mode;
- logical manifest hash of included candle identities + accepted revision identifiers.

`snapshot_id` is:

```text
"sha256:" + lowercase_hex(SHA-256(JCS(snapshot_identity_payload)))
```

Parquet is the initial physical format for immutable analytical snapshots. Physical Parquet byte layout is not used as the sole logical identity because different writers may encode equivalent logical data differently.

## ExperimentDefinition / ExperimentRun

A run freezes:

- DatasetSnapshot;
- analytical definition versions;
- parameter grid;
- OutcomeDefinitions;
- BaselineDefinition;
- split policy;
- software/config revision.
