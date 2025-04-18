#!/bin/bash

set -e  # Stop on first error

echo "🔄 Updating system ..."
sudo apt update

echo "🔄 Installing dependencies..."
sudo apt install -y \
  parprouted \
  dhcp-helper \
  dhcpcd \
  systemd-resolved \
  python3-gpiozero

echo "✅ Dependencies installed."

echo "🔁 Executing bridge setup and rebooting..."
sudo sh bridge.sh

echo "🚀 Running BSSID watcher container..."
sudo sh watch_bssid/run.sh

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "➡️  To switch to the operational Wi-Fi network (SSID: BBB):"
echo "   Run: sudo nmtui"
echo "   Then select and activate the network named 'BBB'"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "♻️ Rebooting now..."
sudo reboot
