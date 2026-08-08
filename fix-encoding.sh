#!/bin/bash
# Fixer le secrets.yaml

# 1. Convertir en UTF-8
iconv -f UTF-16LE -t UTF-8 "secrets.yaml" > "secrets_fixed.yaml"
mv "secrets_fixed.yaml" "secrets.yaml"
echo "✅ Encodage corrigé (UTF-16 → UTF-8)"

# 2. Vérifier le format
head -5 "secrets.yaml"