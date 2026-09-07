# BTC Analytics V2 — P0 Canonique v7

> Source maître consolidée validée pour BTC Analytics V2.
> `P0 — VALIDATED` — D-001 à D-020 approuvées explicitement par l'utilisateur le 6 septembre 2026 après deux audits finaux indépendants `P0 — VALIDATION READY`.
> La présente version française est une traduction documentaire non sémantique ; le tag `p0-foundation-v7` conserve l'historique exact validé.


---

## FICHIER SOURCE : `README.md`

# BTC Analytics V2

BTC Analytics V2 est une plateforme d'analyse quantitative et structurelle du marché Bitcoin.

Le projet repart volontairement de zéro au niveau du code afin d'éviter d'hériter de la dette architecturale de la V1. La V1 reste figée comme prototype de référence et source de leçons, mais son code n'est pas copié par défaut.

## Objectif

Transformer des données de marché en primitives causales, structures, événements et contextes mesurables, puis étudier objectivement ce qui s'est produit après leurs occurrences historiques.

BTC Analytics V2 n'est pas un bot de trading, un moteur d'exécution, un gestionnaire de portefeuille ni un système de recommandations d'achat/vente.

## Principes

1. Causalité stricte pour toute information déclarée connue à T.
2. Primitives objectives avant interprétations humaines.
3. Toute hypothèse analytique doit pouvoir être mesurée.
4. Séparation stricte entre production et recherche.
5. Les dépendances externes fournissent des briques ; l'intelligence métier reste développée dans BTC Analytics.
6. Les figures chartistes sont optionnelles et ne constituent pas une fondation du projet.
7. Les configurations de chandeliers sont traitées comme des événements analytiques, jamais comme des signaux de trading.

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

P0 a été explicitement validé le 6 septembre 2026 après deux audits finaux indépendants de la v7 et l'approbation utilisateur en bloc de D-001 à D-020. P1 peut désormais commencer en respectant strictement les contrats P0 validés.


---

## FICHIER SOURCE : `P0_START_HERE.md`

# P0 — Commencer ici

## Objectif

P0 transforme la vision de la V2 en contrat de développement avant l'écriture de code de production.

## Lecture obligatoire

1. `P0_AUDIT_RESOLUTION.md`
2. `docs/00_PROJECT_CHARTER.md`
3. `docs/01_ARCHITECTURE.md`
4. `docs/02_TECH_STACK.md`
5. `docs/03_DOMAIN_MODEL.md`
6. `docs/04_CAUSALITY.md`
7. `docs/05_MARKET_DATA.md`
8. `docs/15_TEMPORAL_CONVENTIONS.md`
9. `docs/16_OUTCOME_BASELINE_CONVENTIONS.md`
10. `docs/17_DEPENDENCY_ASSESSMENT.md`
11. `docs/10_DECISIONS.md`
12. `docs/11_ROADMAP.md`

## Critères de validation de P0

P0 n'est validé que lorsque :

- le périmètre du projet et le hors-périmètre sont explicites ;
- les coordonnées temporelles sont sans ambiguïté ;
- les frontières de `features/`, `outcomes/` et `research/` sont stables ;
- les identités Market/Candle/Event/Occurrence/Context/Outcome/Experiment sont suffisamment stables pour que des implémentations indépendantes convergent ;
- les conventions d'outcome et de baseline sont explicites ;
- les politiques de gaps, révisions et timeframes natifs des données de marché sont explicites ;
- le rôle des dépendances est documenté ;
- le journal de décisions D-001 à D-020 est explicitement approuvé ;
- aucune question bloquante ne subsiste.

## Statut de validation

`P0 — VALIDATED`

Les audits finaux indépendants de la v7 ont conclu `P0 — VALIDATION READY`, et D-001 à D-020 ont été explicitement approuvées par l'utilisateur le 6 septembre 2026.

## Règle

P1 est autorisé à démarrer à partir de ce contrat P0 validé. Toute modification sémantique d'une décision P0 validée exige une nouvelle décision explicite et versionnée ; elle ne doit jamais réécrire silencieusement l'historique de P0.


---

## FICHIER SOURCE : `CURRENT_STATE.md`

# État courant

## Projet

BTC Analytics V2

## Phase

P0 — Fondation / documentation

## Statut

`P0 — VALIDATED`

La v7 ferme le dernier blocage identifié lors de l'audit indépendant de la v6 : une candidate `CandleRevision` existait entre sa création et sa confirmation native, mais `revision_status` ne possédait aucun état représentant cette phase intermédiaire.

Le contrat définit désormais `pending_confirmation` :

- la candidate reçoit son `revision_seq` et son `observed_at` dès sa création ;
- elle reste sans `accepted_at` et n'est jamais éligible au PIT tant que la confirmation n'a pas réussi ;
- confirmation réussie -> `accepted_current` et l'ancienne révision courante devient `accepted_superseded` ;
- désaccord, indisponibilité ou échec de validation -> `quarantined` ;
- une seule candidate `pending_confirmation` est autorisée à la fois par lignée de bougie afin de sérialiser les transitions et d'empêcher les acceptations hors ordre ;
- après interruption, une candidate en attente reste durablement en attente jusqu'à reprise/résolution et n'est jamais assimilée à une révision acceptée.

Les deux audits finaux indépendants de la v7 ont conclu `P0 — VALIDATION READY`. Le 6 septembre 2026, l'utilisateur a explicitement approuvé D-001 à D-020 en bloc. Le critère de passage P0 est donc satisfait et P1 est autorisé à démarrer à partir de ces contrats validés.

## Source canonique ChatGPT recommandée

Utiliser en priorité le fichier unique :

`BTC_ANALYTICS_V2_P0_CANONICAL_v7.md`

Ne pas conserver simultanément un ancien document maître P0 dans les sources actives du projet ChatGPT.

## Prochaine étape

Figer le jalon Git P0 validé, puis démarrer **P1 — Données de marché** dans une nouvelle discussion sans modifier rétroactivement les décisions P0 validées.


---

## FICHIER SOURCE : `LESSONS_FROM_V1.md`

# Leçons de BTC Analytics V1

La V1 ne doit pas être considérée comme un échec. Elle a servi de prototype permettant d'identifier des invariants importants pour la V2.

## Ce qui doit être conservé conceptuellement

### Causalité explicite

Un phénomène physique peut appartenir à une bougie T sans être connaissable à T.

La V2 doit séparer `event_time` / `pivot_time` du moment `confirmed_at` / `known_at`.

### Analyse prospective séparée de la détection

La détection ne doit jamais utiliser le futur. Les outcomes futurs peuvent utiliser le futur uniquement après qu'une occurrence a été figée comme connue à T.

### Backend comme source analytique

Le frontend ne recalcule pas la logique analytique.

### Inspection visuelle indispensable

Une métrique ou un score ne suffit pas à valider une représentation structurelle.

### Les figures chartistes sont subjectives

La V2 privilégie les swings, amplitudes, durées, retracements, pentes, compressions/expansions et HH/HL/LH/LL. Les figures chartistes deviennent optionnelles.

## Ce qui doit être évité

- introduire une feature simplement parce qu'elle est populaire en analyse technique ;
- calibrer des seuils avant de prouver l'utilité d'une représentation ;
- mélanger code de recherche et code de production ;
- laisser un fournisseur de données imposer ses objets au domaine ;
- ajouter trop tôt des couches UI ou des abstractions sophistiquées ;
- optimiser avant profiling ;
- utiliser une méthode offline comme si elle était causale ;
- transformer le projet en moteur de stratégie/backtest.

## V1 figée

Dernier jalon de référence : `p8b-pattern-calibration-frontend`.

La V1 peut être consultée pour comparer les résultats, pas comme base de code de la V2.


---

## FICHIER SOURCE : `P0_AUDIT_RESOLUTION.md`

# Résolution de l'audit P0 — Consolidée v7

## Statut

`P0 — VALIDATED`

Cette révision ferme le dernier blocage signalé par l'audit indépendant de la v6. Deux audits finaux indépendants de la v7 ont ensuite conclu `P0 — VALIDATION READY`. Le 6 septembre 2026, l'utilisateur a explicitement approuvé D-001 à D-020 en bloc. P0 est donc validé et P1 est autorisé à démarrer à partir de ces contrats figés.

## Blocages v6 précédemment résolus

La candidate v6 avait déjà fermé :

- la règle point-in-time obsolète `observed_at <= T` dans les conventions temporelles, remplacée par la règle canonique `accepted_at <= T` ;
- le cycle de vie de la première `CandleRevision` acceptée, notamment `revision_seq = 1`, les références locales stables de révision et l'allocation monotone de séquence à la création d'une candidate.

Ces contrats restent inchangés.

## Blocage R6 — état non résolu d'une candidate de révision

Le modèle v6 créait une candidate de révision distincte et allouait son `revision_seq` avant la confirmation native de la même venue, mais les valeurs autorisées de `revision_status` étaient uniquement `accepted_current`, `accepted_superseded` et `quarantined`. Aucun statut ne représentait l'intervalle réel entre la création de la candidate et la résolution de la confirmation.

