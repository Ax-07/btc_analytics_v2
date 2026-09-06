# 01 — Architecture

## Vue conceptuelle

```text
Exchange
   |
   v
Market Data Access
   |
   v
Normalization + Validation
   |
   v
Canonical Market Data
   |
   +-------------------+
   |                   |
   v                   v
Causal Feature      Research Dataset
Engine              (Parquet/DuckDB)
   |
   v
Market Structure
   |
   v
Event Engine
   |
   v
Context Engine
   |
   v
Occurrence Store
   |
   +------------------------+
   |                        |
   v                        v
Product API            Outcome Engine
                            |
                            v
                       Experiment Engine
```

## Frontières obligatoires

- `market_data/` : accès exchange, pagination, normalisation, validation, stockage ; aucune logique analytique.
- `features/` : calculs strictement causaux.
- `structure/` : pivots, swings, HH/HL/LH/LL, retracements, métriques de segments.
- `events/` : événements timestampés construits à partir d'informations causales.
- `contexts/` : état de marché à T.
- `occurrences/` : instances figées d'une définition satisfaite.
- `outcomes/` : seule couche analytique autorisée à lire après T.
- `experiments/` : comparaisons de définitions, paramètres, timeframes, périodes.
- `research/` : zone non canonique ; look-ahead/offline autorisé s'il est déclaré.

## Backend / frontend

FastAPI expose les contrats internes. Le frontend ne dépend jamais directement de CCXT, TA-Lib, DuckDB, VectorBT ou SciPy et ne recalcule pas les features métier.

## Structure cible

```text
btc_analytics_v2/
├── backend/
│   ├── src/btc_analytics/
│   │   ├── api/
│   │   ├── domain/
│   │   ├── market_data/
│   │   ├── features/
│   │   ├── structure/
│   │   ├── events/
│   │   ├── contexts/
│   │   ├── occurrences/
│   │   ├── outcomes/
│   │   ├── experiments/
│   │   ├── storage/
│   │   └── observability/
│   └── tests/
├── frontend/
├── research/
├── docs/
├── infra/
└── pyproject.toml
```
