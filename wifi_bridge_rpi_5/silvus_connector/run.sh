#!/bin/bash

set -e  # Stop on first error

echo "🔄 Installing dependencies..."
sudo apt install -y \
  python3-scapy \
  python3-netifaces

# === EXPORT ENV VAR AND PERSIST ===
ENV_VAR_KEY="N2N_SUPERNODE_URL"
ENV_VAR_VAL="192.168.68.5"

echo "📦 Setting environment variable: $ENV_VAR_KEY=$ENV_VAR_VAL"

# Check if already present in /etc/environment and update or append accordingly
if grep -q "^${ENV_VAR_KEY}=" /etc/environment; then
  sudo sed -i "s|^${ENV_VAR_KEY}=.*|${ENV_VAR_KEY}=${ENV_VAR_VAL}|" /etc/environment
else
  echo "${ENV_VAR_KEY}=${ENV_VAR_VAL}" | sudo tee -a /etc/environment > /dev/null
fi

# Also export it for the current session (not persistent)
export ${ENV_VAR_KEY}=${ENV_VAR_VAL}

# === CONFIGURATION ===
SERVICE_NAME="silvus_connector"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT_PATH="${SCRIPT_DIR}/main.py"
PYTHON_EXEC="/usr/bin/python3"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

# === VALIDATION ===
if [ ! -f "$SCRIPT_PATH" ]; then
  echo "❌ Error: Python script not found at $SCRIPT_PATH"
  exit 1
fi

# === CREATE SYSTEMD SERVICE FILE ===
echo "🛠️ Creating systemd service file at $SERVICE_FILE..."

sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=Watch BSSID Script
After=network.target

[Service]
ExecStart=${PYTHON_EXEC} ${SCRIPT_PATH}
WorkingDirectory=${SCRIPT_DIR}
Environment=${ENV_VAR_KEY}=${ENV_VAR_VAL}
StandardOutput=inherit
StandardError=inherit
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOL

# === APPLY CHANGES ===
echo "🔄 Reloading systemd daemon..."
sudo systemctl daemon-reexec

echo "📌 Enabling service to start on boot..."
sudo systemctl enable ${SERVICE_NAME}.service

echo "🚀 Starting the service now..."
sudo systemctl start ${SERVICE_NAME}.service

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DONE!"
echo "➡️  Use 'sudo systemctl status ${SERVICE_NAME}.service' to check the status."
echo "➡️  Use 'sudo journalctl -u ${SERVICE_NAME}.service -f' to see logs."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