Contrat de candidate résolu en v7 :

- `revision_status` inclut en plus `pending_confirmation` ;
- une observation ultérieure distincte d'une bougie déjà acceptée crée une révision durable `pending_confirmation` avec le prochain `revision_seq`, `observed_at` et sans `accepted_at` ;
- `pending_confirmation` n'est jamais éligible à `observed_point_in_time` ;
- une confirmation native réussie fait passer cette même révision à `accepted_current`, enregistre `accepted_at` et fait passer l'ancienne révision courante acceptée à `accepted_superseded` ;
- un désaccord, une confirmation indisponible ou un échec de validation fait passer cette même révision à `quarantined`, en conservant sa séquence et sans renseigner `accepted_at` ;
- une promotion ou une mise en quarantaine ne renumérote jamais la révision ;
- au plus une révision `pending_confirmation` non résolue peut exister à la fois pour une lignée de bougie ; le traitement d'une autre candidate distincte pour cette bougie est sérialisé jusqu'à résolution de la révision en attente ;
- une observation de mêmes valeurs correspondant à la candidate en attente est idempotente et n'alloue pas une nouvelle séquence ;
- après interruption/redémarrage, une révision en attente non résolue reste pending et non éligible au PIT jusqu'à ce que la confirmation soit retentée/résolue ; elle n'est jamais silencieusement considérée comme acceptée ou quarantined.

## Mise à jour de décision

D-020 inclut désormais explicitement l'état `pending_confirmation`, sa non-éligibilité au PIT et la règle de sérialisation des transitions par candle.

## Tests ajoutés au contrat

Les tests de révision de données doivent en plus vérifier :

- qu'une observation modifiée est persistée comme `pending_confirmation` avant le retour de la confirmation ;
- qu'une révision en attente possède `observed_at`, n'a pas d'`accepted_at` et n'est jamais éligible au PIT ;
- qu'une confirmation réussie fait passer la même révision/séquence à `accepted_current` ;
- qu'une confirmation échouée ou indisponible fait passer la même révision/séquence à `quarantined` ;
- qu'une réobservation de mêmes valeurs d'une candidate en attente est idempotente ;
- qu'une bougie ne peut pas avoir deux candidates en attente non résolues et que les résultats de confirmation ne peuvent pas être appliqués hors ordre ;
- qu'un redémarrage/recovery conserve l'état pending sans impliquer une acceptation.

## Critère de validation — satisfait

- Audit final indépendant A : `P0 — VALIDATION READY`.
- Audit final indépendant B : `P0 — VALIDATION READY`.
- Approbation utilisateur : D-001 à D-020 explicitement approuvées en bloc le 6 septembre 2026.

Résultat : `P0 — VALIDATED`. P1 peut démarrer, mais les décisions P0 validées sont des contrats historiques à ajouts uniquement (append-only) et ne doivent jamais être réécrites silencieusement.


---

## FICHIER SOURCE : `SOURCE_INTEGRITY.md`

# Intégrité des sources — P0 v7

## État de validation

`P0 — VALIDATED`

Deux audits finaux indépendants de la v7 ont conclu `P0 — VALIDATION READY`, et l'utilisateur a explicitement approuvé D-001 à D-020 en bloc le 6 septembre 2026. Les contrats sémantiques v7 sont figés comme référence P0 validée.

## Source canonique ChatGPT

Utiliser un seul fichier source :

`BTC_ANALYTICS_V2_P0_CANONICAL_v7.md`

Ne pas conserver simultanément d'anciens fichiers maîtres P0 dans les mêmes sources de projet.

## Marqueurs v7 obligatoires

La source canonique v7 doit contenir tous les éléments suivants :

- le journal de décisions D-001 à D-020 ;
- `RFC 8785` et `parameter_fingerprint` ;
- le payload exact `occurrence-key.v1` ;
- `DatasetSnapshot` avec `knowledge_mode` ;
- le modèle `CandleRevision` ;
- la première révision acceptée avec `revision_seq = 1` ;
- la référence exacte et stable de révision `(market, timeframe, open_time, revision_seq)` ;
- les observations distinctes ultérieures allouent le prochain `revision_seq` lors de la création de la candidate ;
- `revision_status` inclut `pending_confirmation`, `accepted_current`, `accepted_superseded`, `quarantined` ;
- les candidates en attente possèdent `observed_at`, n'ont pas d'`accepted_at` et ne sont jamais éligibles au PIT ;
- au plus une candidate en attente non résolue par lignée de bougie ;
- une confirmation en attente survit à une interruption/redémarrage sans impliquer une acceptation ;
- les candidates mises en quarantaine conservent leur séquence allouée et n'ont pas d'`accepted_at` ;
- `observed_at` ;
- `accepted_at` ;
- l'invariant `observed_at <= accepted_at` pour les révisions acceptées ;
- `revision acceptance policy v1` ;
- `reconstructed_latest` ;
- `observed_point_in_time` ;
- la règle d'éligibilité PIT `accepted_at <= T` ;
- `observed_at <= T` seul est insuffisant pour le PIT ;
- les révisions mises en quarantaine ne sont jamais éligibles au PIT ;
- confirmation native sur la même venue pour les candles acceptées modifiées et absence de remplacement cross-exchange ;
- l'ingestion initiale ne requiert pas de confirmation native candle par candle ;
- Pyright ;
- les contextes basiques en P5 ;
- les contextes avancés et régimes en P8 ;
- PostgreSQL comme autorité canonique courante ;
- snapshots Parquet immuables ;
- tests généralisés d'invariance par préfixe ;
- tests de révision de données couvrant la révision initiale, la confirmation en attente, l'observation avant acceptation, la quarantaine et la reprise.

Si un audit affirme que ces marqueurs sont absents, il ne lit pas la source canonique v7.


---

## FICHIER SOURCE : `docs/00_PROJECT_CHARTER.md`

# 00 — Charte du projet

## Vision

BTC Analytics V2 est une plateforme d'analyse quantitative et structurelle du marché Bitcoin.

Le système doit permettre de collecter et valider des données de marché fiables, calculer des features causales, représenter objectivement la structure du marché, détecter des événements reproductibles, caractériser des contextes/régimes, retrouver les occurrences historiques et mesurer ce qui s'est produit après chaque occurrence.

## Objectif central

> Lorsqu'une condition observable X est connue à T, comment la distribution du comportement futur du marché diffère-t-elle de sa distribution de référence ?

## Non-objectifs

V2 n'est pas :

- un bot de trading ;
- un moteur d'ordres ;
- un système d'achat/vente ;
- un gestionnaire de portefeuille ;
- une plateforme de copy trading ;
- un optimiseur de stratégie ;
- une plateforme ML par défaut.

## Périmètre initial

### Marché

- Bitcoin spot ;
- fournisseur initial : Binance ;
- accès principal : CCXT derrière une abstraction interne ;
- marché initial : BTC/USDC côté fournisseur ;
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
- événements de chandeliers ;
- contextes ;
- outcomes futurs.

### Figures chartistes

Les figures chartistes ne sont pas un objectif central. Elles pourront être ajoutées comme interprétations optionnelles si elles démontrent une valeur analytique supplémentaire.

## Principes

- causalité stricte ;
- explicabilité ;
- reproductibilité ;
- mesurabilité ;
- séparation recherche/production.

## Définition du succès

Le succès n'est pas d'accumuler des indicateurs. Le succès est d'obtenir un système où les données sont fiables, les features sont causales, les occurrences comparables, les outcomes cohérents, les expérimentations reproductibles et les analyses inutiles rejetables objectivement.


---

## FICHIER SOURCE : `docs/01_ARCHITECTURE.md`

# 01 — Architecture

## Vue conceptuelle

```text
Exchange
   |
   v
Accès aux données de marché
   |
   v
Normalisation + Validation
   |
   v
Données de marché canoniques
   |
   +-------------------+
   |                   |
   v                   v
Moteur de features   Jeu de données de recherche
causales             (Parquet/DuckDB)
   |
   v
Structure de marché
   |
   v
Moteur d'événements
   |
   v
Moteur de contextes
   |
   v
Stockage des occurrences
   |
   +------------------------+
   |                        |
   v                        v
API produit             Moteur d'outcomes
                             |
                             v
                        Moteur d'expériences
```

## Frontières obligatoires

- `market_data/` : accès exchange, pagination, normalisation, validation, stockage ; aucune logique analytique.
- `features/` : calculs strictement causaux.
- `structure/` : pivots, swings, HH/HL/LH/LL, retracements, métriques de segments.
- `events/` : événements timestampés construits à partir d'informations causales.
- `contexts/` : état de marché à T.
- `occurrences/` : instances figées d'une définition satisfaite.
- `outcomes/` : seule couche analytique autorisée à lire après T.
- `experiments/` : comparaisons de définitions, paramètres, timeframes, périodes.
- `research/` : zone non canonique ; look-ahead/offline autorisé s'il est déclaré.

