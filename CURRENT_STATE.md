# État courant

## Projet

BTC Analytics V2

## Phase

P1 — Données de marché / P1D — Schéma PostgreSQL canonique

## Statut

`P1D — VALIDATION READY / VALIDATION UTILISATEUR EN ATTENTE`

P0 — Fondation reste validé et figé au jalon `p0-foundation-v7`. P1A — Amorçage du backend reste validé et figé au jalon `p1a-backend-bootstrap`. P1B — Domaine des données de marché reste validé et figé au jalon `p1b-market-data-domain`. P1C — `MarketDataProvider` + adaptateur CCXT Binance reste validé et figé au jalon `p1c-ccxt-provider`.

P1D matérialise les contrats P0/P1B dans PostgreSQL via des métadonnées SQLAlchemy et la première migration produit Alembic. Le schéma couvre `markets`, `candles` et `candle_revisions`, les identités canoniques, les coordonnées temporelles, les invariants OHLCV et les contraintes locales de statut/référence nécessaires à la future machine P1E.

Les valeurs OHLCV courantes ne sont pas dupliquées dans `candles` : la table porte l'identité/temps et le pointeur exact `current_revision_seq`, tandis que `candle_revisions` reste la source unique des valeurs et de leur provenance. Les transitions transactionnelles, l'idempotence et l'allocation monotone restent explicitement reportées à P1E.

Aucune nouvelle dépendance n'est introduite en P1D. SQLAlchemy, Psycopg, PostgreSQL et Alembic restent ceux validés en P1A.

Le gate local P1D a été exécuté le 7 septembre 2026 sur Python 3.14.7 et PostgreSQL 18.6 : PostgreSQL est `healthy`, la migration `0001_market_data_schema` est appliquée au `head`, `alembic check` ne détecte aucune opération supplémentaire, Ruff est propre sur 17 fichiers, Pyright termine avec `0 errors, 0 warnings` et un code de sortie `0`, et pytest termine avec `64 passed, 1 skipped`. Le seul skip est le smoke Binance P1C désactivé par défaut. Les tests PostgreSQL confirment la création effective des trois tables, l'écriture atomique de la première `Candle` avec sa révision `revision_seq = 1` grâce aux contraintes différées, et l'unicité d'une seule `pending_confirmation` par lignée. La revue sémantique finale n'a identifié aucun blocage P1D.

## Source canonique P0

`BTC_ANALYTICS_V2_P0_CANONICAL_v7.md`

Les décisions validées restent à ajouts uniquement (append-only) dans `docs/10_DECISIONS.md`.

## Prochaine étape

Créer et revoir le commit candidat de **P1D — schéma PostgreSQL canonique**, puis attendre la validation explicite de l'utilisateur avant de passer P1D au statut `VALIDATED`.
