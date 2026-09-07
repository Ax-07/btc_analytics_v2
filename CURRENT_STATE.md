# État courant

## Projet

BTC Analytics V2

## Phase

P1 — Données de marché / P1E — Transitions et politique des révisions

## Statut

`P1E — VALIDATION READY / VALIDATION UTILISATEUR EN ATTENTE`

P0 — Fondation reste validé et figé au jalon `p0-foundation-v7`. P1A — Amorçage du backend reste validé et figé au jalon `p1a-backend-bootstrap`. P1B — Domaine des données de marché reste validé et figé au jalon `p1b-market-data-domain`. P1C — `MarketDataProvider` + adaptateur CCXT Binance reste validé et figé au jalon `p1c-ccxt-provider`. P1D — Schéma PostgreSQL canonique reste validé et figé au jalon `p1d-postgresql-schema`.

Le design P1E a été explicitement validé par l'utilisateur le 7 septembre 2026. L'implémentation candidate matérialise la machine transactionnelle D-020 au-dessus du schéma P1D : première ingestion acceptée, idempotence, allocation monotone de `revision_seq`, persistance `pending_confirmation`, sérialisation par lignée, promotion atomique, quarantaine et reprise après interruption.

L'implémentation conserve la séparation validée entre le contrat applicatif sous `market_data/` et PostgreSQL sous `storage/`. Les appels réseau de confirmation native restent hors transaction PostgreSQL : P1E persiste d'abord la candidate, puis une transition terminale applique ultérieurement le résultat exact de confirmation que P1G fournira.

Aucune nouvelle dépendance ni migration Alembic n'est introduite par le candidat P1E. Il réutilise SQLAlchemy/Psycopg/PostgreSQL validés en P1A, le domaine P1B et le schéma P1D. Le gate local final du 7 septembre 2026 est vert : Ruff et Pyright sont propres, Alembic reste sur `0001_market_data_schema (head)` sans dérive, les 11 tests PostgreSQL P1E passent, et la suite complète termine avec `81 passed, 1 skipped`. Le seul skip est le smoke Binance P1C désactivé par défaut. La revue finale a en outre ajouté une vérification défensive garantissant que la quarantaine refuse un état où `candles.current_revision_seq` ne pointe pas une `accepted_current`.

## Source canonique P0

`BTC_ANALYTICS_V2_P0_CANONICAL_v7.md`

Les décisions validées restent à ajouts uniquement (append-only) dans `docs/10_DECISIONS.md`.

## Prochaine étape

Créer et revoir le commit candidat de **P1E — transitions et politique des révisions**, puis attendre la validation explicite de l'utilisateur avant de passer P1E au statut `VALIDATED`.