## Backend / frontend

FastAPI expose les contrats internes. Le frontend ne dépend jamais directement de CCXT, TA-Lib, DuckDB, VectorBT ou SciPy et ne recalcule pas les features métier.

## Structure cible

```text
btc_analytics_v2/
├── backend/
│   ├── src/btc_analytics/
│   │   ├── api/
│   │   ├── domain/
│   │   ├── market_data/
│   │   ├── features/
│   │   ├── structure/
│   │   ├── events/
│   │   ├── contexts/
│   │   ├── occurrences/
│   │   ├── outcomes/
│   │   ├── experiments/
│   │   ├── storage/
│   │   └── observability/
│   └── tests/
├── frontend/
├── research/
├── docs/
├── infra/
└── pyproject.toml
```


---

## FICHIER SOURCE : `docs/02_TECH_STACK.md`

# 02 — Stack technique

## Politique

Les bibliothèques externes fournissent des primitives génériques. BTC Analytics possède la sémantique du domaine, les contrats causaux, le versionnement et la reproductibilité.

Les versions exactes des paquets sont figées dans les fichiers de verrouillage lors de l'amorçage du dépôt, après vérification de compatibilité.

## ADOPT — produit/exécution

- Python
- NumPy
- Polars
- SciPy
- CCXT derrière `MarketDataProvider`
- TA-Lib derrière des adaptateurs internes pour les fonctions sélectionnées et validées
- PostgreSQL
- FastAPI
- Pydantic
- Alembic

## ADOPT — développement

- uv
- pytest
- Ruff
- **Pyright**
- GitHub Actions
- Docker Compose

## ADOPT — frontend

- Next.js
- TypeScript
- pnpm
- Lightweight Charts
- shadcn/ui

## ADOPT — recherche/snapshots de données

- Parquet
- DuckDB

## RESEARCH / REFERENCE

- VectorBT : concepts d'expérimentation vectorisée, grilles et walk-forward ; pas de moteur produit de portefeuille.
- ruptures : recherche hors ligne de points de rupture uniquement jusqu'à validation d'une formulation causale.
- statsmodels : uniquement lorsqu'un besoin statistique concret existe.

## REJECT comme dépendances produit

- PatternPy
- TradingPatternScanner

## Décision TA-Lib à périmètre limité

TA-Lib peut exécuter certains indicateurs standards et certaines fonctions de chandeliers uniquement lorsque chaque fonction sélectionnée possède :

- des entrées et une période rétrospective (`lookback`) documentées ;
- une vérification causale sous la sémantique de bougies clôturées (`closed-candle`) de BTC Analytics ;
- des tests de référence (`golden tests`) ;
- un adaptateur BTC Analytics (`wrapper`) avec définition/version.

TA-Lib peut également servir d'oracle de référence pour des primitives implémentées en interne.

## Règle de performance

1. algorithme correct ;
2. implémentation vectorisée NumPy/Polars ;
3. profilage ;
4. Numba/Rust uniquement pour des goulots d'étranglement démontrés.


---

## FICHIER SOURCE : `docs/03_DOMAIN_MODEL.md`

# 03 — Modèle de domaine

## Primitives d'identité partagées

### Représentation canonique des paramètres

Chaque définition analytique canonique possède un schéma de paramètres.

Avant le calcul d'identité :

- toutes les valeurs par défaut du schéma sont matérialisées explicitement ;
- les noms des membres d'objet et les valeurs d'enum/string utilisent l'orthographe canonique de leur schéma ;
- les collections non ordonnées sont triées selon la règle propre au schéma de leur définition avant sérialisation ;
- les timestamps, lorsqu'ils sont des paramètres, utilisent des millisecondes Unix UTC entières ;
- les nombres non finis (`NaN`, `+Inf`, `-Inf`) sont interdits ;
- les sémantiques décimales exactes doivent être représentées par des chaînes décimales normalisées, et non par des nombres flottants binaires.

Les octets canoniques des paramètres sont les octets UTF-8 de l'objet de paramètres sérialisé avec le **JSON Canonicalization Scheme (JCS) RFC 8785**.

Les chaînes décimales normalisées utilisent :

- aucun `+` initial ;
- `-0` normalisé en `0` ;
- aucun zéro entier initial inutile ;
- aucun zéro fractionnaire final inutile ;
- aucun point décimal lorsque la partie fractionnaire est vide ;
- une notation décimale en base 10 sans exposant, sauf si une définition versionnée spécifie explicitement une autre représentation.

Exemples :

```text
"001.2300" -> forme d'entrée invalide ; valeur sémantique normalisée -> "1.23"
"-0.000"   -> "0"
"2.500"    -> "2.5"
```

### DefinitionIdentity

Chaque définition analytique canonique possède :

- `definition_key` : clé namespacée stable ;
- `definition_version` : change dès que la sémantique change ;
- `parameters` : objet de paramètres canoniques normalisés ;
- `parameter_fingerprint`.

`parameter_fingerprint` vaut exactement :

```text
"sha256:" + lowercase_hex(SHA-256(JCS(parameters)))
```

Le hash couvre uniquement les paramètres normalisés. La clé et la version de définition restent des champs d'identité explicites.

### Provenance

Les artefacts dérivés canoniques doivent être traçables jusqu'à :

- market ;
- timeframe ;
- l'identité des données source ou le DatasetSnapshot lorsque pertinent ;
- la clé/version de définition ;
- le fingerprint des paramètres ;
- la révision logicielle/le run de calcul lorsque cela est matériel.

## Market

- venue
- base_asset
- quote_asset
- market_type
- canonical_symbol

`canonical_symbol` est un identifiant de domaine BTC Analytics indépendant de la notation CCXT/fournisseur.

## Candle

Bougie OHLCV clôturée canonique :

- market
- timeframe
- `open_time`
- `end_time`
- open
- high
- low
- close
- `base_volume`
- `quote_volume` optionnel
- `trade_count` optionnel
- source
- source_symbol
- `available_at`
- `ingested_at`
- métadonnées de la révision courante acceptée

Identité :

```text
(market, timeframe, open_time)
```

L'intervalle canonique est `[open_time, end_time)` et `available_at = end_time` dans le modèle analytique initial de bougies clôturées reconstruites.

## CandleRevision

Chaque bougie canonique possède une lignée de révisions explicite et append-only, comprenant sa première observation acceptée et chaque observation distincte ultérieure.

Champs minimaux :

- identité de la bougie `(market, timeframe, open_time)` ;
- `revision_seq` local croissant de manière monotone ;
- valeurs OHLCV normalisées ;
- `observed_at` ;
- `accepted_at` optionnel ;
- `revision_status` : `pending_confirmation`, `accepted_current`, `accepted_superseded`, `quarantined` ;
- provenance du fournisseur primaire ;
- provenance de confirmation lorsque nécessaire ;
- fingerprints logiques avant/après des valeurs ;
- motif/métadonnées d'audit.

La référence locale exacte et stable d'une révision est :

```text
(market, timeframe, open_time, revision_seq)
```

### Première révision acceptée

La première observation valide d'une bougie clôturée jusque-là inconnue crée immédiatement la première révision :

- `revision_seq = 1` ;
- `observed_at` = premier instant auquel BTC Analytics a observé cette bougie normalisée ;
- `accepted_at` = instant où la validation canonique réussit ;
- `revision_status = accepted_current`.

L'acceptation initiale ne requiert pas de confirmation native individuelle sur la même venue pour chaque bougie. La correction du chemin fournisseur est validée séparément par la fixture P1 bornée CCXT-vs-native.

### Observations distinctes ultérieures

Toute observation ultérieure qui diffère des valeurs logiques de la révision courante acceptée crée une nouvelle candidate de révision et reçoit le prochain `revision_seq` croissant **au moment de la création de la candidate**. Les numéros de séquence ne sont jamais réutilisés.

La nouvelle candidate est persistée avec `revision_status = pending_confirmation`, possède `observed_at` et n'a pas d'`accepted_at`. Une révision `pending_confirmation` n'est jamais éligible au PIT.

Pour une lignée de bougie donnée, au plus une révision `pending_confirmation` non résolue peut exister à la fois. Le traitement d'une autre candidate distincte pour cette bougie est sérialisé jusqu'à résolution de la révision en attente. Une réobservation de mêmes valeurs correspondant à la candidate en attente est idempotente et ne crée aucune révision supplémentaire. Cela empêche l'application des résultats de confirmation hors ordre de révision.

Si la confirmation native réussit, la **même** révision en attente passe à `accepted_current` : la promotion ne la renumérote jamais, enregistre `accepted_at` et marque la précédente révision courante acceptée comme `accepted_superseded`. Si la confirmation est en désaccord, indisponible ou si la validation échoue, la même révision en attente passe à `quarantined`, conserve son `revision_seq` alloué et garde `accepted_at` absent.

