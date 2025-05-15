#!/bin/bash

set -e  # Stop on first error

echo "🔄 Updating system ..."
sudo apt update

echo "🔄 Installing dependencies..."
sudo apt install -y \
  python3-gpiozero \
  tcpdump

echo "✅ Dependencies installed."

echo "🔁 Executing bridge setup and rebooting..."
sudo sh bridge.sh

echo "🚀 Running BSSID watcher systemd process..."
sudo sh watch_bssid/run.sh

echo "🚀 Running Silvus Connector watcher systemd process..."
sudo sh silvus_connector/run.sh

echo "🚀 Setting static IP..."
sudo sh static_ip.sh


echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "➡️  To switch to the operational Wi-Fi network (SSID: BBB):"
echo "   Run: sudo nmtui"
echo "   Then select and activate the network named 'BBB'"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "♻️ Rebooting now..."
sudo reboot
