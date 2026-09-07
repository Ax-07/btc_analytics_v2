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
