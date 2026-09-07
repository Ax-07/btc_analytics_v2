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
