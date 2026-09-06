# 02 — Tech Stack

## Policy

External libraries provide generic primitives. BTC Analytics owns domain semantics, causal contracts, versioning and reproducibility.

Exact package versions are pinned in lockfiles at repository bootstrap after compatibility checks.

## ADOPT — product/runtime

- Python
- NumPy
- Polars
- SciPy
- CCXT behind `MarketDataProvider`
- TA-Lib behind internal adapters for selected validated functions
- PostgreSQL
- FastAPI
- Pydantic
- Alembic

## ADOPT — development

- uv
- pytest
- Ruff
- **Pyright**
- GitHub Actions
- Docker Compose

## ADOPT — frontend

- Next.js
- TypeScript
- pnpm
- Lightweight Charts
- shadcn/ui

## ADOPT — research/data snapshots

- Parquet
- DuckDB

## RESEARCH / REFERENCE

- VectorBT: vectorized experimentation concepts, grids and walk-forward; not product portfolio engine.
- ruptures: offline change-point research only until a causal formulation is validated.
- statsmodels: only when a concrete statistical need exists.

## REJECT as product dependencies

- PatternPy
- TradingPatternScanner

## TA-Lib scoped decision

TA-Lib may execute selected standard indicators and candlestick functions only when each selected function has:

- documented inputs/lookback;
- causal verification under BTC Analytics closed-candle semantics;
- golden tests;
- a BTC Analytics definition/version wrapper.

TA-Lib can additionally serve as a reference oracle for primitives implemented internally.

## Performance rule

1. correct algorithm;
2. vectorized NumPy/Polars implementation;
3. profiling;
4. Numba/Rust only for demonstrated bottlenecks.
