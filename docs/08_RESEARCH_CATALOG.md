# 08 — Catalogue de recherche

Ce catalogue est un index de décisions. Les éléments détaillés concernant les dépendances structurelles figurent dans `17_DEPENDENCY_ASSESSMENT.md`.

| Outil | Statut candidat | Périmètre |
|---|---|---|
| NumPy | ADOPT | tableaux numériques |
| Polars | ADOPT | moteur de tableaux de données/requêtes (`dataframe`) |
| SciPy | ADOPT | primitives scientifiques/signal |
| CCXT | ADOPT | accès à la plateforme d'échange derrière adaptateur |
| fonctions TA-Lib sélectionnées | ADOPT | indicateurs/chandeliers standards validés derrière adaptateur |
| TA-Lib | REFERENCE | oracle/comparaison lorsque utile |
| PostgreSQL | ADOPT | stockage produit canonique courant |
| Parquet | ADOPT | snapshots de recherche immuables |
| DuckDB | ADOPT recherche | SQL analytique sur snapshots |
| FastAPI/Pydantic | ADOPT | API/contrats |
| uv | ADOPT dev | gestion des paquets/projet |
| Ruff | ADOPT dev | analyse de style (`lint`)/formatage |
| Pyright | ADOPT dev | typage statique |
| pytest | ADOPT dev | tests |
| VectorBT | RESEARCH/REFERENCE | concepts d'expérimentation vectorisée |
| ruptures | RESEARCH | recherche hors ligne de points de rupture |
| statsmodels | RESEARCH / adoption au besoin | méthodes statistiques |
| PatternPy | REJECT produit | comparaison uniquement |
| TradingPatternScanner | REJECT produit | comparaison/recherche uniquement |

## Dimensions d'évaluation obligatoires

Fonction, méthode, implications causales, validation/tests, maintenance, adéquation des performances, licence, couplage, périmètre final.

Un outil peut avoir des statuts différents selon ses rôles, mais ces rôles doivent être explicites (par exemple exécution TA-Lib vs oracle).
