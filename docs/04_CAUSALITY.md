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
