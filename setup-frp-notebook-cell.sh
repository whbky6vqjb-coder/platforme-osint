# ── Cell 1 : Setup FRP + API ──────────────────────────────────────
# Exécutez cette cellule dans chaque notebook Kaggle (kaggle_1 à kaggle_6)
# pour configurer le tunnel FRP permanent et lancer l'API Flask.

# ── 1. Configuration FRP ──
# Le tunnel FRP expose l'API Flask sur l'URL fixe :
#   https://vortx-api.duckdns.org:38443
#   (port 38443 = 8080 local + FRP + HTTPS)

# Créer le dossier et le fichier de config FRP
mkdir -p /opt/API

# Générer frpc.toml avec le nom de proxy dynamique selon le worker
worker_id="${KAGGLE_WORKER_ID:-kaggle_1}"
proxy_name="vortx-kaggle-api-${worker_id}"

cat > /opt/API/frpc.toml << EOF
[server]
server_addr = "vortx-api.duckdns.org"
server_port = 27000

[auth]
token = "#2PIAUengaly"

[[proxies]]
name = "${proxy_name}"
type = "http"
localPort = 8080
customDomains = ["vortx-api.duckdns.org"]
EOF

echo "✅ FRP config créé (proxy: ${proxy_name})"

# ── 2. Installer FRP (si pas déjà installé) ──
# Le binaire frpc est déjà installé via setup-secrets.sh
# Si ce n'est pas le cas, voici la commande manuelle :

if ! command -v frpc &> /dev/null; then
  echo "Installation FRP..."
  wget -q https://github.com/fatedier/frp/releases/download/v0.61.0/frp_0.61.0_linux_amd64.tar.gz -O /tmp/frp.tar.gz
  tar xzf /tmp/frp.tar.gz -C /tmp/
  sudo cp /tmp/frp_0.61.0_linux_amd64/frpc /usr/local/bin/
  sudo chmod +x /usr/local/bin/frpc
  echo "FRP installé"
fi

# ── 3. Lancer le client FRP ──
# Exécuter en arrière-plan pour que le notebook continue de tourner
frpc -c /opt/API/frpc.toml &

# ── 4. Vérifier le tunnel ──
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🔌 Tunnel FRP actif"
echo "  Proxy :   ${proxy_name}"
echo "  API URL  : https://vortx-api.duckdns.org:38443"
echo "  Local API : http://localhost:8080"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📌 L'API Flask est accessible via https://vortx-api.duckdns.org:38443"
echo "📌 L'authentification est basée sur le header Bearer <token>"
echo "   (le token est défini dans les secrets.yaml)"
echo ""
echo "✅ Client FRP démarré avec le nom de proxy : ${proxy_name}"