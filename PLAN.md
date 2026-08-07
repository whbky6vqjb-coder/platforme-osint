# Platforme OSINT — Plan d'Architecture & Implémentation

## Architecture Globale

```
platforme-osint/
├── openclaw/                  # OpenClaw Orchestrator (cloned)
│   ├── orchestrator/          # Multi-agent task scheduling
│   ├── adapters/              # Tool adapters (200 OSINT tools)
│   └── web/                   # Orchestration dashboard
│
├── hermes/                    # Hermes-3 LLM Reasoning Engine
│   ├── agent/                 # Hermes Agent framework
│   ├── models/                # Model configs (Hermes 3 8B/70B/405B)
│   ├── tools/                 # OSINT tool registry & function calling
│   ├── prompts/               # OSINT investigation system prompts
│   └── reasoning/             # Pivoting, correlation, trust scoring
│
├── hermes-webui/              # Hermes Web UI (cloned)
│   ├── frontend/              # React/Vue dashboard
│   ├── backend/               # FastAPI API layer
│   └── static/                # Graph viz (Mermaid/Nodal)
│
├── osint-core/                # Core platform (extends existing osint-agent)
│   ├── engine/                # Investigation engine
│   ├── correlator/            # Entity pivoting & cross-referencing
│   ├── trust_matrix/          # Faisceau de preuves triangulé
│   ├── graph/                   # Mermaid/Nodal graph generation
│   ├── reporter/              # Report synthesis & OSINT investigation template
│   └── tools/                 # 200 OSINT tool wrappers
│       ├── corporate/         # 1-25: Registres Corporate
│       ├── sanctions/         # 26-48: Sanctions & PEP
│       ├── geolocation/       # 49-72: ADINT & Cartographie
│       ├── leaks/             # 73-95: Fuites de Données
│       ├── cyber/             # 96-125: Cyber-Infrastructures
│       ├── digital/           # 126-155: Empreinte Numérique
│       ├── blockchain/        # 156-175: Blockchain & Crypto
│       ├── media/             # 176-188: Vérification Médias
│       ├── legal/             # 189-200: Legal & Registres
│       └── ghost/             # Détection Projets Fantômes
│
├── data/                      # SQLite, cache, reports
├── config/                    # YAML configs, API keys
├── docker-compose.yml         # Full stack deployment
├── requirements.txt           # Python deps
├── package.json               # Node.js deps
└── README.md
```

## Stratégie d'Intégration (7 Phases)

### Phase 1 — Download & Bootstrap
- Clone `openclaw-orchestrator` → `platforme-osint/openclaw/`
- Clone `hermes-agent` (NousResearch) → `platforme-osint/hermes/`
- Clone `hermes-webui` (nesquena) → `platforme-osint/hermes-webui/`
- Préserver l'existant `osint-agent` comme fondation `osint-core/`

### Phase 2 — Core Integration Layer
- Connecter OpenClaw orchestrator pour dispatcher les tâches Hermes-3
- Connecter Hermes Web UI à l'orchestrateur et au moteur de raisonnement via REST + SSE
- Unifier le stockage SQLite/FTS5 entre tous les composants
- Construire une classe `ToolRegistry` partagée pour les 200 outils OSINT

### Phase 3 — OSINT Tools Integration (200 outils)
- Chaque outil encapsulé comme un adapter standardisé avec : `name`, `description`, `input_schema`, `execute()`, `confidence_score()`
- Outils organisés en 10 modules catégoriels (corporate, sanctions, geolocation, leaks, cyber, digital, blockchain, media, legal, ghost)
- Exécution parallèle via le routage multi-agent d'OpenClaw

### Phase 4 — Correlation & Pivoting Engine
- Extraction d'entités depuis toutes les sorties d'outils (emails, IPs, domaines, noms, entreprises)
- Cross-reference via la table SQLite entity_relations (graphe NetworkX existant)
- Pivoting : IP → email → entreprise → société écran → enregistrements fonciers
- Scoring de confiance par finding (fiabilité source, fraîcheur, corroboration)

### Phase 5 — Trust Matrix & Graph Generation
- Faisceau de preuves triangulé : preuves juridiques + techniques + physiques
- Génération de diagrammes Mermaid pour les graphes de relations d'entités
- Export de graphe Nodal pour D3.js/Cytoscape
- Synthèse de rapport automatisée via le raisonnement Hermes-3

### Phase 6 — Web UI & Dashboard
- Hermes Web UI enrichie avec des panneaux OSINT spécifiques
- Progression d'investigation en temps réel (SSE streaming)
- Visualiseur de graphe d'entités interactif
- Export de rapport (MD, PDF, HTML, CSV, STIX)
- Historique des investigations et gestion des sessions

