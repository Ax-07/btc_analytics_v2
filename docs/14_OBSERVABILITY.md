# 14 — Observabilité

## Minimum

Logs structurés avec composant, opération, market, timeframe, run_id, durée, nombres de lignes et contexte d'erreur.

## Métriques de qualité des données

bougies récupérées, doublons rejetés, gaps détectés, bougies invalides, dernière bougie clôturée, latence d'ingestion.

## Métriques analytiques

lignes de features, occurrences, durée des expériences, combinaisons de paramètres, échecs.

## Reproductibilité

Chaque batch significatif doit être relié à la version du code, la configuration, le dataset et les timestamps.

Commencer simplement ; ajouter OpenTelemetry/Prometheus uniquement en réponse à un besoin réel.
