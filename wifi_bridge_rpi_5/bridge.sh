#!/bin/bash
set -e

# === Configuration ===
ETH_PROFILE="Wired connection 1"
ETH_STATIC_IP="172.20.0.1"
ETH_PREFIX="16"
SYSCTL_CONF="/etc/sysctl.conf"

echo "🔧 Configuring '$ETH_PROFILE' with static IP $ETH_STATIC_IP/$ETH_PREFIX..."

# Configure static IP for eth0 via existing profile
nmcli connection modify "$ETH_PROFILE" ipv4.addresses "$ETH_STATIC_IP/$ETH_PREFIX"
nmcli connection modify "$ETH_PROFILE" ipv4.method manual
nmcli connection modify "$ETH_PROFILE" ipv6.method ignore
nmcli connection modify "$ETH_PROFILE" ipv4.gateway ""
nmcli connection modify "$ETH_PROFILE" ipv4.dns ""
nmcli connection up "$ETH_PROFILE"

echo "🔁 Enabling IP forwarding permanently..."
sudo sysctl -w net.ipv4.ip_forward=1
sudo sed -i '/^#net.ipv4.ip_forward=1/s/^#//' "$SYSCTL_CONF"
sudo sed -i '/^net.ipv4.ip_forward=0/s/0/1/' "$SYSCTL_CONF" || true

# Install iptables if missing
if ! command -v iptables >/dev/null; then
  echo "📦 'iptables' not found. Installing it..."
  sudo apt update
  sudo apt install -y iptables
else
  echo "✅ 'iptables' is already installed."
fi

echo "🧹 Flushing NAT rules (no NAT is used)..."
sudo iptables -t nat -F

echo "✅ Setup complete!"
echo "  • '$ETH_PROFILE' is now using static IP $ETH_STATIC_IP/$ETH_PREFIX"
echo "  • IP forwarding is enabled"
echo "  • iptables installed and NAT table flushed (just in case)"
