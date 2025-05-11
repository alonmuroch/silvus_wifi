#!/bin/bash

set -e  # Stop on first error

echo "🔄 Installing dependencies..."
sudo apt install -y \
  python3-scapy \
  python3-netifaces


# === CONFIGURATION ===
SERVICE_NAME="silvus_connector"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT_PATH="${SCRIPT_DIR}/main.py"
PYTHON_EXEC="/usr/bin/python3"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

# === VALIDATION ===
if [ ! -f "$SCRIPT_PATH" ]; then
  echo "Error: Python script not found at $SCRIPT_PATH"
  exit 1
fi

# === CREATE SYSTEMD SERVICE FILE ===
echo "Creating systemd service file at $SERVICE_FILE..."

sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=Watch BSSID Script
After=network.target

[Service]
ExecStart=${PYTHON_EXEC} ${SCRIPT_PATH}
WorkingDirectory=${SCRIPT_DIR}
StandardOutput=inherit
StandardError=inherit
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOL

# === APPLY CHANGES ===
echo "Reloading systemd daemon..."
sudo systemctl daemon-reexec

echo "Enabling service to start on boot..."
sudo systemctl enable ${SERVICE_NAME}.service

echo "Starting the service now..."
sudo systemctl start ${SERVICE_NAME}.service

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "DONE!"
echo "➡️  Use 'sudo systemctl status ${SERVICE_NAME}.service' to check the status."
echo "➡️  Use 'sudo journalctl -u ${SERVICE_NAME}.service -f' to see logs."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"



