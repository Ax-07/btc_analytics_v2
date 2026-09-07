# État courant

## Projet

BTC Analytics V2

## Phase

P1 — Données de marché / P1C — `MarketDataProvider` + adaptateur CCXT Binance

## Statut

`P1C — VALIDATION READY / VALIDATION UTILISATEUR EN ATTENTE`

P0 — Fondation reste validé et figé au jalon `p0-foundation-v7`. P1A — Amorçage du backend reste validé et figé au jalon `p1a-backend-bootstrap`. P1B — Domaine des données de marché reste validé et figé au jalon `p1b-market-data-domain`.

P1C implémente la frontière `MarketDataProvider`, un DTO fournisseur interne distinct de la `Candle` canonique et l'adaptateur synchrone CCXT pour Binance Spot. Le DTO réutilise les identités `Market`/`Timeframe` de P1B sans importer de types CCXT dans le domaine. Le domaine P1B n'est pas modifié.

Le périmètre P1C reste limité à l'accès public OHLCV : mapping explicite `Market -> source_symbol`, récupération avec `since` explicite, filtrage des bougies non clôturées et isolation des erreurs CCXT derrière nos propres exceptions. La normalisation canonique complète, la persistance PostgreSQL, les transitions de révision, les gaps/contrôles de qualité et le cross-check CCXT-vs-Binance-native restent dans les sous-jalons P1 suivants.

CCXT reste classé **ADOPT derrière adaptateur**. La dépendance est revalidée pour P1C avant verrouillage local ; aucune API de trading, ordre ou portefeuille n'est utilisée.

Le gate local P1C a été exécuté le 7 septembre 2026 : Ruff lint et formatage sont passés, Pyright a terminé avec `0 errors, 0 warnings`, pytest avec `54 passed, 1 skipped` (le seul skip étant le smoke Binance désactivé par défaut), PostgreSQL était `healthy`, et le smoke public Binance a passé avec `1 passed`. La revue Git finale a confirmé les neuf fichiers P1C attendus. Le candidat est donc **prêt pour validation utilisateur**, mais n'est pas encore validé.

## Source canonique P0

`BTC_ANALYTICS_V2_P0_CANONICAL_v7.md`

Les décisions validées restent à ajouts uniquement (append-only) dans `docs/10_DECISIONS.md`.

## Prochaine étape

Créer le commit d'implémentation candidat de **P1C — `MarketDataProvider` + adaptateur CCXT Binance**, vérifier l'état Git, puis attendre la validation explicite de l'utilisateur avant de passer P1C au statut `VALIDATED` et de poursuivre vers P1D.
