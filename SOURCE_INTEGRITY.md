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
