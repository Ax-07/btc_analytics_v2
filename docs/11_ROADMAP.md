# 11 — Feuille de route

## P0 — Fondation

Charte, architecture, stack, identité/provenance du domaine, conventions temporelles, contrat causal, sémantique des données de marché, conventions outcome/baseline, évaluation des dépendances, politique qualité et journal de décisions.

## P1 — Données de marché

Bootstrap du repository, PostgreSQL, adaptateur CCXT, Candle canonique clôturée, ingestion native `1h`/`4h`/`1d`, validation, gaps, audit des révisions, idempotence, fixture CCXT-vs-native.

## P2 — Cœur analytique

Alignement temporel, interface/registre des features, versionnement/fingerprints, conventions Polars/NumPy, politique de matérialisation.

## P3 — Caractéristiques techniques (`features`)

Rendements/range, ATR, RSI, volatilité, momentum, volume et features standards sélectionnées avec tests causaux/golden.

## P4 — Structure de marché

Extrema causaux, prominence, pivots/swings, HH/HL/LH/LL, amplitude, durée, pente, retracement, compression/expansion.

## P5 — Événements, occurrences et contextes basiques

Définitions d'événements, identité d'occurrence, événements techniques/structurels, shortlist validée de configurations de chandeliers, ContextDefinition/ContextSnapshot causaux basiques et occurrences filtrées par contexte.

## P6 — Résultats futurs (`outcomes`)

OutcomeDefinitions versionnées, rendements futurs, MFE, MAE, définition de volatilité future, états de complétude/gap et populations de baseline.

## P7 — Moteur d'expériences

DatasetSnapshots, grilles de paramètres, évaluation batch multi-timeframe, BaselineDefinition, walk-forward et rapports de robustesse.

## P8 — Contextes avancés et régimes

Combinaisons d'états plus riches, recherche sur les régimes, exploration offline de points de rupture et règles de promotion causale.

## P9 — Poste de travail analytique

API + graphique + inspection structure/événement/contexte + comparaison occurrences/outcomes/expériences.

## P10 — Analyses optionnelles

Figures chartistes ou autres modèles interprétatifs uniquement si une valeur incrémentale est démontrée. P10 peut rester vide.
