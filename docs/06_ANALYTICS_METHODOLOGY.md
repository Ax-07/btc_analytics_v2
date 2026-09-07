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
