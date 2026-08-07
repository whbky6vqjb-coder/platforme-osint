#!/usr/bin/env bash
set -e

echo "=== Platforme OSINT Bootstrap ==="

PLATFORM_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PLATFORM_DIR"

echo "[1/5] Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "[2/5] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "[3/5] Installing Node.js dependencies..."
npm install

echo "[4/5] Setting up directories..."
mkdir -p data/cache data/reports

echo "[5/5] Platform ready!"
echo ""
echo "To start the platform:"
echo "  python main.py"
echo ""
echo "Or with Docker:"
echo "  docker-compose up -d"