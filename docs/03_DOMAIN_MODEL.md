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
