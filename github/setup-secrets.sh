#!/bin/bash
set -e

echo "=== Platforme OSINT - SOPS + Age + Pinggy Setup ==="

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

# Install Pinggy CLI
echo "Installing Pinggy..."
curl -sL https://github.com/pinggy-io/pinggy/releases/latest/download/pinggy_linux_amd64.tar.gz -o /tmp/pinggy.tar.gz
tar xzf /tmp/pinggy.tar.gz -C /usr/local/bin/
pinggy --version

# Prompt for Pinggy auth token
echo "Enter Pinggy Auth Token:"
read -r PINGGY_AUTH_TOKEN

echo "Enter Pinggy Endpoint URL (e.g., https://api.mon-domaine.com):"
read -r PINGGY_ENDPOINT

# Add Pinggy token and endpoint to secrets.yaml (if not present)
echo "" >> secrets.yaml
echo "PINGGY_AUTH_TOKEN: \"$PINGGY_AUTH_TOKEN\"" >> secrets.yaml
echo "PINGGY_ENDPOINT: \"$PINGGY_ENDPOINT\"" >> secrets.yaml

# Encrypt secrets
echo "Encrypting secrets.yaml..."
sops --encrypt secrets.yaml > secrets.yaml.tmp
mv secrets.yaml.tmp secrets.yaml
echo "secrets.yaml encrypted successfully"

echo "=== Setup complete ==="
echo "Add the following as a GitHub Secret (Pinggy token):"
echo "Pinggy token: \$PINGGY_AUTH_TOKEN"
echo "Add it to settings > Secrets and variables > Actions"