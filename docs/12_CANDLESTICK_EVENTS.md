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
