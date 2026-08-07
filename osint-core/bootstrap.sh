#!/usr/bin/env bash
set -e

echo "=== INITIALISATION DE L'AGENT OSINT 24/7 (NEMOTRON-3-NANO) ==="

# 1. Verification de l'accélérateur GPU
nvidia-smi

# 2. Installeurs système & dépendances Python
apt-get update && apt-get install -y -q tesseract-ocr ffmpeg
python3 -m pip install --upgrade pip
pip install trafilatura curl_cffi fastapi uvicorn networkx kaggle smolagents dnsrecon sublist3r

# 3. Restauration de l'état persistant
if [ -d "/kaggle/input/osint-agent-state" ]; then
    echo "Restauration de la base d'état..."
    cp /kaggle/input/osint-agent-state/database.sqlite ./storage/database.sqlite
fi

# 4. Lancement de llama-server avec TurboQuant / KV Compression
./llama-server \
  --model ./models/Nemotron-3-Nano-Q4_K_M.gguf \
  --n-gpu-layers 99 \
  --ctx-size 1048576 \
  --batch-size 2048 \
  --ubatch-size 512 \
  --cache-type-k q8_0 \
  --cache-type-v q4_0 \
  --flash-attn \
  --host 127.0.0.1 \
  --port 8080 > ./llama_server.log 2>&1 &

# Attente de la disponibilité du serveur d'inférence
until curl -s http://127.0.0.1:8080/health | grep -q "ok"; do
    sleep 5
done

# 5. Démarrage de l'interface Dashboard FastAPI
python3 web/app.py &

# 6. Exécution du runner principal
python3 main.py
