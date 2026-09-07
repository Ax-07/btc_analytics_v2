# 17 — Évaluation des dépendances

Date de vérification initiale : 2026-09-06. Les versions exactes sont figées dans `pyproject.toml` et `uv.lock` au moment où chaque dépendance entre effectivement dans son jalon d'implémentation.

## CCXT — ADOPT derrière adaptateur

- Fonction : accès unifié aux plateformes d'échange et aux données de marché.
- Méthode : implémentations propres aux plateformes d'échange exposées via une API unifiée comprenant la récupération OHLCV.
- Causalité : neutre ; BTC Analytics doit filtrer les barres clôturées et définir sa propre sémantique temporelle.
- Validation : requiert en P1 une vérification croisée contre les klines natives Binance.
- Maintenance : projet actif avec support Binance et documentation OHLCV unifiée à jour.
- Licence : MIT.
- Couplage : moyen en cas de fuite ; faible lorsqu'il est isolé derrière `MarketDataProvider`.
- Décision : ADOPT comme couche d'accès, pas comme modèle de domaine.

### Revalidation P1C — 2026-09-07

- Version PyPI vérifiée : `4.5.77`, publiée le 1er septembre 2026.
- Licence recontrôlée : MIT.
- Métadonnées Python : `>=3.10` ; compatibilité réelle avec Python 3.14.7 confirmée localement par installation, tests et smoke public Binance.
- API recontrôlée : `fetchOHLCV` / `fetch_ohlcv`, `since` en millisecondes Unix UTC, timeframes exposés par l'exchange.
- Risque causal recontrôlé : la dernière bougie peut être incomplète ; BTC Analytics la filtre avec un cutoff capturé avant l'appel fournisseur afin de ne pas accepter une bougie qui se clôture pendant la requête.
- Qualité/tests : tests unitaires de la frontière, suite projet complète et smoke public Binance borné exécutés localement ; la fixture de parité native reste P1G.
- Dépendances : le verrouillage P1C fait passer le graphe uv de 19 à 41 paquets, soit CCXT plus 21 dépendances transitives verrouillées pour les plateformes supportées par le lock.
- Performances : P1C utilise le chemin synchrone batch avec `enableRateLimit=True`; aucune optimisation n'est revendiquée sans profiling. Ce coût est acceptable pour le périmètre borné P1C et sera réévalué uniquement sur mesure.
- Compatibilité architecturale : aucun type CCXT ne traverse `MarketDataProvider` vers le domaine ; l'adaptateur peut être remplacé sans modifier `Market`, `Timeframe` ou `Candle`.
- Les gaps éventuels sont transmis par CCXT tels que retournés par l'exchange ; leur politique canonique reste propriété de BTC Analytics.
- Décision maintenue : **ADOPT derrière `MarketDataProvider`**, usage P1C limité aux endpoints publics de données de marché.

## Polars — ADOPT

- Fonction : moteur de tableaux de données/transformation (`dataframe`).
- Méthode : moteur colonnaire Rust, optimisation différée des requêtes (`lazy`), exécution parallèle et traitement en flux (`streaming`).
- Causalité : neutre ; les expressions doivent toujours respecter les fenêtres causales BTC Analytics.
- Validation : documentation de projet solide et développement actif.
- Adéquation des performances : excellent candidat pour l'analytique colonnaire par lots (`batch`).
- Licence : MIT.
- Couplage : conserver les objets Polars dans les frontières calcul/stockage, pas dans les contrats API/domaine.

## SciPy — ADOPT

- Fonction : algorithmes scientifiques, statistiques et primitives de signal.
- Méthode : implémentations numériques/scientifiques matures ; `signal` peut fournir des primitives génériques de pics/prominence.
- Causalité : dépend de la fonction. Certains filtres/lissages peuvent être non causaux ; chaque usage adopté doit être revu.
- Validation : projet mature avec de nombreuses versions publiées et tests.
- Licence : BSD-3-Clause.
- Couplage : faible derrière les définitions BTC Analytics de features/structure.

