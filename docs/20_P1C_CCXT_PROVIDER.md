# P1C — `MarketDataProvider` + adaptateur CCXT Binance

Statut : `VALIDATION READY — VALIDATION UTILISATEUR EN ATTENTE`

P1C implémente la frontière fournisseur déjà décidée en P0. Il ne modifie ni le domaine P1B ni les décisions validées dans `docs/10_DECISIONS.md`.

## Sources canoniques

Ordre appliqué :

1. `docs/10_DECISIONS.md`, notamment D-004, D-011, D-012, D-015 et D-016 ;
2. `docs/05_MARKET_DATA.md` ;
3. `docs/17_DEPENDENCY_ASSESSMENT.md` ;
4. `docs/18_P1A_BACKEND_BOOTSTRAP.md` pour le découpage P1 ;
5. `docs/19_P1B_MARKET_DATA_DOMAIN.md` pour les primitives `Market` et `Timeframe`.

## Contrats P0 appliqués

- CCXT reste derrière notre abstraction interne `MarketDataProvider` ;
- le domaine n'importe aucun type CCXT ;
- fournisseur initial : Binance Spot ;
- symbole fournisseur initial : `BTC/USDC` ;
- timeframes P1 : `1h`, `4h`, `1d`, récupérés nativement ;
- seules des bougies clôturées sont éligibles au chemin analytique P1 ;
- aucun resampling ;
- les gaps ne sont ni inventés ni interpolés ;
- le contrôle croisé CCXT-vs-Binance-native reste requis en P1 mais appartient à P1G.

## Revalidation CCXT — 7 septembre 2026

La dépendance a été recontrôlée avant son ajout effectif au projet :

- version PyPI courante vérifiée : `4.5.77`, publiée le 1er septembre 2026 ;
- licence : MIT ;
- métadonnées Python : Python `>=3.10` ; l’installation et l’exécution locales sous Python 3.14.7 ont confirmé la compatibilité P1C ;
- la documentation CCXT courante expose toujours `fetchOHLCV` / `fetch_ohlcv` ;
- `since` est un timestamp Unix UTC en millisecondes ;
- sans `since`, la plage renvoyée dépend du fournisseur : P1C impose donc un `since` explicite ;
- la dernière bougie retournée peut être incomplète tant qu'elle n'est pas clôturée : l'adaptateur P1C l'exclut ;
- CCXT peut restituer des lacunes si la plateforme n'a pas de bougie pour une période : P1C les préserve et ne les traite pas ;
- décision maintenue : **ADOPT derrière adaptateur**, uniquement pour l'accès public market-data dans ce jalon.

## Architecture P1C

```text
Market/Timeframe canonique
        |
        v
MarketDataProvider
        |
        v
CcxtBinanceMarketDataProvider
        |
        v
CCXT fetch_ohlcv(BTC/USDC, timeframe, since, limit)
        |
        v
ProviderOHLCV
```

`ProviderOHLCV` est un DTO fournisseur interne. Il stabilise la forme de la réponse CCXT et la provenance, mais n'est pas une `Candle` canonique et n'effectue pas la normalisation décimale canonique P1B.

## Choix d'implémentation P1C

1. L'API fournisseur est synchrone, cohérente avec le pipeline batch et la couche SQLAlchemy/Psycopg synchrones retenus en P1A.
2. `MarketDataProvider` est un `Protocol` Python indépendant de CCXT.
3. L'adaptateur reçoit explicitement un mapping `Market -> source_symbol`. Aucun format de `canonical_symbol` n'est inventé.
4. L'instance CCXT Binance utilise `enableRateLimit = True` et `defaultType = "spot"`.
5. `since` est obligatoire et UTC ; `limit` est validé à l’exécution comme entier strictement positif : booléens, flottants, chaînes, zéro et valeurs négatives sont refusés.
6. `request_started_at` est capturé immédiatement avant l'appel fournisseur ; le même `observed_at` est capturé après son retour pour toutes les observations du lot, et `observed_at < request_started_at` est rejeté afin de ne pas produire une provenance temporelle incohérente.
7. Une ligne n'est exposée par `fetch_closed_ohlcv` que si `open_time + durée(timeframe) <= request_started_at`. Ce cutoff conservateur exclut une bougie qui se clôturerait pendant l'appel réseau, car la ligne reçue a pu être lue par l'exchange avant sa clôture.
8. Les erreurs du fournisseur sont encapsulées dans les exceptions internes `MarketDataProviderError` et dérivées.
9. Les lignes malformées sont rejetées ; les gaps, l'ordre et les doublons ne sont pas corrigés silencieusement dans P1C.
10. La dépendance CCXT n'est importée dynamiquement qu'au moment de créer l'implémentation réelle ; les tests unitaires utilisent un faux exchange injecté.

