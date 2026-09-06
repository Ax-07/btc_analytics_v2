# 17 — Dependency Assessment

Verification date: 2026-09-06. Exact versions are pinned only at repository bootstrap.

## CCXT — ADOPT behind adapter

- Function: unified exchange/market-data access.
- Method: exchange-specific implementations exposed through a unified API including OHLCV retrieval.
- Causality: neutral; BTC Analytics must filter to closed bars and define its own temporal semantics.
- Validation: requires P1 cross-check against Binance-native klines.
- Maintenance: active project with Binance support and current unified OHLCV documentation.
- License: MIT.
- Coupling: medium if leaked; low when isolated behind `MarketDataProvider`.
- Decision: ADOPT as access layer, not domain model.

## Polars — ADOPT

- Function: dataframe/transformation engine.
- Method: Rust columnar engine, lazy query optimization, parallel execution and streaming.
- Causality: neutral; expressions must still obey BTC Analytics causal windows.
- Validation: strong project documentation and active development.
- Performance fit: excellent candidate for batch columnar analytics.
- License: MIT.
- Coupling: keep Polars objects inside computation/storage boundaries, not API/domain contracts.

## SciPy — ADOPT

- Function: scientific algorithms, statistics and signal primitives.
- Method: mature numerical/scientific implementations; `signal` can supply generic peak/prominence primitives.
- Causality: function-specific. Some filters/smoothers can be non-causal; each adopted use must be reviewed.
- Validation: mature project with extensive releases/tests.
- License: BSD-3-Clause.
- Coupling: low behind BTC Analytics feature/structure definitions.

## TA-Lib Python — scoped ADOPT + REFERENCE

- Function: standard technical indicators and candlestick pattern functions.
- Method: Python/Cython wrapper over TA-Lib core.
- Causality: function-specific; adoption requires per-function lookback/closed-bar validation.
- Validation: project classifies package as production/stable; wrappers/types are available for modern Python releases.
- Maintenance: active upstream in 2026.
- License: Python wrapper BSD-2-Clause; core uses BSD-family licensing.
- Coupling: medium if function names become domain contracts; mitigate with internal definition/adapters.
- Decision: selected validated functions ADOPT; oracle/reference use remains REFERENCE.

## DuckDB — ADOPT for research

- Function: local analytical SQL over Parquet/datasets.
- Method: in-process analytical database with direct Parquet scanning and pushdown.
- Causality: neutral; used after dataset construction.
- Validation: project documents extensive CI/testing, including millions of queries.
- Maintenance: active; project remains open source under independent foundation governance.
- License: MIT.
- Coupling: low because product API does not depend on DuckDB.

## FastAPI / Pydantic — ADOPT API boundary

- Function: typed HTTP API and schemas.
- Causality: neutral.
- License: FastAPI MIT; package versions/compatibility pinned at bootstrap.
- Coupling: intentionally limited to API/application layer; domain must remain framework-independent.

## uv — ADOPT development tooling

- Function: Python package/project/environment management.
- Method: Rust implementation and lock/project workflow.
- Causality/runtime: none.
- Maintenance: active and production-oriented.
- License: MIT OR Apache-2.0.
- Coupling: development only.

## Ruff — ADOPT development tooling

- Function: Python linting and formatting.
- Method: Rust implementation.
- Causality/runtime: none.
- License: MIT.
- Coupling: development only.

## Pyright — ADOPT development tooling

- Function: static Python type checking.
- Method: standards-based high-performance static checker.
- Causality/runtime: none.
- Maintenance: active project.
- License: MIT.
- Coupling: development only.

## pytest — ADOPT development tooling

- Function: test runner/framework.
- Causality/runtime: none in product; used to enforce causal invariants and integration contracts.
- License: MIT.
- Coupling: tests only.

## VectorBT — RESEARCH / REFERENCE

Use conceptual inspiration for vectorized parameter grids, broadcasting and walk-forward experimentation. Do not make product semantics or portfolio/trading abstractions depend on it.

## ruptures — RESEARCH

Offline change-point algorithms are research-only by default. Any production promotion requires a separately demonstrated causal formulation.

## PatternPy / TradingPatternScanner — REJECT product

Retain only as comparative/research references. They are not foundations of V2 market structure or chart-pattern semantics.
