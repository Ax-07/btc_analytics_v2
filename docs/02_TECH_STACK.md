# 02 — Stack technique

## Politique

Les bibliothèques externes fournissent des primitives génériques. BTC Analytics possède la sémantique du domaine, les contrats causaux, le versionnement et la reproductibilité.

Les versions exactes des paquets sont figées dans les fichiers de verrouillage lors de l'amorçage du dépôt, après vérification de compatibilité.

## ADOPT — produit/exécution

- Python
- NumPy
- Polars
- SciPy
- CCXT derrière `MarketDataProvider`
- TA-Lib derrière des adaptateurs internes pour les fonctions sélectionnées et validées
- PostgreSQL
- FastAPI
- Pydantic
- Alembic

## ADOPT — développement

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

## ADOPT — recherche/snapshots de données

- Parquet
- DuckDB

## RESEARCH / REFERENCE

- VectorBT : concepts d'expérimentation vectorisée, grilles et walk-forward ; pas de moteur produit de portefeuille.
- ruptures : recherche hors ligne de points de rupture uniquement jusqu'à validation d'une formulation causale.
- statsmodels : uniquement lorsqu'un besoin statistique concret existe.

## REJECT comme dépendances produit

- PatternPy
- TradingPatternScanner

## Décision TA-Lib à périmètre limité

TA-Lib peut exécuter certains indicateurs standards et certaines fonctions de chandeliers uniquement lorsque chaque fonction sélectionnée possède :

- des entrées et une période rétrospective (`lookback`) documentées ;
- une vérification causale sous la sémantique de bougies clôturées (`closed-candle`) de BTC Analytics ;
- des tests de référence (`golden tests`) ;
- un adaptateur BTC Analytics (`wrapper`) avec définition/version.

TA-Lib peut également servir d'oracle de référence pour des primitives implémentées en interne.

## Règle de performance

1. algorithme correct ;
2. implémentation vectorisée NumPy/Polars ;
3. profilage ;
4. Numba/Rust uniquement pour des goulots d'étranglement démontrés.