## Hors périmètre P1C

- authentification Binance et endpoints privés ;
- ordres, trading, portefeuille ou stratégies ;
- WebSocket / CCXT Pro ;
- pagination automatique complète d'un historique ;
- retries métier ;
- normalisation en `Decimal` canonique et construction de `Candle` ;
- persistance PostgreSQL ;
- allocation ou transition de `CandleRevision` ;
- traitement des gaps et politique complète de qualité des données ;
- confirmation native Binance des révisions ;
- fixture de parité CCXT-vs-Binance-native de P1G.

## Tests P1C

Les tests unitaires doivent couvrir au minimum :

- mapping de marché configuré ;
- `since` UTC explicite ;
- `limit` entier positif et rejet des booléens ;
- capacité `fetchOHLCV` et timeframe déclaré ;
- passage exact de `symbol/timeframe/since/limit` à CCXT ;
- filtrage d'une bougie encore ouverte, y compris si elle se clôture pendant l'appel réseau ;
- préservation des gaps ;
- rejet d'une ligne malformée ;
- rejet des timestamps/types fournisseur invalides ;
- encapsulation des erreurs CCXT ;
- validation des clocks `request_started_at` / `observed_at` et refus d'une régression temporelle.

Un smoke test réseau public, borné et désactivé par défaut est fourni. Il ne requiert aucune clé API :

```powershell
$env:BTC_ANALYTICS_RUN_BINANCE_INTEGRATION = "1"
uv run pytest -m binance_integration -v
Remove-Item Env:BTC_ANALYTICS_RUN_BINANCE_INTEGRATION
```

Ce test doit être exécuté localement avant de considérer P1C prêt pour validation. La fixture CCXT-vs-Binance-native complète reste P1G.

## Gate local exécuté — 7 septembre 2026

Les contrôles P1C ont été exécutés sur l'environnement local Python 3.14.7 avec PostgreSQL 18.6 actif :

- `uv lock` : résolution réussie de 41 packages, avec `ccxt==4.5.77` ;
- `docker compose -f .\infra\compose.yaml ps` : PostgreSQL `healthy` ;
- `uv run ruff check backend` : `All checks passed!` ;
- `uv run ruff format --check backend` : `14 files already formatted` ;
- `uv run pyright` : `0 errors, 0 warnings, 0 informations`, code de sortie `0` ;
- `uv run pytest` : `54 passed, 1 skipped` ;
- le seul test ignoré par défaut est le smoke Binance protégé par `BTC_ANALYTICS_RUN_BINANCE_INTEGRATION` ;
- le smoke public Binance a été exécuté après le correctif causal `request_started_at` et a terminé avec `1 passed` ; le dernier correctif portant uniquement sur la validation runtime de `limit` n'a pas modifié le chemin réseau ;
- `git diff --check` : aucune erreur de whitespace ; seul l'avertissement Windows LF -> CRLF de `uv.lock` a été observé ;
- la revue Git finale a confirmé exactement les neuf fichiers P1C attendus, incluant `uv.lock`.

Les edge cases finaux couvrent notamment le cutoff causal avant l'appel réseau, la provenance `observed_at`, la validation runtime stricte de `limit`, les types fournisseur invalides et l'absence de fuite de types CCXT vers le domaine.

Ces résultats placent P1C au statut **`VALIDATION READY`**. La validation finale du jalon reste soumise à l'approbation explicite de l'utilisateur après création et revue du commit candidat.