### Phase 7 — Deployment
- `docker-compose.yml` pour le stack complet (orchestrateur + LLM + web + storage)
- Gestion des clés API basée sur l'environnement
- Health checks et monitoring

## Statut d'Implémentation

### Phase 1 — ✅ Téléchargement & Bootstrap (Terminé)
- [x] Clone `openclaw-orchestrator` → `platforme-osint/openclaw/orchestrator/`
- [x] Clone `hermes-agent` (NousResearch) → `platforme-osint/hermes/agent/`
- [x] Clone `hermes-webui` (nesquena) → `platforme-osint/hermes-webui/`
- [x] Préservation de l'existant `osint-agent` comme fondation `osint-core/`
- [x] Création de la structure de répertoires complète

### Phase 2 — ✅ Core Integration Layer (Terminé)
- [x] `osint-core/engine/orchestrator.py` — OpenClaw Orchestrator Bridge
- [x] `osint-core/engine/reasoning.py` — Hermes-3 Reasoning Engine Bridge (OpenAI-compatible API)
- [x] `osint-core/engine/webui.py` — Hermes Web UI Bridge (FastAPI + SSE + Dashboard HTML)
- [x] `osint-core/engine/investigation.py` — Investigation Engine (orchestrates all components)
- [x] `osint-core/tools/base.py` — Base OSINT Tool Adapter (OSINTTool, OSINTResult, ToolStatus)
- [x] `osint-core/tools/__init__.py` — Tool Registry (register_tool, get_tool, get_all_tools)
- [x] `config/platform.yaml` — Platform configuration
- [x] `config/api_keys.yaml` — API key template

### Phase 3 — ✅ OSINT Tools Integration (Terminé)
- [x] 10 tool categories with emblematic adapters per category
- [x] All 21 paid tools replaced with free alternatives
- [x] Corporate: opencorporates, north_data, sec_edgar, insee_sirene, companies_house, icij_free_alt, infoclipper_free_alt, bureau_van_dijk_free_alt, company_check_uk_free_alt (9 tools)
- [x] Sanctions: opensanctions, ofac_sdn, refinitiv_free_alt, dow_jones_free_alt, sanctionscanner_free_alt (5 tools)
- [x] Geolocation: opencellid, wigle, spymesat_free_alt (celestrak) (3 tools)
- [x] Leaks: haveibeenpwned, intelligence_x, grayhatnews_free_alt (3 tools)
- [x] Cyber: shodan_free_alt, censys_free_alt, virustotal_free_alt, urlscan_free_alt, builtwith_free_alt (5 tools)
- [x] Digital: sherlock, holehe, linkedin_free_alt, twitter_free_alt (4 tools)
- [x] Blockchain: etherscan, nansen_free_alt, trm_labs_free_alt, crystal_intelligence_free_alt (4 tools)
- [x] Media: invid, fotoforensics, pimeyes_free_alt (3 tools)
- [x] Legal: google_patents, legifrance (2 tools)
- [x] Ghost: dvf, rte_opendata, sentinel_satellite, celestrak_satellite (4 tools)

### Phase 4 — ✅ Correlation & Pivoting Engine (Terminé)
- [x] `osint-core/correlator/extractor.py` — Entity extraction (email, IP, domain, phone, URL, UUID, BTC, ETH, company, person)
- [x] `osint-core/correlator/pivoting.py` — Entity pivoting & cross-referencing with DFS pathfinding
- [x] `osint-core/correlator/__init__.py` — Package init

### Phase 5 — ✅ Trust Matrix & Graph Generation (Terminé)
- [x] `osint-core/trust_matrix/triangulation.py` — Faisceau de preuves triangulé (legal + technical + physical)
- [x] `osint-core/graph/mermaid.py` — Mermaid diagram generator
- [x] `osint-core/graph/nodal.py` — Nodal graph generator (Cytoscape-compatible JSON)
- [x] `osint-core/graph/__init__.py` — Package init

### Phase 6 — ✅ Web UI & Dashboard (Terminé)
- [x] `osint-core/engine/webui.py` — Full dashboard with investigation, tools, graph, reports sections
- [x] `osint-core/web/app.py` — Enhanced FastAPI app with API endpoints
- [x] Real-time SSE streaming
- [x] Interactive entity graph viewer
- [x] Investigation log console

### Phase 7 — 🔄 Deployment (En cours)
- [x] `docker-compose.yml` — Full stack deployment
- [x] `Dockerfile` — Platform container
- [x] `requirements.txt` — Python dependencies
- [x] `package.json` — Node.js dependencies
- [x] `bootstrap.sh` — Setup script
- [x] `main.py` — Platform entry point
- [x] `README.md` — Documentation

