#!/usr/bin/env python3
"""
Script pour réparer et décrypter secrets.yaml
"""
import os
import subprocess
import shutil

# 1. Convertir secrets.yaml en UTF-8
with open('secrets.yaml', 'rb') as f:
    content = f.read()

# Détecter l'encodage BOM
if content[:2] == b'\xff\xfe':
    # UTF-16 LE
    text = content[2:].decode('utf-16-le')
elif content[:2] == b'\xfe\xff':
    # UTF-16 BE
    text = content[2:].decode('utf-16-be')
else:
    # UTF-8
    text = content.decode('utf-8')

# Écrire en UTF-8
with open('secrets.yaml', 'w', encoding='utf-8') as f:
    f.write(text)

print("✅ secrets.yaml converti en UTF-8")

# 2. Configurer la clé Age
key_path = os.path.expanduser("~/.config/sops/age/keys.txt")
os.makedirs(os.path.dirname(key_path), exist_ok=True)

# Copier la clé depuis le téléchargement
source_key = os.path.expanduser("~\\.age\\keys.txt")
if os.path.exists(source_key):
    shutil.copy(source_key, key_path)
    print("✅ Clé Age configurée dans ~/.config/sops/age/keys.txt")
else:
    print("❌ Clé source introuvable")
    exit(1)

# 3. Vérifier la clé
with open(key_path, 'r') as f:
    key_content = f.read()
    print("Clé trouvée :", key_content.split('\n')[1] if len(key_content.split('\n')) > 1 else "??")

print("\n✅ Prêt pour décryptage")
print("Utilisez : sops --decrypt secrets.yaml")