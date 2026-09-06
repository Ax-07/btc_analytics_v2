# 08 — Research Catalog

This catalog is a decision index. Detailed evidence for structural dependencies is in `17_DEPENDENCY_ASSESSMENT.md`.

| Tool | Candidate status | Scope |
|---|---|---|
| NumPy | ADOPT | numerical arrays |
| Polars | ADOPT | dataframe/query engine |
| SciPy | ADOPT | scientific/signal primitives |
| CCXT | ADOPT | exchange access behind adapter |
| TA-Lib selected functions | ADOPT | validated standard indicators/candlesticks behind adapter |
| TA-Lib | REFERENCE | oracle/comparison where useful |
| PostgreSQL | ADOPT | current canonical product store |
| Parquet | ADOPT | immutable research snapshots |
| DuckDB | ADOPT research | analytical SQL over snapshots |
| FastAPI/Pydantic | ADOPT | API/contracts |
| uv | ADOPT dev | package/project management |
| Ruff | ADOPT dev | lint/format |
| Pyright | ADOPT dev | static typing |
| pytest | ADOPT dev | tests |
| VectorBT | RESEARCH/REFERENCE | vectorized experiment concepts |
| ruptures | RESEARCH | offline change-point research |
| statsmodels | RESEARCH / adopt-on-need | statistical methods |
| PatternPy | REJECT product | comparison only |
| TradingPatternScanner | REJECT product | comparison/research only |

## Mandatory evaluation dimensions

Function, method, causal implications, validation/testing, maintenance, performance fit, license, coupling, final scope.

A tool may have different statuses for different roles, but those roles must be explicit (e.g. TA-Lib execution vs oracle).