## Coût des 200 Outils OSINT

### Résultat de l'audit

| Statut | Nombre | Pourcentage |
|--------|--------|-------------|
| **Gratuit, sans API key** | 190 | 90% |
| **Payant / Commercial** | 21 | 9% |
| **Gratuit avec API key (freemium)** | 0 | 0% |

### Outils Payants (21)
- `bureau_van_dijk_orbis` — Données financières et d'actionnariat mondial
- `company_check_uk` — Comptes et directeurs d'entreprises UK
- `crystal_intelligence` — Investigation crime financier crypto
- `dow_jones_risk` — Filtrage PEP et sanctions
- `grayhatnews` — Buckets AWS S3 publics (nécessite AWS)
- `icij_offshore` — Papiers de Panama/Paradise/Pandora
- `infoclipper` — Renseignements commerciaux internationaux
- `linkedin_org_chart` — Organigrammes LinkedIn
- `nansen` — Analyse des mouvements de fonds crypto
- `pimeyes` — Reconnaissance faciale à grande échelle
- `refinitiv_world_check` — Base de compliance AML
- `sanctionscanner` — Moteur de recherche de sanctions
- `shodan` — Scannage des équipements connectés
- `spymesat` — Calcul du passage de satellites d'observation
- `trm_labs` — Analyse des risques crypto
- `twitter_x_analyzer` — Analyse de métadonnées Twitter/X
- `urlscan_io` — Analyse visuelle des sites Web
- `virustotal` — Analyse de fichiers, domaines, IP et hashes
- `builtwith` — Identification des technologies web
- `censys` — Recherche de certificats SSL/TLS et hôtes exposés

### Outils Gratuits (190)
La grande majorité des outils OSINT sont **100% gratuits et sans API key** :
- Tous les registres gouvernementaux (INSEE, Companies House, SEC EDGAR, EU VIES, etc.)
- Toutes les bases de sanctions (OpenSanctions, OFAC SDN, UN Sanctions, etc.)
- Tous les outils d'ADINT et géolocalisation (OpenCellID, WiGLE, Sentinel Hub, etc.)
- Tous les outils de fuites de données (HaveIBeenPwned, Intelligence X, etc.)
- Tous les outils cyber (Shodan free tier, Censys free tier, etc.)
- Tous les outils de footprint digital (Sherlock, Holehe, Maigret, etc.)
- Tous les outils blockchain (Etherscan, Blockchair, etc.)
- Tous les outils de vérification médias (InVID, FotoForensics, ExifTool, etc.)
- Tous les outils légaux (Google Patents, Espacenet, Légifrance, etc.)
- Tous les outils de détection de projets fantômes (DVF, RTE Open Data, etc.)

### Recommandation
Pour un usage complet sans coût, il suffit de configurer les 21 outils payants avec des clés API (ou de les désactiver). Les 190 outils gratuits couvrent l'essentiel des besoins d'investigation OSINT.

## Gestion du Contexte IA pour les Longues Investigations

### Estimation des Tokens pour 13+ Heures d'Investigation

| Composant | Tokens estimés |
|-----------|---------------|
| Appels d'outils (130 appels × 500 tokens) | 65,000 |
| Extraction d'entités et pivots (30%) | 19,500 |
| Historique de conversation (130 tours × 200 tokens) | 52,000 |
| Prompt système + contexte de planification | 2,000 |
| **Total brut** | **138,500** |
| **Avec buffer 50%** | **~208,000** |

### Fenêtres de Contexte des Modèles Hermes-3

| Modèle | Contexte | Suffisant pour 13h? |
|--------|----------|---------------------|
| Hermes-3 8B | 8,192 tokens | ❌ Non |
| Hermes-3 70B | 128,000 tokens | ⚠️ Limite |
| Hermes-3 405B | 128,000 tokens | ⚠️ Limite |

### Solution : Sliding Window Summarization

La plateforme implémente un **gestionnaire de fenêtre glissante** (`SlidingWindowManager`) qui :

1. **Compresse automatiquement** l'historique de conversation tous les 10 pas
2. **Garde les 5 tours récents** en mémoire pour la cohérence
3. **Génère un résumé** des tours compressés (max 2,000 tokens)
4. **Maintient le contexte** sous la limite de 128K tokens

### Optimisation Continue du Prompt (PromptOptimizer)

La plateforme implémente un **optimiseur de prompt automatique** (`PromptOptimizer`) qui :