Une interruption ou un redémarrage n'infère aucun statut terminal : une révision en attente non résolue reste `pending_confirmation`, reste non éligible au PIT et doit être retentée/réconciliée avant le traitement d'une autre candidate distincte pour la même bougie.

Une réobservation de mêmes valeurs que la révision courante acceptée est idempotente et ne crée aucun nouvel état sémantique de révision lorsqu'aucune candidate en attente conflictuelle n'existe.

Une révision ultérieure ne modifie jamais un DatasetSnapshot immuable.

`observed_at` est le premier instant auquel BTC Analytics a observé cette révision. Une correction observée plus tard ne doit jamais être représentée comme ayant réellement été observée par le système à l'`end_time` historique de la bougie.

`accepted_at` est l'instant auquel la validation/confirmation requise réussit et où la révision devient l'état canonique accepté. Il est présent uniquement pour les révisions qui ont été acceptées au moins une fois (`accepted_current` ou `accepted_superseded`). Une révision mise en quarantaine n'a pas d'`accepted_at`.

Pour chaque révision acceptée :

```text
observed_at <= accepted_at
```

`accepted_at` est une provenance temporelle. Il ne participe pas à l'identité de Candle, DefinitionIdentity, `occurrence_key` ni à aucune autre identité sémantique, sauf si un futur contrat versionné le prévoit explicitement.

## FeatureDefinition / FeatureValue

Un FeatureValue inclut l'identité de définition, market/timeframe, `event_time`, `known_at`, les valeurs et la provenance.

## StructuralPoint

- `physical_time`
- `known_at`
- price
- kind
- identité de définition
- métriques
- provenance

`physical_time < known_at` est valide pour une structure historique confirmée.

## StructuralSegment

Relie des points structurels et enregistre direction, rendement, amplitude normalisée par ATR, durée, pente, vélocité et relations de retracement.

Son `known_at` ne peut pas précéder le `known_at` le plus tardif parmi les entrées requises.

## EventDefinition / Event

Un Event est une occurrence causale versionnée avec :

- identité de définition ;
- `event_time` ;
- `known_at` ;
- preuves/valeurs ;
- `instance_discriminator` déterministe ;
- provenance.

Pour une DefinitionIdentity, un market, un timeframe et une bougie d'ancrage donnés, la règle par défaut est au plus un événement canonique avec `instance_discriminator = "0"`.

Si une définition peut émettre plusieurs événements canoniques distincts pour le même ancrage, son schéma versionné doit définir un `instance_discriminator` déterministe et non vide.

## ContextDefinition / ContextSnapshot

Un ContextSnapshot est un état causal évalué sur une bougie d'ancrage en utilisant uniquement des artefacts dont `known_at <= anchor.end_time`.

## Occurrence

Unité centrale de l'analyse historique.

Champs minimaux :

- `occurrence_key` déterministe ;
- identité de définition ;
- market/timeframe ;
- `event_time` lorsqu'il a un sens physique ;
- `known_at` ;
- identité de la bougie d'ancrage ;
- `instance_discriminator` ;
- référence/snapshot de contexte lorsque utilisé ;
- provenance/références d'entrées.

### Payload de la clé d'occurrence

Le payload exact d'identité v1 est :

```json
{
  "schema": "occurrence-key.v1",
  "definition_key": "<canonical definition_key>",
  "definition_version": "<canonical definition_version>",
  "parameter_fingerprint": "sha256:<hex>",
  "market": "<canonical market symbol>",
  "timeframe": "<canonical timeframe>",
  "anchor_open_time_ms": 0,
  "event_time_ms": 0,
  "instance_discriminator": "0"
}
```

Règles :

- les timestamps sont des millisecondes Unix UTC entières ;
- `event_time_ms` est le temps canonique d'attribution physique/de l'événement ; si la définition n'a pas d'attribution physique distincte, il est égal à l'`end_time` de la bougie d'ancrage ;
- `instance_discriminator` vaut par défaut `"0"` ;
- le contexte ne fait **pas** partie de l'identité de l'occurrence ; les contextes sont un état analytique attaché et peuvent servir au découpage sans dupliquer l'occurrence ;
- DatasetSnapshot est une provenance, pas une identité d'occurrence, de sorte qu'une même occurrence sémantique peut être comparée entre snapshots/révisions.

`occurrence_key` vaut exactement :

```text
"sha256:" + lowercase_hex(SHA-256(JCS(occurrence_key_payload)))
```

L'ordre d'insertion en base, les identifiants de substitution et les identifiants de run de calcul ne participent jamais à la clé.

## OutcomeDefinition

Définit :

- clé/version de métrique ;
- horizon en barres ;
- convention de prix de référence ;
- convention de fenêtre future ;
- politique de gaps ;
- paramètres spécifiques à la métrique.

L'identité des paramètres d'OutcomeDefinition suit la même règle JCS/SHA-256.

## Outcome

Attaché à une Occurrence et une OutcomeDefinition.

Un Outcome ne modifie jamais l'occurrence d'origine et peut être `complete`, `incomplete_gap` ou `incomplete_end_of_dataset`.

## BaselineDefinition

Chaque expérience comparant des distributions conditionnelles doit définir explicitement sa population de baseline :

- market/timeframe ;
- plage historique ;
- politique d'ancrages éligibles ;
- filtre de contexte le cas échéant ;
- mêmes conventions d'outcomes/gaps ;
- politique/version d'échantillonnage.

L'identité de BaselineDefinition suit les mêmes règles de canonicalisation des paramètres que DefinitionIdentity.

## DatasetSnapshot

Identité immuable d'entrée d'expérience contenant au minimum :

- `snapshot_id` ;
- markets/timeframes sources ;
- couverture temporelle ;
- instant de création ;
- `knowledge_mode` ;
- hashes de manifeste/contenu ;
- résumé des gaps ;
- références exactes des CandleRevision acceptées incluses dans le snapshot.

Valeurs initiales de `knowledge_mode` :

- `reconstructed_latest` ;
- `observed_point_in_time` lorsqu'un historique suffisant d'observation/révision existe.

Le payload d'identité du snapshot exclut l'instant de création et inclut :

- schéma/version du snapshot ;
- markets/timeframes ;
- couverture temporelle ;
- knowledge mode ;
- hash logique du manifeste des identités de bougies + identifiants de révisions acceptées incluses.

`snapshot_id` vaut :

```text
"sha256:" + lowercase_hex(SHA-256(JCS(snapshot_identity_payload)))
```

Parquet est le format physique initial des snapshots analytiques immuables. La disposition physique des octets Parquet n'est pas utilisée comme seule identité logique, car différents writers peuvent encoder différemment des données logiquement équivalentes.

## ExperimentDefinition / ExperimentRun

Un run fige :

- DatasetSnapshot ;
- versions des définitions analytiques ;
- grille de paramètres ;
- OutcomeDefinitions ;
- BaselineDefinition ;
- politique de split ;
- révision logicielle/configuration.


---

## FICHIER SOURCE : `docs/04_CAUSALITY.md`

# 04 — Contrat de causalité

## Règle absolue

Si BTC Analytics affirme qu'un artefact est connu à T, aucune information postérieure à T ne peut avoir contribué à cet artefact.

## Cadence initiale

Les analyses canoniques P0–P8 fonctionnent sur des **bougies clôturées**.

Les artefacts dérivés deviennent donc connus sur les frontières canoniques de bougies, sauf si un futur jalon définit explicitement un contrat intrabar.

## Coordonnées temporelles

- `open_time` de la bougie : début inclusif ;
- `end_time` de la bougie : fin exclusive ;
- `available_at` de la bougie : `end_time` dans la sémantique historique closed-bar ;
- `event_time`/`physical_time` dérivé : instant auquel appartient physiquement le phénomène ;
- `known_at` dérivé : premier instant canonique auquel toutes les preuves requises sont disponibles ;
- `ingested_at` : instant d'observation par le système, pas un substitut à l'`known_at` analytique.

## Règles par couche

### market_data

Les barres ouvertes ou encore en cours côté fournisseur ne sont pas éligibles au calcul analytique canonique.

### features

Strictement causal. Interdit sans formulation explicite avec `known_at` retardé :

- `shift(-1)` ;
- fenêtres centrées ;
- lissage ajusté sur la série complète ;
- ajustement global de paramètres sur la série complète ;
- extrema confirmés par le futur affectés rétroactivement à leur temps physique.

### structure

Peut référencer un point physique passé, mais la latence de confirmation doit être représentée par `known_at`.

### events / contexts / occurrences

`known_at` est supérieur ou égal à chaque `known_at` d'entrée requis.

### outcomes

L'utilisation du futur est autorisée uniquement après que la sélection de l'occurrence a été figée.

### research

Les méthodes look-ahead/offline sont autorisées uniquement lorsqu'elles sont explicitement étiquetées comme recherche et ne peuvent pas être promues sans contrat causal de production.

## Tests obligatoires d'invariance par préfixe

Ils s'appliquent à tout artefact déclaré connu à T :

