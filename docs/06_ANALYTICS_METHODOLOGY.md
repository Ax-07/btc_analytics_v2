# 06 — Analytics Methodology

## Hiérarchie

```text
OHLCV
  -> Primitive Features
  -> Market Structure
  -> Events
  -> Contexts
  -> Occurrences
  -> Forward Outcomes
```

## Features initiales

### Prix

returns, range, gaps, position dans range.

### Volatilité

true range, ATR, realized volatility, expansion/compression.

### Momentum

RSI, ROC, MACD seulement si justifié.

### Trend

slope, ADX, structure.

### Volume

volume brut, normalisé, changements relatifs.

### Structure

extrema, prominence, swings, HH/HL/LH/LL, amplitude ATR, duration, retracement, slope, compression/expansion.

## Events

Causaux, versionnés, timestampés, explicables, testables.

## Candlestick patterns

Shortlist à étudier :

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

## Chart patterns

Optionnels. Une figure ne devient canonique que si sa définition est objective, causale, inspectable, stable et apporte une information supplémentaire mesurable.

## Mesure d'utilité

- nombre d'occurrences
- stabilité temporelle
- distribution conditionnelle des outcomes
- différence vs baseline
- robustesse multi-timeframe
- sensibilité aux paramètres
- robustesse walk-forward

## Langage

Éviter `buy`, `sell`, `entry`, `exit`, `take profit`, `stop loss` dans les contrats canoniques.
