#!/bin/bash
set -e

# === Configuration ===
ETH_PROFILE="Wired connection 1"
ETH_STATIC_IP="172.20.0.1"
ETH_PREFIX="16"
SYSCTL_CONF="/etc/sysctl.conf"
WIFI_IFACE="wlan0"

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
  echo "📦 Installing iptables..."
  sudo apt update
  sudo apt install -y iptables
else
  echo "✅ iptables already installed."
fi

# Install netfilter-persistent if not installed
if ! dpkg -l | grep -q netfilter-persistent; then
  echo "📦 Installing netfilter-persistent..."
  sudo apt update
  sudo apt install -y netfilter-persistent
else
  echo "✅ netfilter-persistent already installed."
fi

echo "🧹 Flushing old NAT rules..."
sudo iptables -t nat -F

echo "🌐 Applying MASQUERADE NAT on $WIFI_IFACE..."
sudo iptables -t nat -A POSTROUTING -o "$WIFI_IFACE" -j MASQUERADE
sudo iptables -t nat -A PREROUTING -i "$WIFI_IFACE" -p tcp --dport 8554 -j DNAT --to-destination 172.20.10.1:554
sleep 5 # make sure rules saved before persisting 

echo "💾 Saving iptables rules persistently..."
sudo netfilter-persistent save

echo "✅ Setup complete!"
echo "  • '$ETH_PROFILE' uses static IP $ETH_STATIC_IP/$ETH_PREFIX"
echo "  • IP forwarding is enabled"
echo "  • MASQUERADE active on $WIFI_IFACE for UDP port 9000"
echo "  • NAT rules will persist after reboot"
