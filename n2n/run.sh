#!/bin/bash

set -e

echo "🔄 Updating package list..."
sudo apt update && sudo apt upgrade -y

echo "📦 Installing required packages..."
sudo apt install -y git build-essential tcpdump

REPO_DIR="n2n_v2_fork"
if [ ! -d "$REPO_DIR" ]; then
  echo "📁 Cloning the repository..."
  git clone https://github.com/lukablurr/n2n_v2_fork.git
else
  echo "📁 Repository already cloned, skipping..."
fi

cd $REPO_DIR

echo "🔐 Disabling AES support..."
export N2N_OPTION_AES=no

echo "🧹 Cleaning previous builds..."
make clean

echo "🔨 Building the project..."
make

# Optional: Set SUID-root on supernode (not needed, runs as regular user)
# echo "🔒 Setting SUID-root on supernode (optional)..."
# sudo chown root:root supernode
# sudo chmod +s supernode

echo "📝 Creating systemd service for supernode..."

SERVICE_PATH="/etc/systemd/system/supernode.service"
sudo bash -c "cat > $SERVICE_PATH" <<EOF
[Unit]
Description=n2n supernode service
After=network-online.target
Wants=network-online.target

[Service]
Type=forking
ExecStart=/home/admin/Desktop/n2n/n2n_v2_fork/supernode -l 9000 -v
Restart=on-failure
User=root

[Install]
WantedBy=multi-user.target
EOF

echo "🔄 Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "📌 Enabling supernode to start on boot..."
sudo systemctl enable supernode

echo "🚀 Starting supernode..."
sudo systemctl start supernode

echo "🌐 Configuring static IP for wlan interface via NetworkManager..."
CON_NAME="wifi-static"
IFACE_NAME="wlan0"
STATIC_IP="192.168.68.201/16"
GATEWAY="192.168.68.1"
DNS="1.1.1.1"
SSID="blox"
WIFI_PASSWORD="B1l2o3x4"

nmcli con delete "$CON_NAME" 2>/dev/null || true
nmcli con add type wifi ifname "$IFACE_NAME" con-name "$CON_NAME" autoconnect yes ssid "$SSID"
nmcli con modify "$CON_NAME" ipv4.method manual ipv4.addresses "$STATIC_IP" ipv4.gateway "$GATEWAY" ipv4.dns "$DNS"
nmcli con modify "$CON_NAME" wifi-sec.key-mgmt wpa-psk
nmcli con modify "$CON_NAME" wifi-sec.psk "$WIFI_PASSWORD"
nmcli con up "$CON_NAME"

echo "✅ Supernode is now running!"
echo "📜 View logs: journalctl -u supernode -f"
echo "🧩 Check port: sudo lsof -iUDP:9000"
echo "🔁 Reboot to test persistence: sudo reboot"
