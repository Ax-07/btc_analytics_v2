# P0 — Commencer ici

## Objectif

P0 transforme la vision de la V2 en contrat de développement avant l'écriture de code de production.

## Lecture obligatoire

1. `P0_AUDIT_RESOLUTION.md`
2. `docs/00_PROJECT_CHARTER.md`
3. `docs/01_ARCHITECTURE.md`
4. `docs/02_TECH_STACK.md`
5. `docs/03_DOMAIN_MODEL.md`
6. `docs/04_CAUSALITY.md`
7. `docs/05_MARKET_DATA.md`
8. `docs/15_TEMPORAL_CONVENTIONS.md`
9. `docs/16_OUTCOME_BASELINE_CONVENTIONS.md`
10. `docs/17_DEPENDENCY_ASSESSMENT.md`
11. `docs/10_DECISIONS.md`
12. `docs/11_ROADMAP.md`

## Critères de validation de P0

P0 n'est validé que lorsque :

- le périmètre du projet et le hors-périmètre sont explicites ;
- les coordonnées temporelles sont sans ambiguïté ;
- les frontières de `features/`, `outcomes/` et `research/` sont stables ;
- les identités Market/Candle/Event/Occurrence/Context/Outcome/Experiment sont suffisamment stables pour que des implémentations indépendantes convergent ;
- les conventions d'outcome et de baseline sont explicites ;
- les politiques de gaps, révisions et timeframes natifs des données de marché sont explicites ;
- le rôle des dépendances est documenté ;
- le journal de décisions D-001 à D-020 est explicitement approuvé ;
- aucune question bloquante ne subsiste.

## Statut de validation

`P0 — VALIDATED`

Les audits finaux indépendants de la v7 ont conclu `P0 — VALIDATION READY`, et D-001 à D-020 ont été explicitement approuvées par l'utilisateur le 6 septembre 2026.

## Règle

P1 est autorisé à démarrer à partir de ce contrat P0 validé. Toute modification sémantique d'une décision P0 validée exige une nouvelle décision explicite et versionnée ; elle ne doit jamais réécrire silencieusement l'historique de P0.
