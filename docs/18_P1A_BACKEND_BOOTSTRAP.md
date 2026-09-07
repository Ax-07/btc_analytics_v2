# P1A — Amorçage du backend

Statut : `VALIDATED — VALIDATION UTILISATEUR 2026-09-07`

P0 reste validé et inchangé. Cet amorçage n'introduit aucune sémantique de données de marché ni aucun schéma canonique produit.

## Périmètre

- amorçage Python 3.14 / uv ;
- `pyproject.toml` racine avec sources du package sous `backend/src` ;
- pytest, Ruff et Pyright ;
- infrastructure SQLAlchemy synchrone + Psycopg pour PostgreSQL ;
- PostgreSQL 18 via Docker Compose ;
- Alembic initialisé sans migration produit à ce stade ;
- CI GitHub Actions minimale ;
- tests minimaux d'import du package et de connectivité PostgreSQL.

## Éléments explicitement reportés

- `Market`, `Timeframe`, `Candle`, `CandleRevision` : P1B ;
- CCXT et DTO fournisseur : P1C ;
- schéma PostgreSQL canonique : P1D ;
- transitions d'état des révisions : P1E ;
- domaine des gaps / qualité des données : P1F ;
- fixture CCXT vs Binance native : P1G ;
- FastAPI/Pydantic, Polars/NumPy/SciPy : ajout uniquement lorsque le jalon prévu en a effectivement besoin.

## Choix d'implémentation P1A

Ces choix sont des décisions d'implémentation P1A et ne modifient pas rétroactivement P0 :

1. Version Python : branche 3.14, interpréteur local fixé par `.python-version`.
2. Backend de construction du package : `uv_build`, configuré pour `backend/src`.
3. Couche d'accès base de données : SQLAlchemy 2.0 stable, en mode synchrone adapté au pipeline batch initial.
4. Pilote PostgreSQL : Psycopg 3 avec extra binaire pour simplifier l'amorçage Windows.
5. CLI Pyright : wrapper Python communautaire utilisé comme véhicule d'exécution local afin d'éviter un prérequis Node séparé ; sa version PyPI au bootstrap est 1.1.411.
6. Dépendances Python directes contraintes dans `pyproject.toml` ; la résolution transitive exacte est figée dans `uv.lock` généré par uv.
7. Actions GitHub épinglées sur des SHA immuables ; uv est également épinglé explicitement.
8. Le package source est déclaré explicitement à Ruff/Pyright via `backend/src` et porte le marqueur PEP 561 `py.typed`.

## Résultats du gate local — 7 septembre 2026

Les contrôles suivants ont été effectivement exécutés et leurs sorties revues :

- uv mis à niveau en `0.12.10` ;
- Python `3.14.7` installé et sélectionné ;
- `uv lock` puis `uv sync --locked --all-groups` réussis ;
- PostgreSQL `18.6` démarré via Docker Compose et confirmé `healthy` ;
- connexion directe au conteneur confirmant la base `btc_analytics` et l'utilisateur `btc_analytics` ;
- `uv run alembic upgrade head` réussi ;
- `uv run ruff check backend` sans diagnostic ;
- `uv run ruff format --check backend` : 9 fichiers déjà formatés ;
- `uv run pyright` : 0 erreur, 0 avertissement ;
- `uv run pytest` : 2 tests réussis ;
- `git diff --check` : aucune erreur de whitespace ; seuls des avertissements de conversion LF/CRLF ont été observés sous Windows.

Ces résultats ont été revus, puis P1A a été explicitement validé par l'utilisateur le 7 septembre 2026.

## Validation finale

La validation finale de P1A couvre les sorties effectives suivantes :

- `uv lock` et `uv sync --locked --all-groups` ;
- démarrage et état `healthy` du PostgreSQL géré par Docker Compose ;
- connectivité directe au conteneur PostgreSQL ;
- `uv run alembic upgrade head` ;
- `uv run ruff check backend` ;
- `uv run ruff format --check backend` ;
- `uv run pyright` ;
- `uv run pytest` ;
- contrôles Git finaux.

## Décision de clôture

Le 7 septembre 2026, l'utilisateur a explicitement validé P1A après revue du gate local et de l'état Git. P1A est donc clôturé avec le statut `VALIDATED`. Le sous-jalon suivant autorisé est **P1B — Domaine des données de marché**.
