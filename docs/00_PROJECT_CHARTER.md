# 00 — Project Charter

## Vision

BTC Analytics V2 est une plateforme d'analyse quantitative et structurelle du marché Bitcoin.

Le système doit permettre de collecter et valider des données de marché fiables, calculer des features causales, représenter objectivement la structure du marché, détecter des événements reproductibles, caractériser des contextes/régimes, retrouver les occurrences historiques et mesurer ce qui s'est produit après chaque occurrence.

## Objectif central

> Lorsqu'une condition observable X est connue à T, comment la distribution du comportement futur du marché diffère-t-elle de sa distribution de référence ?

## Non-objectifs

V2 n'est pas :

- un bot de trading ;
- un moteur d'ordres ;
- un système buy/sell ;
- un gestionnaire de portefeuille ;
- une plateforme de copy trading ;
- un optimiseur de stratégie ;
- une plateforme ML par défaut.

## Scope initial

### Marché

- Bitcoin spot ;
- provider initial : Binance ;
- accès principal : CCXT derrière une abstraction interne ;
- marché initial : BTC/USDC côté provider ;
- timeframes : `1h`, `4h`, `1d` ;
- UTC canonique.

### Analyses

- momentum ;
- volatilité ;
- volume ;
- tendance ;
- extrema ;
- swings ;
- HH/HL/LH/LL ;
- retracements ;
- durées ;
- pentes ;
- compression / expansion ;
- événements techniques ;
- événements chandeliers ;
- contextes ;
- forward outcomes.

### Chart patterns

Les figures chartistes ne sont pas un objectif central. Elles pourront être ajoutées comme interprétations optionnelles si elles démontrent une valeur analytique supplémentaire.

## Principes

- causalité stricte ;
- explicabilité ;
- reproductibilité ;
- mesurabilité ;
- séparation recherche/production.

## Définition du succès

Le succès n'est pas d'accumuler des indicateurs. Le succès est d'obtenir un système où les données sont fiables, les features sont causales, les occurrences comparables, les outcomes cohérents, les expérimentations reproductibles et les analyses inutiles rejetables objectivement.
