# Leçons de BTC Analytics V1

La V1 ne doit pas être considérée comme un échec. Elle a servi de prototype permettant d'identifier des invariants importants pour la V2.

## Ce qui doit être conservé conceptuellement

### Causalité explicite

Un phénomène physique peut appartenir à une bougie T sans être connaissable à T.

La V2 doit séparer `event_time` / `pivot_time` du moment `confirmed_at` / `known_at`.

### Analyse prospective séparée de la détection

La détection ne doit jamais utiliser le futur. Les outcomes futurs peuvent utiliser le futur uniquement après qu'une occurrence a été figée comme connue à T.

### Backend comme source analytique

Le frontend ne recalcule pas la logique analytique.

### Inspection visuelle indispensable

Une métrique ou un score ne suffit pas à valider une représentation structurelle.

### Les figures chartistes sont subjectives

La V2 privilégie les swings, amplitudes, durées, retracements, pentes, compressions/expansions et HH/HL/LH/LL. Les figures chartistes deviennent optionnelles.

## Ce qui doit être évité

- introduire une feature simplement parce qu'elle est populaire en analyse technique ;
- calibrer des seuils avant de prouver l'utilité d'une représentation ;
- mélanger code de recherche et code de production ;
- laisser un fournisseur de données imposer ses objets au domaine ;
- ajouter trop tôt des couches UI ou des abstractions sophistiquées ;
- optimiser avant profiling ;
- utiliser une méthode offline comme si elle était causale ;
- transformer le projet en moteur de stratégie/backtest.

## V1 figée

Dernier jalon de référence : `p8b-pattern-calibration-frontend`.

La V1 peut être consultée pour comparer les résultats, pas comme base de code de la V2.
