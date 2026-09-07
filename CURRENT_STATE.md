# État courant

## Projet

BTC Analytics V2

## Phase

P1 — Données de marché / P1A — Amorçage du backend

## Statut

`P1A — VALIDATED`

P0 — Fondation reste validé et figé au jalon `p0-foundation-v7`.

P1A introduit uniquement le socle backend et l'outillage nécessaires pour commencer l'implémentation de manière contrôlée :

- packaging du projet Python avec uv ;
- outillage qualité pytest, Ruff et Pyright ;
- infrastructure PostgreSQL de développement via Docker Compose ;
- initialisation d'Alembic sans tables produit canoniques à ce stade ;
- frontières initiales des packages `domain/`, `market_data/`, `storage/` et `observability/` ;
- tests minimaux de bon fonctionnement et CI GitHub Actions.

Aucun contrat sémantique P0 n'est modifié. P1A n'implémente pas encore `Market`, `Timeframe`, `Candle`, `CandleRevision`, l'adaptateur CCXT, le schéma PostgreSQL canonique, la politique de révision, la logique de gaps ni le contrôle croisé CCXT vs Binance native ; ces éléments restent planifiés dans les sous-jalons P1 suivants.

Le gate local P1A a été exécuté et audité le 7 septembre 2026 : uv/lockfile, PostgreSQL 18.6 via Docker Compose, Alembic, Ruff, Pyright et pytest sont passés sur l'environnement local. PostgreSQL a été confirmé `healthy` et la suite pytest a terminé avec `2 passed`.

Le 7 septembre 2026, l'utilisateur a explicitement validé P1A après revue des résultats locaux et de la séparation Git. Le jalon P1A est donc **validé**.

## Source canonique P0

`BTC_ANALYTICS_V2_P0_CANONICAL_v7.md`

Les décisions validées restent à ajouts uniquement (append-only) dans `docs/10_DECISIONS.md`.

## Prochaine étape

Créer le commit de clôture P1A, pousser la branche `p1-market-data`, puis démarrer **P1B — Domaine des données de marché** à partir des contrats P0 validés et du socle P1A.