## TA-Lib Python — ADOPT à périmètre limité + REFERENCE

- Fonction : indicateurs techniques standards et fonctions de configurations de chandeliers.
- Méthode : adaptateur Python/Cython (`wrapper`) au-dessus du cœur TA-Lib.
- Causalité : dépend de la fonction ; l'adoption exige une validation de période rétrospective / bougies clôturées (`lookback`/`closed-bar`) fonction par fonction.
- Validation : le projet classe le package comme production/stable ; adaptateurs/types (`wrappers`) disponibles pour les versions Python modernes.
- Maintenance : projet amont actif en 2026.
- Licence : wrapper Python BSD-2-Clause ; le cœur utilise une licence de famille BSD.
- Couplage : moyen si les noms de fonctions deviennent des contrats du domaine ; atténuer avec des définitions/adaptateurs internes.
- Décision : fonctions sélectionnées et validées en ADOPT ; usage oracle/référence en REFERENCE.

## DuckDB — ADOPT pour la recherche

- Fonction : SQL analytique local sur Parquet/jeux de données.
- Méthode : base analytique embarquée dans le processus (`in-process`) avec scan direct Parquet et pushdown.
- Causalité : neutre ; utilisée après construction du dataset.
- Validation : le projet documente une CI/des tests étendus, notamment des millions de requêtes.
- Maintenance : actif ; le projet reste à code source ouvert sous gouvernance d'une fondation indépendante.
- Licence : MIT.
- Couplage : faible car l'API produit ne dépend pas de DuckDB.

## FastAPI / Pydantic — ADOPT à la frontière API

- Fonction : API HTTP typée et schémas.
- Causalité : neutre.
- Licence : FastAPI MIT ; versions/compatibilité des paquets figées au bootstrap.
- Couplage : intentionnellement limité à la couche API/application ; le domaine doit rester indépendant du framework.

## uv — ADOPT pour l'outillage de développement

- Fonction : gestion des paquets/projet/environnement Python.
- Méthode : implémentation Rust et flux de travail de verrouillage/projet (`lock`).
- Causalité/exécution : aucune.
- Maintenance : actif et orienté production.
- Licence : MIT OR Apache-2.0.
- Couplage : développement uniquement.

## Ruff — ADOPT pour l'outillage de développement

- Fonction : analyse de style (`lint`) et formatage Python.
- Méthode : implémentation Rust.
- Causalité/exécution : aucune.
- Licence : MIT.
- Couplage : développement uniquement.

## Pyright — ADOPT pour l'outillage de développement

- Fonction : vérification statique des types Python.
- Méthode : vérificateur de types haute performance basé sur les standards.
- Causalité/exécution : aucune.
- Maintenance : projet actif.
- Licence : MIT.
- Couplage : développement uniquement.

## pytest — ADOPT pour l'outillage de développement

- Fonction : exécuteur/cadre de tests (`runner`/`framework`).
- Causalité/exécution : aucune dans le produit ; utilisé pour imposer les invariants causaux et les contrats d'intégration.
- Licence : MIT.
- Couplage : tests uniquement.

## VectorBT — RESEARCH / REFERENCE

Utiliser comme inspiration conceptuelle pour les grilles de paramètres vectorisées, la diffusion (`broadcasting`) et l'expérimentation walk-forward. Ne pas faire dépendre la sémantique produit ou les abstractions de portefeuille/trading de VectorBT.

## ruptures — RESEARCH

Les algorithmes hors ligne de points de rupture sont par défaut réservés à la recherche. Toute promotion en production exige une formulation causale démontrée séparément.

## PatternPy / TradingPatternScanner — REJECT produit

Les conserver uniquement comme références de comparaison/recherche. Ils ne constituent pas des fondations de la structure de marché ou de la sémantique des figures chartistes de V2.
