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
IFACE_NAME="wlan0"
read -p "📥 Enter static IP to assign to wlan0 (e.g., 192.168.50.201/16): " STATIC_IP
GATEWAY="192.168.50.1"
DNS="1.1.1.1"

# Find the active connection for wlan0
CON_NAME=$(nmcli -g NAME,DEVICE con show --active | grep "$IFACE_NAME" | cut -d: -f1)

if [ -z "$CON_NAME" ]; then
  echo "❌ No active connection found on $IFACE_NAME. Please connect Wi-Fi first."
  exit 1
fi

echo "⚙️ Modifying connection '$CON_NAME' to set static IP $STATIC_IP..."

nmcli con modify "$CON_NAME" ipv4.method manual ipv4.addresses "$STATIC_IP" ipv4.gateway "$GATEWAY" ipv4.dns "$DNS"
nmcli con up "$CON_NAME"

echo "✅ Supernode is now running!"
echo "📜 View logs: journalctl -u supernode -f"
echo "🧩 Check port: sudo lsof -iUDP:9000"
echo "🧩 Check systemd: sudo systemctl status supernode"
echo "🧩 Check traffic: sudo tcpdump -i wlan0 udp port 9000"
echo "🔁 Reboot to test persistence: sudo reboot"