- FeatureValue ;
- StructuralPoint ;
- StructuralSegment ;
- Event ;
- ContextSnapshot ;
- Occurrence dérivée.

Protocole de test :

1. calculer sur la série complète ;
2. calculer sur plusieurs préfixes historiques se terminant à différents T ;
3. comparer les artefacts dont `known_at <= T` ;
4. l'ajout de barres futures ne doit pas modifier leur identité, valeur ou état canonique.

Toute révision ultérieure légitime doit être modélisée comme un nouvel état/une nouvelle version explicitement timestampée, jamais comme une mutation rétroactive silencieuse.


---

## FICHIER SOURCE : `docs/05_MARKET_DATA.md`

# 05 — Données de marché

## Objectif

Fournir des bougies clôturées fiables et indépendantes de la plateforme d'échange pour l'usage analytique.

## Architecture d'accès

```text
Plateforme d'échange -> Adaptateur CCXT -> DTO fournisseur -> Normaliseur -> Validateur -> Bougie canonique (`Candle`)
                                                          -> stockage canonique courant PostgreSQL
                                                          -> snapshots analytiques immuables Parquet
```

## Fournisseur/marché initial

- bibliothèque d'accès : CCXT ;
- plateforme d'échange : Binance Spot ;
- symbole fournisseur : `BTC/USDC` ;
- l'identité canonique interne du marché est indépendante de la notation CCXT.

Le domaine n'importe jamais de types CCXT.

## Sémantique de la bougie canonique

- intervalle : `[open_time, end_time)` ;
- UTC ;
- P1 stocke/utilise des bougies clôturées pour l'analytique ;
- `available_at = end_time` décrit la disponibilité historique de la barre en temps de marché ;
- les timestamps bruts de clôture propres au fournisseur peuvent être conservés uniquement comme provenance.

### Volume

Le `base_volume` canonique est le volume dans l'actif de base (BTC pour BTC/USDC).

Si elles sont conservées, l'activité en devise de cotation est nommée `quote_volume` et le nombre de transactions `trade_count`. Aucun champ canonique ambigu nommé simplement `volume` n'est utilisé dans les contrats du domaine.

## Unités de temps natives initiales (`timeframes`)

- `1h`
- `4h`
- `1d`

P1 récupère chaque unité de temps nativement auprès du fournisseur. Aucun rééchantillonnage canonique (`resampling`) n'est effectué en P1.

L'alignement UTC attendu est validé.

Si une plateforme d'échange ou un fournisseur ne prend pas en charge une unité de temps native requise, ce couple `market/timeframe` est non pris en charge jusqu'à l'ajout explicite d'un contrat distinct de rééchantillonnage (`resampling`).

## Validation

- alignement fuseau horaire/intervalle ;
- invariants OHLC ;
- volumes/nombres de transactions non négatifs ;
- unicité ;
- statut/éligibilité de clôture ;
- ordre monotone ;
- détection des doublons ;
- détection des gaps.

## Politique des lacunes (`gaps`)

Une lacune (`gap`) n'est jamais interpolée silencieusement.

Les analyses canoniques traitent les lacunes (`gaps`) comme des frontières dures de continuité :

- la phase d'initialisation (`warm-up`) des `features` glissantes redémarre après un `gap` lorsqu'une continuité est requise ;
- les algorithmes structurels ne relient pas par défaut des points de part et d'autre d'un gap ;
- les événements/contextes dépendant d'un historique continu sont indisponibles jusqu'à ce que leurs exigences soient de nouveau satisfaites ;
- un horizon d'`Outcome` traversant un `gap` est `incomplete_gap` ;
- ExperimentRun rapporte les exclusions et comptes incomplets.

## Autorité PostgreSQL

PostgreSQL est le **stockage produit canonique courant**.

Les observations répétées qui se normalisent vers les mêmes valeurs sont idempotentes.

### Ingestion initiale d'une bougie clôturée

Pour la première observation valide d'une bougie clôturée jusque-là inconnue :

1. normaliser l'observation du fournisseur ;
2. valider tous les invariants canoniques ;
3. créer une `CandleRevision` avec `revision_seq = 1` ;
4. enregistrer `observed_at` au premier instant où BTC Analytics a observé cette bougie normalisée ;
5. enregistrer `accepted_at` lorsque la validation canonique réussit ;
6. définir `revision_status = accepted_current` ;
7. faire référencer cet identifiant exact de révision par l'état courant de la Candle canonique.

La première révision acceptée ne requiert **pas** de confirmation individuelle par bougie contre l'endpoint natif. P1 valide plutôt le chemin fournisseur CCXT avec un jeu de test de référence borné (`fixture`) CCXT-vs-Binance-native défini ci-dessous. Une confirmation native par bougie est requise lorsqu'une observation ultérieure entre en conflit avec une bougie déjà acceptée.

La référence locale exacte de révision est `(market, timeframe, open_time, revision_seq)`.

### Bougie clôturée modifiée : politique d'acceptation des révisions v1 (`revision acceptance policy v1`)

Une réobservation différente d'une bougie clôturée déjà stockée n'écrase jamais directement l'état courant.

Le flux déterministe est :

1. normaliser la nouvelle observation ;
2. valider tous les invariants canoniques ;
3. la comparer à la révision courante acceptée ;
4. si les valeurs sont identiques, ne rien faire hormis d'éventuelles métadonnées d'observation ;
5. si les valeurs diffèrent, créer et persister une candidate de révision avec le prochain `revision_seq` croissant, enregistrer `observed_at`, définir `revision_status = pending_confirmation` et laisser `accepted_at` absent ;
6. confirmer cette candidate en attente contre l'endpoint natif faisant autorité configuré pour la **même venue et le même marché** ;
7. promouvoir la candidate uniquement si la confirmation native normalisée concorde sur OHLC canonique et `base_volume` ;
8. en cas de confirmation, faire passer cette même révision de `pending_confirmation` à `accepted_current`, enregistrer `accepted_at` à l'instant de la promotion réussie, marquer l'ancienne révision comme `accepted_superseded`, préserver le `revision_seq` déjà alloué à la candidate et écrire l'entrée d'audit avant/après ;
9. si la confirmation est en désaccord, indisponible ou si la validation échoue, faire passer cette même révision de `pending_confirmation` à `quarantined`, préserver son `revision_seq`, laisser `accepted_at` absent et ne pas modifier les valeurs canoniques courantes de PostgreSQL.

Pour le fournisseur Binance initial, la source de confirmation est l'endpoint natif Binance klines.

Aucune observation provenant d'un autre exchange/d'une autre venue ne peut remplacer automatiquement la bougie canonique Binance.

### Sérialisation des confirmations en attente (`pending_confirmation`)

Pour une lignée de bougie donnée, au plus une révision `pending_confirmation` non résolue peut exister à la fois. Le traitement des confirmations est sérialisé par bougie afin qu'une ancienne candidate en attente ne puisse pas être acceptée après une candidate plus récente et écraser l'ordre d'acceptation.

Tant qu'une révision est en attente :

- une réobservation avec les mêmes valeurs logiques normalisées que cette révision en attente est idempotente et n'alloue pas de nouveau `revision_seq` ;
- une autre candidate distincte pour la même bougie n'est pas traitée comme nouvelle révision avant résolution de la candidate en attente existante ;
- `accepted_at` reste absent et la révision en attente n'est jamais éligible au relecture point-in-time (`PIT`).

Si le traitement est interrompu, la révision en attente persistée reste `pending_confirmation` après redémarrage. La reprise retente/réconcilie cette révision exacte avant de traiter une autre candidate distincte pour la même bougie ; le redémarrage seul ne la promeut ni ne la met en quarantaine.

### Sémantique temporelle des révisions

Trois notions ne doivent pas être confondues :

- `available_at = end_time` : disponibilité en temps de marché de la bougie terminée dans le modèle reconstruit à bougies clôturées (`closed-bar`) ;
- `CandleRevision.observed_at` : instant où BTC Analytics a observé pour la première fois une candidate de révision particulière ;
- `CandleRevision.accepted_at` : instant où la validation/confirmation a réussi et où cette révision est devenue l'état canonique accepté.

Pour toute révision acceptée, `observed_at <= accepted_at`. Les révisions en attente et `quarantined` n'ont pas d'`accepted_at`.

Une correction découverte plus tard n'est jamais présentée comme ayant été **observée par le système** ou **acceptée** à l'`end_time` historique d'origine.

## Modes de connaissance du jeu de données

### `reconstructed_latest`

Mode par défaut pour la recherche analytique historique.

Le snapshot (`DatasetSnapshot`) utilise la révision courante acceptée de chaque bougie au moment de sa création.

Le séquençage causal des features/événements est ancré sur l'`end_time` des bougies, mais l'exécution doit être décrite comme une **analyse historique `reconstructed_latest`**. Il ne doit pas prétendre que des corrections ultérieures du fournisseur étaient réellement connues de BTC Analytics ou d'un acteur de marché au T historique d'origine.

