# 14 — Observability

## Minimum

Logs structurés avec component, operation, market, timeframe, run_id, duration, row counts et contexte d'erreur.

## Data quality metrics

candles fetched, duplicates rejected, gaps detected, invalid candles, latest closed candle, ingestion lag.

## Analytics metrics

feature rows, occurrences, experiment duration, parameter combinations, failures.

## Reproductibilité

Chaque batch significatif doit être relié à code version, config, dataset et timestamps.

Commencer simple ; ajouter OpenTelemetry/Prometheus uniquement en réponse à un besoin réel.