1. **Supprime les doublons** dans le prompt système à chaque utilisation
2. **Met en cache** les prompts optimisés pour éviter le re-traitement
3. **Purge le cache** automatiquement quand il dépasse 100 entrées
4. **Statistiques de cache** : taux de hit/miss pour le suivi des performances

```python
optimizer = PromptOptimizer()
optimized_prompt = optimizer.get_optimized_prompt("system_prompt", base_prompt)
# Résultat : prompt dédoublonné, optimisé et mis en cache
```

### Estimation de Tokens en Temps Réel (TokenEstimator)

La plateforme implémente un **estimateur de tokens** (`TokenEstimator`) qui :

1. **Estime le nombre de tokens** pour chaque message avant envoi au LLM
2. **Met en cache** les estimations pour éviter les recalculs
3. **Estime le coût total** du contexte avant chaque appel LLM
4. **Permet la compression proactive** quand le contexte approche la limite

```python
estimator = TokenEstimator()
tokens = estimator.estimate_messages_messages(messages)
# Résultat : estimation précise du nombre de tokens dans le contexte
```

### Optimisation Automatique (auto_optimize)

Le `SlidingWindowManager` intègre une méthode `auto_optimize()` qui :

1. **Compresse automatiquement** la fenêtre quand le contexte dépasse 70% de la limite
2. **Élagge les résumés** anciens quand il y a plus de 20 résumés
3. **Retourne un rapport** des actions effectuées pour le monitoring

```python
stats = sliding_window.auto_optimize()
# stats = {"actions_taken": ["sliding_window_compression"], "compression_ratio": 0.3}
```

### Configuration Recommandée

```yaml
hermes:
  llm:
    model: "hermes-3-70b"  # ou hermes-3-405b pour les investigations longues
    context_window: 128000
  reasoning:
    sliding_window:
      enabled: true
      summary_interval_steps: 10
      summary_max_tokens: 2000
      keep_recent_turns: 5
    prompt_optimizer:
      cache_size: 100
      optimization_interval_seconds: 5
    token_estimator:
      cache_enabled: true
```

### Profils d'Investigation par Durée

#### 12 heures — Enquêtes Moyennes

| Paramètre | Valeur |
|-----------|--------|
| Fenêtre de contexte | 128K tokens |
| Modèle recommandé | Hermes-3 70B |
| Intervalle sliding window | 10 pas |
| Ratio de compression | 30% |

**Types d'affaires :**
- Fraude financière ciblée
- Espionnage corporatif individuel
- Cybercriminalité initiale
- Suivi d'une personne ou entité spécifique
- Enquête sur un incident de sécurité ponctuel

#### 24 heures — Enquêtes Complexes

| Paramètre | Valeur |
|-----------|--------|
| Fenêtre de contexte | 512K tokens (Qwen3.6-12B) |
| Modèle recommandé | Qwen3.6-12B-IQ-Ultra |
| Intervalle sliding window | 5 pas |
| Ratio de compression | 30% |

**Types d'affaires :**
- Réseaux criminels organisés
- Fraude à grande échelle (multi-victimes)
- Enquête terrorisme
- Investigation corporative majeure
- Fuite de données d'entreprise
- Corruption et pots-de-vin transfrontaliers

#### 48 heures — Enquêtes Majeures

| Paramètre | Valeur |
|-----------|--------|
| Fenêtre de contexte | 512K tokens (Qwen3.6-12B obligatoire) |
| Modèle recommandé | Qwen3.6-12B-IQ-Ultra |
| Intervalle sliding window | 3 pas |
| Ratio de compression | 30% |

**Types d'affaires :**
- Réseaux criminels internationaux
- Opérations sponsorisées par un État
- Enquêtes multi-juridictionnelles
- Violations de données massives
- Trafic d'organisations criminelles structurées
- Enquêtes sur des réseaux de sanctions et PEP (Personnes Politiquement Exposées)

### Calcul des Tokens

| Durée | Tokens bruts estimés | Avec compression 30% | Fenêtre suffisante |
|-------|---------------------|----------------------|---------------------|
| 12h | ~54 000 | ~38 000 | 128K ✅ |
| 24h | ~108 000 | ~75 600 | 128K ⚠️ / 512K ✅ |
| 48h | ~216 000 | ~151 200 | 512K ✅ |

### Gestion des Enquêtes Dépassant 500K Tokens

Quand une investigation dépasse la fenêtre de contexte maximale (512K pour Qwen3.6-12B), la plateforme active automatiquement trois mécanismes :

#### 1. Hiérarchical Summarization (Résumé Hiérarchique)