Ce mode convient à la question : « analyser la meilleure reconstruction de l'histoire actuellement disponible ».

### `observed_point_in_time`

Mode strict de replay.

Une révision de bougie ne peut influencer un ancrage T que si elle était déjà devenue l'état canonique accepté au plus tard à T.

Pour une bougie donnée, le relecture point-in-time (`PIT`) sélectionne la révision acceptée ayant le plus grand `accepted_at` satisfaisant :

```text
accepted_at <= T
```

`observed_at <= T` seul est insuffisant : une candidate `pending_confirmation` qui n'avait pas encore passé la confirmation à T ne peut pas influencer le replay. Les révisions en attente et `quarantined` ne sont jamais éligibles car elles n'ont pas d'`accepted_at`.

Exemple : si une candidate est observée à 10:00 et acceptée à 10:05, le replay à 10:02 utilise la révision précédemment acceptée ; le replay à 10:05 ou après peut utiliser la nouvelle révision acceptée.

Ce mode n'est valide que pour les périodes disposant d'une provenance continue suffisante d'observation/révision. Un backfill historique antérieur à la couverture d'observation de BTC Analytics ne peut pas être silencieusement traité comme un historique observé point-in-time.

P0 définit la sémantique ; P1 n'a pas à implémenter un moteur complet de relecture point-in-time (`PIT`) live sauf si cela est explicitement planifié.

## Snapshots Parquet

Les snapshots Parquet sont des datasets dérivés immuables pour l'analytique/recherche reproductible, pas une seconde autorité mutable.

Chaque DatasetSnapshot fige :

- les identités de bougies ;
- les identifiants exacts de révisions acceptées ;
- le knowledge mode ;
- les gaps ;
- les hashes logiques de manifeste/contenu.

Une correction ultérieure de bougie PostgreSQL ne modifie jamais un snapshot existant.

## Idempotence

Des récupérations répétées qui se normalisent vers la même bougie canonique ne créent aucun nouvel état sémantique.

## Vérification croisée P1

Une fixture/plage bornée compare les OHLCV Binance via CCXT aux klines natives Binance pour timestamp/OHLC/base volume après normalisation.

Le même chemin natif est utilisé comme confirmation uniquement lorsqu'une observation historique modifiée nécessite la validation d'une révision.

## Temps réel

Hors périmètre P1. La gestion WebSocket/des bougies ouvertes requiert un futur contrat explicite intrabar/live.


---

## FICHIER SOURCE : `docs/06_ANALYTICS_METHODOLOGY.md`

# 06 — Méthodologie analytique

## Hiérarchie

```text
OHLCV
  -> Features primitives
  -> Structure de marché
  -> Événements
  -> Contextes
  -> Occurrences
  -> Outcomes futurs
```

## Caractéristiques initiales (`features`)

### Prix

rendements, range, gaps, position dans le range.

### Volatilité

true range, ATR, volatilité réalisée, expansion/compression.

### Momentum

RSI, ROC, MACD seulement si justifié.

### Tendance

pente, ADX, structure.

### Volume

volume brut, normalisé, changements relatifs.

### Structure

extrema, prominence, swings, HH/HL/LH/LL, amplitude ATR, durée, retracement, pente, compression/expansion.

## Événements

Causaux, versionnés, timestampés, explicables, testables.

## Configurations de chandeliers

Liste initiale à étudier :

- Doji
- Hammer
- Inverted Hammer
- Shooting Star
- Bullish Engulfing
- Bearish Engulfing
- Morning Star
- Evening Star
- Three White Soldiers
- Three Black Crows

Ils sont des événements, jamais des recommandations.

## Figures chartistes

Optionnelles. Une figure ne devient canonique que si sa définition est objective, causale, inspectable, stable et apporte une information supplémentaire mesurable.

## Mesure d'utilité

- nombre d'occurrences
- stabilité temporelle
- distribution conditionnelle des outcomes
- différence par rapport à la baseline
- robustesse multi-timeframe
- sensibilité aux paramètres
- robustesse walk-forward

## Langage

Éviter `buy`, `sell`, `entry`, `exit`, `take profit`, `stop loss` dans les contrats canoniques.


---

## FICHIER SOURCE : `docs/07_EXPERIMENT_ENGINE.md`

# 07 — Moteur d'expériences

## Objectif

Comparer des hypothèses analytiques à l'aide de grilles de paramètres batch/vectorisées, sans trading ni simulation de portefeuille.

## Entrées figées obligatoires

Chaque ExperimentRun enregistre :

- DatasetSnapshot, notamment son `knowledge_mode` et le manifeste exact de CandleRevision ;
- plage historique ;
- timeframes ;
- clés/versions de définitions ;
- grille de paramètres normalisée ;
- OutcomeDefinitions ;
- BaselineDefinition ;
- politique de split/walk-forward ;
- révision logicielle/configuration.

## Dimensions de paramètres

Exemples : timeframe, paramètres de feature, paramètres de structure, définition de contexte, horizon d'outcome.

## Métriques de résultat (`outcome`)

Métriques standards initiales :

- rendement futur de clôture ;
- MFE ;
- MAE ;
- volatilité future lorsque sa définition de métrique est versionnée.

Les sémantiques temporelles exactes sont définies dans `16_OUTCOME_BASELINE_CONVENTIONS.md`.

## Population de référence

Aucune expérience ne peut s'appuyer sur une formulation implicite telle que « baseline pertinente ». Une BaselineDefinition est obligatoire pour toute affirmation comparative.

Population de référence candidate par défaut : toutes les bougies d'ancrage éligibles du même market/timeframe/snapshot/plage de dates, en appliquant les mêmes règles de qualité des données, de gaps et de complétude des outcomes que l'échantillon conditionnel.

Les populations de référence alternatives doivent être explicites et versionnées.

## Walk-forward

Les périodes de calibration et d'évaluation sont séparées temporellement. Le run enregistre les frontières des splits et indique si les paramètres ont été sélectionnés à l'aide de folds antérieurs.

## Anti-surapprentissage

Exiger lorsque pertinent :

- évaluation hors échantillon ;
- stabilité temporelle ;
- robustesse multi-timeframe ;
- sensibilité aux paramètres ;
- rapport de taille d'échantillon.

## Reproductibilité de l'identité

Les paramètres d'expérience normalisés utilisent la représentation canonique des paramètres définie dans `03_DOMAIN_MODEL.md` :

- normalisation par schéma ;
- sérialisation RFC 8785 JCS ;
- fingerprints SHA-256 en hexadécimal minuscule.

ExperimentRun doit enregistrer les fingerprints exacts des paramètres utilisés.

## Sémantique de révision des données

Un ExperimentRun ne suit jamais l'état courant mutable de PostgreSQL après son lancement.

Il évalue le DatasetSnapshot immuable auquel il fait référence.

Si une correction ultérieure du fournisseur modifie les valeurs canoniques courantes de PostgreSQL, un nouveau snapshot/run est requis. Les résultats provenant de snapshots différents restent comparables grâce aux identités explicites de snapshots et à la provenance des révisions.


---

## FICHIER SOURCE : `docs/08_RESEARCH_CATALOG.md`

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


---

## FICHIER SOURCE : `docs/09_TESTING_QUALITY.md`

# 09 — Tests et qualité

## Outils

- pytest
- Ruff
- Pyright
- GitHub Actions

## Classes de tests

### Unitaires

Normalisation, indicateurs, métriques structurelles, règles d'événements, métriques d'outcomes, sérialiseurs.

### Invariants/tests de propriétés

Validité OHLC, alignement des intervalles, fingerprints déterministes, timestamps monotones, règles de gaps, conventions MFE/MAE.

### Intégration

CCXT -> normalisation/validation -> PostgreSQL ; snapshot -> DuckDB/Polars ; feature -> structure/event/context -> occurrence -> outcome.

### Jeux de données de référence

Petites fixtures versionnées pour la normalisation de marché, la parité avec les fonctions TA-Lib sélectionnées, la structure causale et les outcomes.

### Causalité/invariance par préfixe

Obligatoire pour tout artefact déclaré connu à T : feature, point/segment structurel, événement, contexte et occurrence dérivée.

### Tests de révision des données

Vérifier :

