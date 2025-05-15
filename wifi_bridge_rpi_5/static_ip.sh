#!/bin/bash

set -e

echo "🌐 Configuring static IP for wlan interface via NetworkManager..."
IFACE_NAME="wlan0"
read -p "📥 Enter static IP to assign to wlan0 (e.g., 192.168.68.5/16): " STATIC_IP
GATEWAY="192.168.68.1"
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