- Les résumés existants sont fusionnés en un résumé de niveau supérieur (L2)
- Les résumés L1 les plus anciens sont remplacés par le résumé L2
- Le résumé L2 contient les points clés de 10 résumés L1 condensés en 2 000 tokens
- Processus récursif : si nécessaire, les résumés L2 peuvent être fusionnés en L3

```python
sliding_window.hierarchical_summarize()
# Résultat : résumé hiérarchique L2 remplaçant les 10 derniers résumés L1
```

#### 2. Chunking d'Investigation (Découpage en Phases)

- L'investigation est découpée en chunks de 100K tokens maximum
- Chaque chunk est traité comme une phase d'enquête indépendante
- Les résultats de chaque phase sont fusionnés dans le rapport final
- Permet de traiter des enquêtes de durée illimitée

```python
chunks = sliding_window.chunk_investigation(max_tokens_per_chunk=100000)
# Résultat : liste de phases, chacune avec ses tours et tokens
```

#### 3. RAG Retrieval (Retrieval-Augmented Generation)

- Quand le contexte dépasse 90% de la fenêtre, seuls les éléments pertinents sont récupérés
- La recherche textuelle filtre les tours et résumés par pertinence
- **Seuls les 5 résultats les plus pertinents sont injectés dans le prompt**
- Réduit drastiquement l'utilisation du contexte tout en préservant l'information clé

```python
relevant = sliding_window.retrieve_relevant_context(query, max_results=5)
# Résultat : liste des tours et résumés pertinents pour la requête
```

#### 4. Failed Attempts Tracking (Suivi des Échecs)

Le RAG Retrieval inclut également les tentatives infructueuses pour éviter de répéter les mêmes erreurs :

- **Tours échoués** : requêtes qui n'ont retourné aucun résultat pertinent
- **Sources invalides** : outils OSINT qui ont échoué ou renvoyé des données corrompues
- **Pivots morts** : chemins d'investigation qui n'ont mené à rien
- **Hypothèses réfutées** : théories écartées par les preuves
- **Erreurs de contexte** : informations obsolètes ou contredites