- que la première ingestion valide crée `revision_seq = 1` comme `accepted_current` ;
- que la première révision acceptée enregistre `observed_at` et `accepted_at` avec `observed_at <= accepted_at` ;
- que sa référence exacte de révision est stable pour les manifestes DatasetSnapshot ;
- qu'une nouvelle récupération avec les mêmes valeurs est idempotente et ne crée aucune nouvelle révision ;
- qu'une bougie source modifiée crée une révision persistée `pending_confirmation` avec le prochain `revision_seq` avant confirmation ;
- que la candidate en attente enregistre `observed_at`, n'a pas d'`accepted_at` et n'est jamais éligible au PIT ;
- qu'une réobservation de mêmes valeurs de la candidate en attente est idempotente et n'alloue pas de nouveau `revision_seq` ;
- qu'au plus une candidate en attente non résolue existe par lignée de bougie et que les résultats de confirmation ne peuvent pas être appliqués hors ordre ;
- qu'une interruption/redémarrage préserve l'état pending et n'implique jamais acceptation ou quarantaine ;
- qu'une candidate mise en quarantaine conserve sa séquence allouée et que la candidate suivante ne la réutilise pas ;
- qu'une promotion préserve le `revision_seq` déjà alloué à la candidate ;
- qu'un accord avec la confirmation native promeut la révision et enregistre `accepted_at` ;
- que toute révision acceptée satisfait `observed_at <= accepted_at` ;
- qu'un désaccord/une confirmation indisponible met la révision en `quarantined`, laisse `accepted_at` absent et préserve l'état canonique courant ;
- qu'une candidate observée n'est pas éligible au PIT avant `accepted_at` ;
- que le replay PIT sélectionne la révision acceptée ayant le plus grand `accepted_at <= T` ;
- qu'une révision mise en quarantaine n'est jamais éligible au PIT ;
- qu'une correction acceptée ne modifie jamais un DatasetSnapshot existant ;
- que `reconstructed_latest` et `observed_point_in_time` ne portent pas la même affirmation de connaissance historique ;
- fixture temporelle de référence : une candidate observée à 10:00 et acceptée à 10:05 ne doit pas affecter le replay à 10:02 et peut l'affecter à 10:05 ou après.

### Tests de référence (`golden tests`) d'identité déterministe

Les fixtures de référence doivent figer :

- la normalisation canonique des paramètres ;
- les octets RFC 8785 JCS ;
- le `parameter_fingerprint` SHA-256 ;
- le payload exact d'`occurrence_key` et la clé résultante ;
- l'identité logique de DatasetSnapshot.

Au moins une représentation de fixture indépendante doit vérifier que des objets de paramètres sémantiquement identiques mais dont l'ordre des clés d'entrée diffère produisent les mêmes fingerprints.

## Définition de terminé

Un jalon est terminé uniquement lorsque les docs/contrats, tests, edge cases, contrôles de causalité, migrations/API/UI lorsque pertinentes, `CURRENT_STATE.md` et l'état du jalon Git ont été validés.

Aucun jalon n'est déclaré validé avant l'examen des sorties réelles des commandes locales/CI.


---

## FICHIER SOURCE : `docs/10_DECISIONS.md`

# 10 — Journal de décisions — P0 validé

> Traduction documentaire non sémantique du journal P0 validé. Le texte historique exact approuvé reste figé dans le tag `p0-foundation-v7` au commit `a055c5f386ce328cb46d57908cf26ea9ddff4255`.

Politique : D-001 à D-020 ont été explicitement approuvées par l'utilisateur le 6 septembre 2026 et sont désormais des décisions historiques validées, à ajouts uniquement (append-only). Toute future modification sémantique exige une nouvelle décision explicite et versionnée et ne doit jamais réécrire silencieusement ces entrées.

| ID | Décision validée | Statut |
|---|---|---|
| D-001 | V2 est un repository greenfield ; le code de la V1 n'est pas migré automatiquement. | VALIDATED — USER APPROVED 2026-09-06 |
| D-002 | Le périmètre produit est l'analyse, pas le trading, la gestion de portefeuille, l'exécution d'ordres ou de stratégies. | VALIDATED — USER APPROVED 2026-09-06 |
| D-003 | Causalité stricte : aucun artefact déclaré connu à T ne peut utiliser d'information postérieure à T. | VALIDATED — USER APPROVED 2026-09-06 |
| D-004 | CCXT est l'implémentation initiale d'accès aux exchanges derrière une abstraction interne `MarketDataProvider`. | VALIDATED — USER APPROVED 2026-09-06 |
| D-005 | PostgreSQL est le stockage produit canonique courant ; les snapshots Parquet immuables servent la recherche reproductible ; DuckDB interroge ces snapshots. | VALIDATED — USER APPROVED 2026-09-06 |
| D-006 | Polars est le moteur dataframe principal ; NumPy/SciPy fournissent les primitives numériques/scientifiques. | VALIDATED — USER APPROVED 2026-09-06 |
| D-007 | Les fonctions TA-Lib sélectionnées peuvent être ADOPTées uniquement derrière des adaptateurs après validation causale/golden fonction par fonction ; TA-Lib peut aussi servir de REFERENCE. | VALIDATED — USER APPROVED 2026-09-06 |
| D-008 | VectorBT est une source d'inspiration RESEARCH/REFERENCE ; son moteur de portefeuille/trading n'est pas une dépendance produit. | VALIDATED — USER APPROVED 2026-09-06 |
| D-009 | Les configurations de chandeliers sont des événements analytiques, jamais des signaux de trading. | VALIDATED — USER APPROVED 2026-09-06 |
| D-010 | Les figures chartistes sont une interprétation optionnelle au-dessus de la structure de marché et exigent une valeur incrémentale démontrée. | VALIDATED — USER APPROVED 2026-09-06 |
| D-011 | L'intervalle de Candle canonique est `[open_time,end_time)` UTC ; en analytique closed-bar `available_at=end_time` ; `ingested_at` est une provenance technique. | VALIDATED — USER APPROVED 2026-09-06 |
| D-012 | Les analyses canoniques P0–P8 fonctionnent à la cadence des bougies clôturées ; une sémantique intrabar exige un futur contrat explicite. | VALIDATED — USER APPROVED 2026-09-06 |
| D-013 | Le prix de base d'un Outcome est la clôture de la bougie d'ancrage ; l'horizon H utilise les H prochaines bougies complètes en excluant la bougie d'ancrage. | VALIDATED — USER APPROVED 2026-09-06 |
| D-014 | Chaque ExperimentRun comparatif fige une BaselineDefinition explicite. | VALIDATED — USER APPROVED 2026-09-06 |
| D-015 | Les timeframes P1 `1h`/`4h`/`1d` sont récupérés nativement ; aucun resampling canonique ; les gaps sont des frontières dures de continuité. | VALIDATED — USER APPROVED 2026-09-06 |
| D-016 | Les corrections de bougies source sont auditées ; la reproductibilité des expériences utilise des DatasetSnapshots immuables. | VALIDATED — USER APPROVED 2026-09-06 |
| D-017 | Pyright est le type checker Python de V2. | VALIDATED — USER APPROVED 2026-09-06 |
| D-018 | Les définitions causales de contextes basiques passent en P5 ; P8 couvre les contextes avancés et régimes. | VALIDATED — USER APPROVED 2026-09-06 |
| D-019 | Les identités analytiques déterministes utilisent des paramètres normalisés par schéma, la sérialisation RFC 8785 JCS et des fingerprints SHA-256 en hexadécimal minuscule ; `occurrence_key.v1` utilise le payload canonique exact défini dans le modèle de domaine. | VALIDATED — USER APPROVED 2026-09-06 |
| D-020 | Chaque bougie clôturée canonique possède une lignée de révisions à ajouts uniquement (append-only) : la première ingestion valide crée `revision_seq = 1` comme `accepted_current` avec `observed_at` et `accepted_at` ; chaque observation distincte ultérieure alloue le prochain `revision_seq` lors de la création de la candidate et est persistée comme `pending_confirmation` avant confirmation native. Les révisions en attente n'ont pas d'`accepted_at`, ne sont jamais éligibles au PIT, survivent à une interruption sans acceptation implicite et sont sérialisées à au plus une candidate en attente non résolue par lignée de bougie. Les bougies acceptées modifiées sont confirmées contre l'endpoint natif faisant autorité de la même venue ; un accord fait passer la même révision en attente à `accepted_current` et supersède la précédente révision courante, tandis qu'un désaccord, une indisponibilité ou un échec de validation la fait passer à `quarantined` sans renumérotation. Les révisions acceptées satisfont `observed_at <= accepted_at` ; `observed_point_in_time` sélectionne uniquement la dernière révision acceptée dont `accepted_at <= T` ; les snapshots ne prétendent jamais rétroactivement qu'une correction tardive a été observée ou acceptée au T historique. | VALIDATED — USER APPROVED 2026-09-06 |


---

## FICHIER SOURCE : `docs/11_ROADMAP.md`

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


---

## FICHIER SOURCE : `docs/12_CANDLESTICK_EVENTS.md`

# 12 — Événements de chandeliers

## Positionnement

Couche analytique prévue mais non fondamentale.

## Règles

Une configuration de chandeliers :

- est calculée sur des bougies clôturées ;
- possède `event_time` et `known_at` ;
- n'implique aucune recommandation ;
- est versionnée ;
- utilise le même Outcome Engine que les autres événements.

## Liste initiale à étudier

Doji, Hammer, Inverted Hammer, Shooting Star, Bullish/Bearish Engulfing, Morning/Evening Star, Three White Soldiers, Three Black Crows.

## TA-Lib

Candidat principal pour implémentation et/ou oracle.

Avant adoption canonique : définition exacte, causalité, golden tests, conventions de sortie.

