# 12 — Candlestick Events

## Positionnement

Couche analytique prévue mais non fondamentale.

## Règles

Un candlestick pattern :

- est calculé sur candles clôturées ;
- possède `event_time` et `known_at` ;
- n'implique aucune recommandation ;
- est versionné ;
- utilise le même Outcome Engine que les autres événements.

## Shortlist initiale à étudier

Doji, Hammer, Inverted Hammer, Shooting Star, Bullish/Bearish Engulfing, Morning/Evening Star, Three White Soldiers, Three Black Crows.

## TA-Lib

Candidat principal pour implémentation et/ou oracle.

Avant adoption canonique : définition exacte, causalité, golden tests, conventions de sortie.

## Utilité

Mesurer le pattern seul puis conditionné par contexte : tendance, volatilité, structure, etc.