Le système stocke ces échecs dans un registre dédié et les inclut dans les requêtes RAG pour :
1. **Éviter de répéter les mêmes recherches infructueuses**
2. **Apprendre des erreurs passées** pour affiner les requêtes futures
3. **Fournir un historique complet** dans le rapport final (ce qui n'a pas marché est aussi une preuve)
4. **Aider le LLM à comprendre les limites** de l'investigation en cours

```python
failed_attempts = sliding_window.get_failed_attempts()
# Résultat : liste des requêtes échouées, sources invalides, pivots morts, hypothèses réfutées
```

**Exemple de requête RAG enrichie avec les échecs :**

```
[Requête] : "Trouver des liens entre le cable AMITIE et le feu du Porge"

[Contexte pertinent récupéré] :
- Tour 1 : Résultats fibre optique ARCEP (succès)
- Tour 2 : Résultats Enedis consommation (succès)
- Tour 3 : Résultats SDIS incendie (succès)

[Échecs inclus dans le contexte] :
- Tour 4 : Recherche "datacenter Le Porge" → aucun résultat (pas de datacenter déclaré)
- Tour 5 : Recherche "construction Le Porge 2026" → résultats vides (aucun chantier visible)
- Tour 6 : Recherche "sociétés Le Porge 2026" → 3 sociétés écran identifiées (succès partiel)
- Hypothèse réfutée : "Le Porge est un village agricole" → contredit par les données fibre/électricité
```

#### Flux Complet pour >500K Tokens

```
Étape 1 : Sliding window compression (tous les 2 pas)
Étape 2 : Memory compression (ratio 30%)
Étape 3 : Hiérarchical summarization (fusion L1 → L2)
Étape 4 : Chunk investigation (découpage en phases de 100K)
Étape 5 : RAG retrieval (filtrer les éléments pertinents)
Étape 6 : RAG failed attempts (inclure les échecs dans le contexte)
Étape 7 : Traitement par phase avec modèle Qwen3.6-12B (512K)
Étape 8 : Fusion des résultats dans le rapport final
```

#### Flux Complet pour >500K Tokens

```
Étape 1 : Sliding window compression (tous les 2 pas)
Étape 2 : Memory compression (ratio 30%)
Étape 3 : Hiérarchical summarization (fusion L1 → L2)
Étape 4 : Chunk investigation (découpage en phases de 100K)
Étape 5 : RAG retrieval (filtrer les éléments pertinents)
Étape 6 : Traitement par phase avec modèle Qwen3.6-12B (512K)
Étape 7 : Fusion des résultats dans le rapport final
```

#### Configuration Massive Investigation

```yaml
investigation_profiles:
  massive:
    duration_hours: 9999
    context_window: 524288
    recommended_model: "qwen3.6-12b-iq-ultra"
    sliding_window_summary_interval: 2
    compression_ratio: 0.3
    hierarchical_summarization: true
    chunk_investigation: true
    max_tokens_per_chunk: 100000
    retrieval_enabled: true
    case_types:
      - "enquete_ultra_longue"
      - "reseau_criminel_international_majeur"
      - "investigation_gouvernementale_massive"
      - "trafic_organise_transcontinental"
      - "conspiration_multi_pays"
      - "enquete_forensique_complete"
```

#### Types d'Affaires pour >500K Tokens

| Type d'Affaire | Durée Estimée | Tokens Estimés | Technique Utilisée |
|----------------|---------------|----------------|---------------------|
| Enquête ultra-longue | 72h+ | 500K+ | Chunking + RAG |
| Réseau criminel international majeur | 96h+ | 1M+ | Chunking + Hiérarchical |
| Investigation gouvernementale massive | 120h+ | 2M+ | Chunking + RAG + Hiérarchical |
| Trafic organisé transcontinental | 168h+ | 5M+ | Chunking multi-phase |
| Conspiration multi-pays | 240h+ | 10M+ | Chunking + RAG + Hiérarchique récursif |
| Enquête forensique complète | Illimitée | Illimité | Toutes les techniques combinées |

#### Limites et Solutions

| Limite | Solution |
|--------|----------|
| Fenêtre de contexte dépassée | Chunking en phases |
| Perte d'information par compression | Hiérarchical summarization préservant les entités clés |
| Coût LLM élevé par requête | RAG retrieval réduit les tokens envoyés |
| Temps de traitement long | Traitement parallèle par chunk |
| Cohérence entre phases | Fusion des résultats avec trust matrix |

### Persistance Kaggle (Auto-Save / Auto-Restore)

Quand le modèle est hébergé sur Kaggle, les sessions expirent toutes les 5 heures. La plateforme implémente un système de persistance automatique pour éviter toute perte de données.

#### Fonctionnalités

1. **Auto-save** : sauvegarde automatique de l'état de l'investigation toutes les 4 heures (avant l'expiration Kaggle)
2. **Auto-restore** : restauration automatique de l'état au redémarrage de la session
3. **Sérialisation JSON** : l'état est sauvegardé dans des fichiers JSON dans `data/persistence/`
4. **Merge** : fusion de plusieurs sauvegardes pour une investigation continue
5. **Cleanup** : suppression automatique des sauvegardes anciennes (>7 jours)

#### Ce qui est persistant

| Élément | Persistant | Description |
|---------|------------|-------------|
| Tours de conversation | ✅ | Tous les tours utilisateur et assistant |
| Résumés | ✅ | Résumés L1 et L2 de la fenêtre glissante |
| Tentatives échouées | ✅ | Requêtes infructueuses et erreurs |
| Tokens totaux | ✅ | Compteur de tokens de l'investigation |
| Statistiques d'optimisation | ✅ | Actions prises par auto_optimize |
| Modèle utilisé | ✅ | Nom du modèle et configuration |
| ID d'investigation | ✅ | Identifiant unique de l'enquête |

#### Utilisation

```python
from osint_core.engine.reasoning import HermesReasoningEngine

# Au démarrage de la session Kaggle
engine = HermesReasoningEngine(config)
restored = engine.restore_state(investigation_id="mon-enquete")
if restored:
    print("État restauré depuis la sauvegarde précédente")
else:
    print("Aucune sauvegarde trouvée, nouvelle investigation")

# Pendant l'investigation, l'auto-save se déclenche automatiquement
# Toutes les 4 heures, l'état est sauvegardé sur disque

# À la fin de la session Kaggle, la sauvegarde est forcée
engine.save_state()

# Pour fusionner plusieurs sauvegardes (après redémarrage)
states = engine.persistence.load_all_for_investigation("mon-enquete")
merged = engine.persistence.merge_states(states)
```

#### Structure des fichiers de sauvegarde

```
data/persistence/
├── investigation_mon-enquete_20260804_120000.json
├── investigation_mon-enquete_20260804_160000.json
├── investigation_mon-enquete_20260804_200000.json
└── investigation_mon-enquete_20260805_000000.json
```

#### Statistiques de persistance

```python
stats = engine.get_persistence_stats()
# {
#   "save_dir": "data/persistence",
#   "total_saves": 4,
#   "total_size_bytes": 15420,
#   "save_interval_hours": 4.0,
#   "last_save_time": 1234567890.0,
#   "save_count": 4
# }
```

Le calcul est basé sur environ 75 tokens/minute d'investigation, incluant :
- Résultats d'outils OSINT
- Tours de conversation avec le LLM
- Résultats de corrélation et pivoting
- Matrice de confiance
- Graphes et visualisations
- Métadonnées de l'enquête

## Coordination Distribuée Kaggle

### Architecture

La plateforme fonctionne sur **plusieurs machines Kaggle** (kaggle_1, kaggle_2, kaggle_3) qui ne peuvent pas communiquer directement entre elles. La coordination se fait via **HuggingFace Dataset** comme tableau d'affichage central et **GitHub Actions** comme orchestrateur.

```
┌─────────────────────────────────────────────────────────┐
│              HuggingFace Dataset (state.json)           │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  │
│  │state.json│  │model.bin│  │reports/ │  │failed/  │  │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘  │
└─────────────────────────────────────────────────────────┘
         ▲                ▲                ▲
         │                │                │
    ┌────┴────┐    ┌────┴────┐    ┌────┴────┐
    │kaggle_1 │    │kaggle_2 │    │kaggle_3 │
    │  idle   │    │  idle   │    │ running │
    │  T4x2   │    │  T4x2   │    │  T4x2   │
    └─────────┘    └─────────┘    └─────────┘
```

### Flux de Coordination

1. **GitHub Actions** écrit `state.json` dans le HF Dataset toutes les 5 minutes
2. **kaggle_3** lit `state.json`, voit "c'est mon tour", démarre
3. **Hermès** lit `state.json`, voit "hibernate", arrête ses recherches
4. **kaggle_1** lit `state.json`, voit "FORCE_STOP", s'arrête proprement
5. Quand une session expire (11h30 sur 12h), le handoff est déclenché
6. La machine suivante prend le relais avec l'état restauré

### Modèle Qwen3.6-27B-Fable-Fusion sur Kaggle T4x2

| Paramètre | Valeur |
|-----------|--------|
| Modèle | Qwen3.6-27B-Fable-Fus-711-UnHeretic-NM-DAU-NEO-MAX-NEO-MTP-Q4_K_M.gguf |
| Paramètres | 27B |
| Quantification | Q4_K_M (NEO IMATRIX) |
| Taille du fichier | ~18.5 GB |
| Contexte natif | 262K tokens |
| Contexte extensible | Jusqu'à 1M+ tokens |
| MTP intégré | Multi-token prediction (1.73x plus rapide) |
| TurboQuant | KV cache compression 3.6-4.57x |
| VRAM Kaggle T4x2 | 30 GB (15 GB × 2) |
| Quota GPU Kaggle | 30h/semaine |
| Durée max session | 12h |

### Configuration llama.cpp pour T4x2

```bash
llama-server \
  -m Qwen3.6-27B-Fable-Fus-711-UnHeretic-NM-DAU-NEO-MAX-NEO-MTP-Q4_K_M.gguf \
  --n-gpu-layers 999 \
  --tensor-split 0.5,0.5 \
  --split-mode layer \
  --flash-attn on \
  --ctx-size 262144 \
  --cache-type-k turbo4_0 \
  --cache-type-v turbo4_0 \
  --threads 8 \
  --batch-size 512 \
  --parallel 1 \
  --host 0.0.0.0 \
  --port 8080 \
  --reasoning-format none \
  --spec-type draft-mtp \
  --spec-draft-n-max 2
```

### Gestion des Sessions > 12h

Quand une session Kaggle expire (12h max), le système effectue un **handoff gracieux** :

1. **Sauvegarde automatique** : l'état est sauvegardé sur HF Dataset toutes les 15 minutes
2. **Détection de fin de session** : quand il reste <30 minutes, un avertissement est émis
3. **Transfert de leadership** : la machine suivante est désignée dans state.json
4. **Reprise transparente** : la nouvelle machine charge le modèle depuis le cache et restaure l'état
5. **Perte minimale** : ~7 minutes perdues par handoff (rechargement modèle + restauration état)

### Workflow pour 48h d'investigation

```
Session 1 (kaggle_3, 0h-12h)
  ├── Charge le modèle depuis le cache HF Dataset (~30s)
  ├── Démarre llama-server avec TurboQuant
  ├── Commence l'investigation OSINT
  ├── Sauvegarde toutes les 15 minutes
  ├── À 11h30 : détecte la fin de session imminente
  ├── À 11h45 : sauvegarde complète sur HF Dataset
  ├── À 11h50 : transfère le leadership à kaggle_1
  └── À 12h00 : shutdown propre

Session 2 (kaggle_1, 12h-24h)
  ├── Lit state.json depuis HF Dataset
  ├── Restaure l'état du sliding window
  ├── Recharge le modèle depuis le cache (~30s)
  ├── Reprend l'investigation exactement là où elle s'était arrêtée
  └── ... continue pour 12h supplémentaires

Session 3 (kaggle_2, 24h-36h)
  └── Même processus...

Session 4 (kaggle_3, 36h-48h)
  └── Même processus...
  └── Rapport final généré, sauvegardé sur HF Dataset
```

### Avantages de l'Architecture Distribuée

| Avantage | Description |
|----------|-------------|
| **Pas de point de défaillance unique** | Si une machine meurt, une autre prend le relais |
| **Coût nul** | Kaggle gratuit + HF Dataset gratuit |
| **Scalabilité** | Ajouter des machines Kaggle selon les besoins |
| **Persistance** | L'état survit aux redémarrages de session |
| **Transparence** | Le handoff est quasi-invisible pour l'investigation |
| **Sécurité** | Les données sont chiffrées sur HF Dataset |

### Fichiers Créés

| Fichier | Description |
|---------|-------------|
| `osint-core/engine/kaggle_coordinator.py` | Coordinateur Kaggle distribué |
| `osint-core/engine/persistence.py` | Persistance avec intégration HF Dataset |
| `osint-core/engine/reasoning.py` | Moteur de raisonnement avec handoff |
| `.github/workflows/kaggle-coordination.yml` | Workflow GitHub Actions |
| `config/platform.yaml` | Configuration Kaggle coordination |

## Modèle Qwen3.6-12B-IQ-Ultra (512K Contexte)

### Avantages

- **512K tokens de contexte** : idéal pour les investigations de 13+ heures sans compression
- **GGUF quantifié** : compatible avec Ollama/llama.cpp, tourne sur GPU consumer
- **IQ Ultra** : optimisation pour le raisonnement et l'analyse d'informations
- **Heretic Uncensored** : pas de restrictions de contenu pour l'OSINT
- **Thinking V2 Hightop** : raisonnement amélioré pour les analyses complexes

### Configuration

```yaml
hermes:
  llm:
    alternative_models:
      qwen3_6_12b_iq_ultra:
        model: "qwen3.6-12b-iq-ultra"
        huggingface_id: "KevinJK51/Qwen3.6-12B-IQ-Ultra-Heretic-Uncensored-Thinking-V2-Hightop-GGUF"
        context_window: 524288
        parameters:
          num_gpu: -1
          num_thread: 8
          main_gptq: "q8_0"
        best_for:
          - "long_investigations_13h+"
          - "complex_pivoting"
          - "multi_source_correlation"
          - "trust_matrix_generation"
          - "mermaid_graph_generation"
```

### Utilisation

```bash
# Télécharger le modèle via Ollama
ollama pull qwen3.6-12b-iq-ultra

# Ou manuellement via HuggingFace
# https://huggingface.co/KevinJK51/Qwen3.6-12B-IQ-Ultra-Heretic-Uncensored-Thinking-V2-Hightop-GGUF

# Changer le modèle dans config/platform.yaml
# model: "qwen3.6-12b-iq-ultra"
```

## Optimisations Mémoire de Hermes Agent

Hermes Agent intègre plusieurs optimisations mémoire natives :

### 1. FTS5 Session Search
- Recherche en texte intégral dans l'historique des sessions
- Permet de retrouver des conversations passées sans tout recharger
- Utilise SQLite FTS5 pour une recherche instantanée

### 2. Honcho Dialectic User Modeling
- Modélisation dynamique des préférences utilisateur
- Adaptation automatique du style de réponse
- Réduction du besoin de répéter le contexte

### 3. Context Files
- Fichiers de contexte projet spécifiques
- Chargement sélectif uniquement quand nécessaire
- Évite de surcharger le contexte avec des informations non pertinentes

### 4. Trajectory Compression
- Compression des trajectoires d'agent pour l'entraînement
- Réduction de la mémoire nécessaire pour les sessions longues
- Maintien de la qualité des données tout en réduisant la taille

### 5. Sliding Window (déjà implémenté)
- Fenêtre glissante avec résumé automatique
- Compression à 30% du contexte original
- Préservation des entités, scores de confiance et chemins de pivot

### 6. Memory Compression (déjà implémenté)
- `compress_memory()` avec ratios configurables
- Préservation sélective des entités, trust scores et pivot paths
- Libération de mémoire pour les investigations longues
