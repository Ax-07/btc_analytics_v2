# État courant

## Projet

BTC Analytics V2

## Phase

P1 — Données de marché / P1B — Domaine des données de marché

## Statut

`P1B — VALIDATED`

P0 — Fondation reste validé et figé au jalon `p0-foundation-v7`. P1A — Amorçage du backend reste validé et figé au jalon `p1a-backend-bootstrap`.

P1B traduit les contrats P0 de données de marché en primitives Python indépendantes des frameworks : `Market`, `Timeframe`, `Candle`, `CandleRevision` et `RevisionStatus`. L'implémentation candidate utilise des objets immuables, des timestamps UTC explicites et des invariants OHLCV/temps testables.

Aucun contrat sémantique P0 n'est modifié. `market_type` et `canonical_symbol` restent opaques tant qu'aucun contrat plus précis n'est validé. Les transitions de révision restent reportées à P1E ; CCXT à P1C ; PostgreSQL à P1D ; les gaps à P1F ; le contrôle croisé CCXT vs Binance native à P1G.

Le gate local P1B a été exécuté et audité le 7 septembre 2026 : Ruff lint et formatage sont passés, Pyright a terminé avec `0 errors, 0 warnings`, pytest avec `26 passed`, et `git diff --check` sans erreur. La revue finale des edge cases a également ajouté l'invariant P0 selon lequel `revision_seq = 1` représente nécessairement une révision acceptée. Le 7 septembre 2026, l'utilisateur a explicitement validé P1B après revue du gate local et de l'état Git. Le jalon P1B est donc **validé**.

## Source canonique P0

`BTC_ANALYTICS_V2_P0_CANONICAL_v7.md`

Les décisions validées restent à ajouts uniquement (append-only) dans `docs/10_DECISIONS.md`.

## Prochaine étape

Créer le commit de clôture P1B, pousser la branche `p1-market-data`, figer le jalon par un tag, puis démarrer **P1C — `MarketDataProvider` + adaptateur CCXT Binance** à partir des contrats P0 validés et du domaine P1B.
