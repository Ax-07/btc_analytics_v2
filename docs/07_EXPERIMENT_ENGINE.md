# 07 — Moteur d'expériences

## Objectif

Comparer des hypothèses analytiques à l'aide de grilles de paramètres batch/vectorisées, sans trading ni simulation de portefeuille.

## Entrées figées obligatoires

Chaque ExperimentRun enregistre :

- DatasetSnapshot, notamment son `knowledge_mode` et le manifeste exact de CandleRevision ;
- plage historique ;
- timeframes ;
- clés/versions de définitions ;
- grille de paramètres normalisée ;
- OutcomeDefinitions ;
- BaselineDefinition ;
- politique de split/walk-forward ;
- révision logicielle/configuration.

## Dimensions de paramètres

Exemples : timeframe, paramètres de feature, paramètres de structure, définition de contexte, horizon d'outcome.

## Métriques de résultat (`outcome`)

Métriques standards initiales :

- rendement futur de clôture ;
- MFE ;
- MAE ;
- volatilité future lorsque sa définition de métrique est versionnée.

Les sémantiques temporelles exactes sont définies dans `16_OUTCOME_BASELINE_CONVENTIONS.md`.

## Population de référence

Aucune expérience ne peut s'appuyer sur une formulation implicite telle que « baseline pertinente ». Une BaselineDefinition est obligatoire pour toute affirmation comparative.

Population de référence candidate par défaut : toutes les bougies d'ancrage éligibles du même market/timeframe/snapshot/plage de dates, en appliquant les mêmes règles de qualité des données, de gaps et de complétude des outcomes que l'échantillon conditionnel.

Les populations de référence alternatives doivent être explicites et versionnées.

## Walk-forward

Les périodes de calibration et d'évaluation sont séparées temporellement. Le run enregistre les frontières des splits et indique si les paramètres ont été sélectionnés à l'aide de folds antérieurs.

## Anti-surapprentissage

Exiger lorsque pertinent :

- évaluation hors échantillon ;
- stabilité temporelle ;
- robustesse multi-timeframe ;
- sensibilité aux paramètres ;
- rapport de taille d'échantillon.

## Reproductibilité de l'identité

Les paramètres d'expérience normalisés utilisent la représentation canonique des paramètres définie dans `03_DOMAIN_MODEL.md` :

- normalisation par schéma ;
- sérialisation RFC 8785 JCS ;
- fingerprints SHA-256 en hexadécimal minuscule.

ExperimentRun doit enregistrer les fingerprints exacts des paramètres utilisés.

## Sémantique de révision des données

Un ExperimentRun ne suit jamais l'état courant mutable de PostgreSQL après son lancement.

Il évalue le DatasetSnapshot immuable auquel il fait référence.

Si une correction ultérieure du fournisseur modifie les valeurs canoniques courantes de PostgreSQL, un nouveau snapshot/run est requis. Les résultats provenant de snapshots différents restent comparables grâce aux identités explicites de snapshots et à la provenance des révisions.
