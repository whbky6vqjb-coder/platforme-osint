# Platforme OSINT

Plateforme automatisée de détection d'infrastructures et d'investigation OSINT, avec orchestration distribuée sur 6 machines Kaggle.

## Architecture

- **OpenClaw Orchestrator**: Planification multi-agents et exécution parallèle de 200 outils OSINT
- **Moteur de Raisonnement**: Analyse de corrélation, pivoting et triangulation de preuves
- **Interface Web**: Dashboard temps réel avec visualisation graphique des entités
- **200 Outils OSINT**: Organisés en 10 catégories avec adaptateurs standardisés
- **Déploiement Distribué**: 6 machines Kaggle avec coordination d'état via HuggingFace Dataset

## Catégories d'Outils OSINT

1. **Corporate** (1-25): Registres d'entreprises, sociétés & paradis fiscaux
2. **Sanctions** (26-48): Sanctions internationales, PEP & conformité
3. **Géolocalisation** (49-72): ADINT, cartographie & géolocalisation GPS
4. **Fuites** (73-95): Data leaks & fuites de données sensibles
5. **Cyber** (96-125): Cyber-infrastructures, DNS & Threat Intel
6. **Digital** (126-155): Empreinte numérique, mails & réseaux sociaux
7. **Blockchain** (156-175): Blockchain, crypto-traçabilité & Web3
8. **Médias** (176-188): Vérification médias, deepfakes & fact-checking
9. **Legal** (189-200): Registres de brevets & jurisprudence
10. **Ghost** (Détection): Projets fantômes & infrastructures cachées

## Déploiement

### GitHub Actions (recommandé)

Le workflow s'exécute automatiquement toutes les 5 minutes pour coordonner les 6 machines Kaggle :
- Déchiffrement des secrets via SOPS + Age
- Gestion des sessions avec circuit breaker et retry
- Monitoring et nettoyage des sessions stale

### Configuration

Édite `config/platform.yaml` pour configurer :
- Modèle LLM et paramètres
- Clés API des outils OSINT
- Paramètres de coordination Kaggle
- Configuration ngrok pour les endpoints persistants

## Fonctionnalités Clés

- Recherche multi-vectorielle sur 200 outils OSINT
- Corrélation automatique d'entités et pivoting
- Matrice de confiance par faisceau de preuves triangulées
- Génération de rapports d'investigation automatiques
- Détection d'infrastructures fantômes (datacenters, usines, hubs logistiques)
- Gestion d'investigations longues (13h+) avec fenêtre glissante et compression de contexte