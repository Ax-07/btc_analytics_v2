# 10 — Journal de décisions — P0 validé

> Traduction documentaire non sémantique du journal P0 validé. Le texte historique exact approuvé reste figé dans le tag `p0-foundation-v7` au commit `a055c5f386ce328cb46d57908cf26ea9ddff4255`.

Politique : D-001 à D-020 ont été explicitement approuvées par l'utilisateur le 6 septembre 2026 et sont désormais des décisions historiques validées, à ajouts uniquement (append-only). Toute future modification sémantique exige une nouvelle décision explicite et versionnée et ne doit jamais réécrire silencieusement ces entrées.

| ID | Décision validée | Statut |
|---|---|---|
| D-001 | V2 est un repository greenfield ; le code de la V1 n'est pas migré automatiquement. | VALIDATED — USER APPROVED 2026-09-06 |
| D-002 | Le périmètre produit est l'analyse, pas le trading, la gestion de portefeuille, l'exécution d'ordres ou de stratégies. | VALIDATED — USER APPROVED 2026-09-06 |
| D-003 | Causalité stricte : aucun artefact déclaré connu à T ne peut utiliser d'information postérieure à T. | VALIDATED — USER APPROVED 2026-09-06 |
| D-004 | CCXT est l'implémentation initiale d'accès aux exchanges derrière une abstraction interne `MarketDataProvider`. | VALIDATED — USER APPROVED 2026-09-06 |
| D-005 | PostgreSQL est le stockage produit canonique courant ; les snapshots Parquet immuables servent la recherche reproductible ; DuckDB interroge ces snapshots. | VALIDATED — USER APPROVED 2026-09-06 |
| D-006 | Polars est le moteur dataframe principal ; NumPy/SciPy fournissent les primitives numériques/scientifiques. | VALIDATED — USER APPROVED 2026-09-06 |
| D-007 | Les fonctions TA-Lib sélectionnées peuvent être ADOPTées uniquement derrière des adaptateurs après validation causale/golden fonction par fonction ; TA-Lib peut aussi servir de REFERENCE. | VALIDATED — USER APPROVED 2026-09-06 |
| D-008 | VectorBT est une source d'inspiration RESEARCH/REFERENCE ; son moteur de portefeuille/trading n'est pas une dépendance produit. | VALIDATED — USER APPROVED 2026-09-06 |
| D-009 | Les configurations de chandeliers sont des événements analytiques, jamais des signaux de trading. | VALIDATED — USER APPROVED 2026-09-06 |
| D-010 | Les figures chartistes sont une interprétation optionnelle au-dessus de la structure de marché et exigent une valeur incrémentale démontrée. | VALIDATED — USER APPROVED 2026-09-06 |
| D-011 | L'intervalle de Candle canonique est `[open_time,end_time)` UTC ; en analytique closed-bar `available_at=end_time` ; `ingested_at` est une provenance technique. | VALIDATED — USER APPROVED 2026-09-06 |
| D-012 | Les analyses canoniques P0–P8 fonctionnent à la cadence des bougies clôturées ; une sémantique intrabar exige un futur contrat explicite. | VALIDATED — USER APPROVED 2026-09-06 |
| D-013 | Le prix de base d'un Outcome est la clôture de la bougie d'ancrage ; l'horizon H utilise les H prochaines bougies complètes en excluant la bougie d'ancrage. | VALIDATED — USER APPROVED 2026-09-06 |
| D-014 | Chaque ExperimentRun comparatif fige une BaselineDefinition explicite. | VALIDATED — USER APPROVED 2026-09-06 |
| D-015 | Les timeframes P1 `1h`/`4h`/`1d` sont récupérés nativement ; aucun resampling canonique ; les gaps sont des frontières dures de continuité. | VALIDATED — USER APPROVED 2026-09-06 |
| D-016 | Les corrections de bougies source sont auditées ; la reproductibilité des expériences utilise des DatasetSnapshots immuables. | VALIDATED — USER APPROVED 2026-09-06 |
| D-017 | Pyright est le type checker Python de V2. | VALIDATED — USER APPROVED 2026-09-06 |
| D-018 | Les définitions causales de contextes basiques passent en P5 ; P8 couvre les contextes avancés et régimes. | VALIDATED — USER APPROVED 2026-09-06 |
| D-019 | Les identités analytiques déterministes utilisent des paramètres normalisés par schéma, la sérialisation RFC 8785 JCS et des fingerprints SHA-256 en hexadécimal minuscule ; `occurrence_key.v1` utilise le payload canonique exact défini dans le modèle de domaine. | VALIDATED — USER APPROVED 2026-09-06 |
| D-020 | Chaque bougie clôturée canonique possède une lignée de révisions à ajouts uniquement (append-only) : la première ingestion valide crée `revision_seq = 1` comme `accepted_current` avec `observed_at` et `accepted_at` ; chaque observation distincte ultérieure alloue le prochain `revision_seq` lors de la création de la candidate et est persistée comme `pending_confirmation` avant confirmation native. Les révisions en attente n'ont pas d'`accepted_at`, ne sont jamais éligibles au PIT, survivent à une interruption sans acceptation implicite et sont sérialisées à au plus une candidate en attente non résolue par lignée de bougie. Les bougies acceptées modifiées sont confirmées contre l'endpoint natif faisant autorité de la même venue ; un accord fait passer la même révision en attente à `accepted_current` et supersède la précédente révision courante, tandis qu'un désaccord, une indisponibilité ou un échec de validation la fait passer à `quarantined` sans renumérotation. Les révisions acceptées satisfont `observed_at <= accepted_at` ; `observed_point_in_time` sélectionne uniquement la dernière révision acceptée dont `accepted_at <= T` ; les snapshots ne prétendent jamais rétroactivement qu'une correction tardive a été observée ou acceptée au T historique. | VALIDATED — USER APPROVED 2026-09-06 |
