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
