# Platforme OSINT - GitHub Setup

## Quick Start

### 1. Encrypt secrets with SOPS

```bash
# Install SOPS and Age
curl -sL https://github.com/getsops/sops/releases/download/v3.8.1/sops_3.8.1_amd64.deb -o /tmp/sops.deb
sudo dpkg -i /tmp/sops.deb || sudo apt-get install -f -y
curl -sL https://github.com/FiloSottile/age/releases/download/v1.1.1/age-v1.1.1-linux-amd64.tar.gz -o /tmp/age.tar.gz
tar xzf /tmp/age.tar.gz -C /usr/local/bin/ age age-keygen

# Encrypt secrets
sops --encrypt secrets.yaml > secrets.yaml.tmp
mv secrets.yaml.tmp secrets.yaml
```

### 2. Add GitHub Secret

Go to `Settings > Secrets and variables > Actions` in your repo and add:
- `AGE_PRIVATE_KEY` — your Age private key (from `age-keygen` output)

### 3. Commit and Push

```bash
git add .
git commit -m "Initial platform setup with SOPS encrypted secrets"
git push origin main
```

## Files in this repo

| File | Description |
|------|-------------|
| `.github/workflows/kaggle-coordination.yml` | GitHub Actions workflow for 6 Kaggle machines |
| `secrets.yaml` | Encrypted secrets (SOPS + Age) |
| `.sops.yaml` | SOPS configuration |
| `.env.example` | Environment variables template |
| `config/platform.yaml` | Platform configuration |
| `config/retry_config.yml` | Retry and circuit breaker settings |

## Architecture

- **OpenClaw** — Orchestrator
- **Hermes-3** — LLM Reasoning Engine
- **Hermes Web UI** — Web interface
- **200 OSINT tools** across 10 categories
- **6 Kaggle machines** (distributed deployment)
- **SOPS + Age** — Encrypted secrets management
- **GitHub Actions** — Full automation