#!/bin/bash
set -e

echo "=== Platforme OSINT - API + FRP Tunnel Startup ==="

# 1. Start Flask API
python3 osint-core/engine/api_server.py &

# 2. Wait for server readiness
sleep 5

# 3. Launch FRP tunnel
worker_id="${KAGGLE_WORKER_ID:-kaggle_1}"

mkdir -p /opt/API

cat > /opt/API/frpc.toml << EOF
[server]
serverAddr = "vortx-api.duckdns.org"
serverPort = 27000

[auth]
token = "#2PIAUengaly"

[[proxies]]
name = "vortx-kaggle-api-${worker_id}"
type = "http"
localPort = 8080
customDomains = ["vortx-api.duckdns.org"]
EOF

# 4. Install and launch FRP client
if ! command -v frpc &> /dev/null; then
  wget -q https://github.com/fatedier/frp/releases/download/v0.61.0/frp_0.61.0_linux_amd64.tar.gz -O /tmp/frp.tar.gz
  tar xzf /tmp/frp.tar.gz -C /tmp/
  sudo cp /tmp/frp_0.61.0_linux_amd64/frpc /usr/local/bin/
  sudo chmod +x /usr/local/bin/frpc
fi

frpc -c /opt/API/frpc.toml &

# 5. Verify startup
sleep 2
if curl -s http://localhost:8080/health > /dev/null; then
    echo "Flask API started on localhost:8080"
    echo "FRP tunnel started"
    echo "  Endpoint : https://vortx-api.duckdns.org:38443"
else
    echo "Startup failed"
    exit 1
fi

wait