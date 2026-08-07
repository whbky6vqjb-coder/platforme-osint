#!/bin/bash
set -e

echo "=== Platforme OSINT - SOPS + Age Setup ==="

# Install SOPS
echo "Installing SOPS..."
curl -sL https://github.com/getsops/sops/releases/download/v3.8.1/sops_3.8.1_amd64.deb -o /tmp/sops.deb
sudo dpkg -i /tmp/sops.deb || sudo apt-get install -f -y
sops --version

# Install Age
echo "Installing Age..."
curl -sL https://github.com/FiloSottile/age/releases/download/v1.1.1/age-v1.1.1-linux-amd64.tar.gz -o /tmp/age.tar.gz
tar xzf /tmp/age.tar.gz -C /usr/local/bin/ age age-keygen
age --version

# Generate Age key pair if not exists
if [ ! -f "$HOME/.config/sops/age/keys.txt" ]; then
  echo "Generating Age key pair..."
  mkdir -p "$HOME/.config/sops/age"
  age-keygen -o "$HOME/.config/sops/age/keys.txt"
  echo "Public key: $(head -1 "$HOME/.config/sops/age/keys.txt" | cut -d' ' -f2)"
fi

# Encrypt secrets
echo "Encrypting secrets.yaml..."
if [ -f "secrets.yaml" ]; then
  sops --encrypt secrets.yaml > secrets.yaml.tmp
  mv secrets.yaml.tmp secrets.yaml
  echo "secrets.yaml encrypted successfully"
else
  echo "ERROR: secrets.yaml not found"
  exit 1
fi

echo "=== Setup complete ==="
echo "Add the following as a GitHub Secret (AGE_PRIVATE_KEY):"
cat "$HOME/.config/sops/age/keys.txt"