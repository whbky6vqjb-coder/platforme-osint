# Platforme OSINT

Automated OSINT & Infrastructure Detection Platform integrating OpenClaw (Orchestrator), Hermes-3 (LLM Reasoning Engine), and Hermes Web UI.

## Architecture

- **OpenClaw Orchestrator**: Multi-agent task scheduling and parallel execution
- **Hermes-3 LLM**: AI-driven reasoning, pivoting, and correlation engine
- **Hermes Web UI**: Real-time dashboard with SSE streaming and interactive graph visualization
- **200 OSINT Tools**: Organized across 10 categories with standardized adapters

## Quick Start

### Native Development

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies (for OpenClaw orchestrator)
npm install

# Run the platform
python main.py
```

### Docker Deployment

```bash
docker-compose up -d
```

## Configuration

Edit `config/platform.yaml` to configure:
- LLM provider and model
- API keys for OSINT tools
- Orchestrator settings
- Trust matrix weights

## OSINT Tool Categories

1. **Corporate** (1-25): Registres Corporate, Sociétés & Paradis Fiscaux
2. **Sanctions** (26-48): Sanctions Internationales, PEP & Conformité
3. **Geolocation** (49-72): ADINT, Cartographie & Géolocalisation GPS
4. **Leaks** (73-95): Fuites de Données & Secret Leaks
5. **Cyber** (96-125): Cyber-Infrastructures, DNS & Threat Intel
6. **Digital** (126-155): Empreinte Numérique, Mails & Réseaux Sociaux
7. **Blockchain** (156-175): Blockchain, Crypto-Traçabilité & Web3
8. **Media** (176-188): Vérification Médias, Deepfakes & Fact-Checking
9. **Legal** (189-200): Legal, Registres de Brevets & Jurisprudence
10. **Ghost** (Détection): Projets Fantômes & Infrastructures Cachées

## Key Features

- Multi-vector search across 200 OSINT tools
- Automatic entity correlation and pivoting
- Faisceau de preuves triangulé trust matrix
- Mermaid/Nodal graph generation for entity relationships
- Real-time streaming dashboard
- Automated investigation report generation
- Ghost infrastructure detection (datacenters, usines, hubs logistiques)