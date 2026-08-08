#!/bin/bash
set -e

echo "=== Setup GitHub Secrets from secrets.yaml ==="

# Verify prerequisites
if ! command -v gh &> /dev/null; then echo "Please install 'gh' CLI"; exit 1; fi
if ! command -v sops &> /dev/null; then echo "Please install 'sops'"; exit 1; fi

# Decrypt secrets
echo "Decrypting secrets.yaml..."
SECRETS=$(sops -d secrets.yaml)

# Extract individual secrets
export AGE_PRIVATE_KEY=$(echo "$SECRETS" | yq -r '.AGE_PRIVATE_KEY')
export HF_TOKEN=$(echo "$SECRETS" | yq -r '.HF_TOKEN')
export HF_DATASET=$(echo "$SECRETS" | yq -r '.HF_DATASET')
export NGROK_AUTHTOKEN=$(echo "$SECRETS" | yq -r '.NGROK_AUTHTOKEN')

# Set GitHub secrets one by one
echo "Setting AGE_PRIVATE_KEY..."
echo "$AGE_PRIVATE_KEY" | gh secret set AGE_PRIVATE_KEY

echo "Setting HF_TOKEN..."
echo "$HF_TOKEN" | gh secret set HF_TOKEN

echo "Setting HF_DATASET..."
echo "$HF_DATASET" | gh secret set HF_DATASET

echo "Setting NGROK_AUTHTOKEN..."
echo "$NGROK_AUTHTOKEN" | gh secret set NGROK_AUTHTOKEN

# Set Kaggle credentials for accounts 1-6
for i in 1 2 3 4 5 6; do
  USERNAME=$(echo "$SECRETS" | yq -r ".KAGGLE_USERNAME_${i}")
  KEY=$(echo "$SECRETS" | yq -r ".KAGGLE_KEY_${i}")
  
  echo "Setting KAGGLE_USERNAME_${i}..."
  echo "$USERNAME" | gh secret set "KAGGLE_USERNAME_${i}"
  
  echo "Setting KAGGLE_KEY_${i}..."
  echo "$KEY" | gh secret set "KAGGLE_KEY_${i}"
done

echo "✅ All secrets configured successfully!"

# List created secrets as confirmation
echo ""
echo "Created secrets:"
gh secret list | grep -E "(AGE_PRIVATE|HF_|NGROK_|KAGGLE_)" || true