## Utilité

Mesurer la configuration seule puis conditionnée par contexte : tendance, volatilité, structure, etc.


---

## FICHIER SOURCE : `docs/13_OPTIONAL_CHART_PATTERNS.md`

# 13 — Figures chartistes optionnelles

## Positionnement

Les figures chartistes ne sont pas un objectif central.

## Ordre correct

```text
bougies -> extrema -> swings -> métriques structurelles -> figure nommée optionnelle
```

## Conditions d'adoption

- définition objective
- causalité
- stabilité multi-timeframe
- qualité visuelle
- valeur incrémentale par rapport à la structure
- robustesse hors échantillon

Question centrale :

> Le label apporte-t-il une information supplémentaire par rapport aux swings, amplitudes, contexte et métriques de structure ?

Aucun jalon P0-P9 ne dépend des figures chartistes.


---

## FICHIER SOURCE : `docs/14_OBSERVABILITY.md`

# 14 — Observabilité

## Minimum

Logs structurés avec composant, opération, market, timeframe, run_id, durée, nombres de lignes et contexte d'erreur.

## Métriques de qualité des données

bougies récupérées, doublons rejetés, gaps détectés, bougies invalides, dernière bougie clôturée, latence d'ingestion.

## Métriques analytiques

lignes de features, occurrences, durée des expériences, combinaisons de paramètres, échecs.

## Reproductibilité

Chaque batch significatif doit être relié à la version du code, la configuration, le dataset et les timestamps.

Commencer simplement ; ajouter OpenTelemetry/Prometheus uniquement en réponse à un besoin réel.


---

## FICHIER SOURCE : `docs/15_TEMPORAL_CONVENTIONS.md`

# 15 — Conventions temporelles

Ce document est le contrat canonique des coordonnées temporelles pour P0.

## Coordonnées d'une bougie

Pour une durée de timeframe `Δ` :

```text
open_time = t
end_time  = t + Δ
interval  = [t, t + Δ)
available_at = end_time
```

Tous les timestamps canoniques sont en UTC.

Les timestamps de clôture propres au fournisseur utilisant une dernière milliseconde inclusive sont normalisés et ne redéfinissent jamais l'intervalle canonique.

## Modèle analytique à bougies clôturées (`closed-bar`)

Les analyses initiales de la V2 utilisent uniquement des bougies complètes. `available_at=end_time` exprime la disponibilité historique en temps de marché de la barre OHLCV complète.

`ingested_at` enregistre quand BTC Analytics a observé/stocké une version et n'est pas utilisé pour déplacer les ancrages analytiques historiques.

Un futur sous-système temps réel/intrabar peut en plus modéliser la latence d'observation par le système, mais ne doit pas modifier rétroactivement la sémantique historique P0.

## Temporalité des artefacts dérivés

### Caractéristique (`Feature`) sur une bougie C

- `event_time = C.end_time` sauf si la définition documente une autre attribution en temps physique ;
- `known_at = C.end_time` si toutes les entrées requises sont disponibles à cet instant.

### Point structurel confirmé

Un pivot peut avoir :

```text
physical_time = candle_100.end_time
known_at      = candle_103.end_time
```

Le point appartient physiquement à 100 mais n'est pas éligible à la sélection d'occurrence avant 103.

### Événement multi-barres

La définition doit préciser :

- la règle d'attribution physique/de l'événement ;
- la dernière bougie de preuve requise ;
- `known_at = end_time` de cette dernière bougie requise.

## Jointures

Une jointure causale à l'ancrage T peut inclure uniquement des enregistrements avec `known_at <= T`.

Joindre un point structurel par son temps physique tout en ignorant son `known_at` ultérieur constitue une violation de causalité.

## Révisions de bougies et affirmations historiques

`available_at=end_time` appartient au modèle reconstructed closed-bar en temps de marché.

Chaque bougie canonique possède une lignée de révisions. Chaque révision enregistre `observed_at` ; toute révision qui devient acceptée enregistre en plus `accepted_at`.

Pour les révisions acceptées :

```text
observed_at <= accepted_at
```

Par conséquent :

- les analyses `reconstructed_latest` peuvent utiliser la dernière révision acceptée tout en ancrant le séquençage analytique des barres sur `end_time`, mais ne doivent pas prétendre qu'une correction ultérieure était réellement connue ou acceptée au T historique ;
- les analyses `observed_point_in_time` peuvent utiliser uniquement une révision acceptée dont `accepted_at <= T` ;
- `observed_at <= T` seul est insuffisant lorsque la candidate n'avait pas encore été acceptée à T ;
- pour une bougie donnée, le PIT sélectionne la révision acceptée ayant le plus grand `accepted_at <= T` ;
- les révisions quarantined n'ont pas d'`accepted_at` et ne sont jamais éligibles au PIT.

Exemple : une correction observée à 10:00 et acceptée à 10:05 ne peut pas influencer le replay à 10:02 ; elle devient éligible à 10:05.

Les périodes historiques sans provenance suffisante d'**observation et d'acceptation** ne peuvent pas être étiquetées `observed_point_in_time`. Les backfills historiques créés ultérieurement sont analysés avec `reconstructed_latest`, sauf s'il existe une véritable provenance point-in-time des révisions.


---

## FICHIER SOURCE : `docs/16_OUTCOME_BASELINE_CONVENTIONS.md`

# 16 — Conventions des résultats (`outcomes`) et des populations de référence (`baselines`)

## Ancrage

Les occurrences canoniques initiales sont ancrées sur des bougies clôturées.

`Occurrence.known_at` correspond à l'`end_time` d'une bougie d'ancrage A.

Prix de référence par défaut :

```text
P0 = close(A)
```

La bougie d'ancrage elle-même est exclue des fenêtres d'excursion future car son high/low s'est produit partiellement ou entièrement avant que l'occurrence ne devienne connue.

## Horizon H

L'horizon `H` est constitué des H prochaines bougies complètes attendues après A :

```text
A+1, A+2, ..., A+H
```

## Rendement futur de clôture

```text
return_H = close(A+H) / P0 - 1
```

## MFE

```text
MFE_H = max(0, max(high(A+i) / P0 - 1)), i=1..H
```

La MFE canonique est donc non négative. Si le prix ne se négocie jamais au-dessus de P0 pendant l'horizon, MFE vaut `0`.

## MAE

```text
MAE_H = min(0, min(low(A+i) / P0 - 1)), i=1..H
```

La MAE canonique est donc non positive. Si le prix ne se négocie jamais sous P0 pendant l'horizon, MAE vaut `0`.

## Futur manquant

Si la séquence attendue A+1..A+H contient :

- un gap de données -> `incomplete_gap` ;
- la fin du dataset disponible -> `incomplete_end_of_dataset`.

Aucune interpolation ni réduction de l'horizon n'est autorisée pour un résultat étiqueté complete.

## Définitions de métriques

La volatilité future et toute métrique supplémentaire exigent leur propre OutcomeDefinition versionnée avant utilisation canonique.

## `BaselineDefinition` — définition de population de référence

Chaque expérience comparative stocke une population de référence explicite (`BaselineDefinition`).

Population de référence candidate par défaut :

- même DatasetSnapshot ;
- même market/timeframe/plage de dates ;
- toutes les bougies d'ancrage clôturées éligibles ;
- mêmes règles de gaps/complétude ;
- mêmes OutcomeDefinitions ;
- aucun filtre de condition/événement sauf déclaration explicite.

Une population de référence appariée par contexte ou régime est autorisée uniquement comme BaselineDefinition distincte et versionnée.

## Cohérence des révisions de dataset

Les échantillons conditionnels et leur BaselineDefinition doivent utiliser le même DatasetSnapshot et donc les mêmes :

- knowledge mode ;
- ensemble de révisions de bougies ;
- état des gaps ;
- couverture temporelle.

Une comparaison entre différentes révisions de snapshots constitue une dimension distincte d'expérience/comparaison et ne doit jamais être masquée à l'intérieur d'une population de référence.


---

## FICHIER SOURCE : `docs/17_DEPENDENCY_ASSESSMENT.md`

# 17 — Évaluation des dépendances

Date de vérification : 2026-09-06. Les versions exactes sont figées uniquement lors de l'amorçage du dépôt.

## CCXT — ADOPT derrière adaptateur

- Fonction : accès unifié aux plateformes d'échange et aux données de marché.
- Méthode : implémentations propres aux plateformes d'échange exposées via une API unifiée comprenant la récupération OHLCV.
- Causalité : neutre ; BTC Analytics doit filtrer les barres clôturées et définir sa propre sémantique temporelle.
- Validation : requiert en P1 une vérification croisée contre les klines natives Binance.
- Maintenance : projet actif avec support Binance et documentation OHLCV unifiée à jour.
- Licence : MIT.
- Couplage : moyen en cas de fuite ; faible lorsqu'il est isolé derrière `MarketDataProvider`.
- Décision : ADOPT comme couche d'accès, pas comme modèle de domaine.

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
