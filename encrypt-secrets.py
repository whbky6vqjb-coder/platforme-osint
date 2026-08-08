#!/usr/bin/env python3
"""
Script pour chiffrer secrets.yaml avec SOPS
"""
import os
import subprocess
import shutil

# 1. D'abord, définir la clé dans l'environnement
key_path = os.path.expanduser("~/.config/sops/age/keys.txt")
os.makedirs(os.path.dirname(key_path), exist_ok=True)

# 2. Configurer SOPS_AGE_KEY_FILE
os.environ['SOPS_AGE_KEY_FILE'] = key_path

# 3. Chiffrer avec sops
try:
    result = subprocess.run([
        "sops", 
        "--encrypt",
        "--age", "age1zw4qn2llvklz94j6p0njp2sjy9z25q6ywyc2ugf2s4usq335ue0sg0f4zq",
        "secrets.yaml"
    ], capture_output=True, text=True, check=True)
    
    with open("secrets.yaml.enc", "w") as f:
        f.write(result.stdout)
    
    print("secrets.yaml chiffré avec succès")
except subprocess.CalledProcessError as e:
    print(f"Erreur sops: {e.stderr}")
    exit(1)
except FileNotFoundError:
    print("sops n'est pas installé")