# BTC Analytics V2

BTC Analytics V2 est une plateforme d'analyse quantitative et structurelle du marché Bitcoin.

Le projet repart volontairement de zéro au niveau du code afin d'éviter d'hériter de la dette architecturale de la V1. La V1 reste figée comme prototype de référence et source de leçons, mais son code n'est pas copié par défaut.

## Objectif

Transformer des données de marché en primitives causales, structures, événements et contextes mesurables, puis étudier objectivement ce qui s'est produit après leurs occurrences historiques.

BTC Analytics V2 n'est pas un bot de trading, un moteur d'exécution, un gestionnaire de portefeuille ou un système de recommandations buy/sell.

## Principes

1. Causalité stricte pour toute information déclarée connue à T.
2. Primitives objectives avant interprétations humaines.
3. Toute hypothèse analytique doit pouvoir être mesurée.
4. Séparation stricte entre production et recherche.
5. Les dépendances externes fournissent des briques ; l'intelligence métier reste développée dans BTC Analytics.
6. Les chart patterns sont optionnels et ne sont pas une fondation du projet.
7. Les patterns de chandeliers sont traités comme des événements analytiques, jamais comme des signaux de trading.

## Point de départ

Lire dans cet ordre :

1. `P0_START_HERE.md`
2. `docs/00_PROJECT_CHARTER.md`
3. `docs/01_ARCHITECTURE.md`
4. `docs/02_TECH_STACK.md`
5. `docs/03_DOMAIN_MODEL.md`
6. `docs/04_CAUSALITY.md`
7. `docs/11_ROADMAP.md`

## Source de vérité

En cas de contradiction :

1. décisions validées dans `docs/10_DECISIONS.md`
2. document métier/technique le plus spécifique
3. `docs/00_PROJECT_CHARTER.md`
4. `README.md`

Aucun code de production ne doit être écrit avant validation explicite de P0. La révision candidate v7 reste en attente de validation utilisateur.
