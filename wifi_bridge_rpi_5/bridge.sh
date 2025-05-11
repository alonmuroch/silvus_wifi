#!/bin/bash
set -e

# === Configuration ===
ETH_PROFILE="Wired connection 1"
ETH_STATIC_IP="172.20.0.1"
ETH_PREFIX="16"
SYSCTL_CONF="/etc/sysctl.conf"
WIFI_IFACE="wlan0"
DNAT_IP="172.20.10.1"
DNAT_PORT="554"
LISTEN_PORT="8554"
SERVICE_NAME="iptables-bridge"

echo "🔧 Configuring '$ETH_PROFILE' with static IP $ETH_STATIC_IP/$ETH_PREFIX..."
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


echo "📝 Writing iptables rule script..."
sudo tee /usr/local/sbin/${SERVICE_NAME}.sh > /dev/null <<EOF
#!/bin/bash
set -e
iptables -t nat -F
iptables -t nat -A POSTROUTING -o "$WIFI_IFACE" -j MASQUERADE
iptables -t nat -A PREROUTING -i "$WIFI_IFACE" -p tcp --dport $LISTEN_PORT -j DNAT --to-destination $DNAT_IP:$DNAT_PORT
EOF

sudo chmod +x /usr/local/sbin/${SERVICE_NAME}.sh

echo "🛠️ Creating systemd service to reapply rules on boot..."
sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null <<EOF
[Unit]
Description=Apply iptables NAT rules on boot
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/local/sbin/${SERVICE_NAME}.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

echo "🔁 Enabling and starting systemd service..."
sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}.service
sudo systemctl start ${SERVICE_NAME}.service

echo "✅ Setup complete!"
echo "  • '$ETH_PROFILE' uses static IP $ETH_STATIC_IP/$ETH_PREFIX"
echo "  • IP forwarding is enabled"
echo "  • NAT rules are active and persist after reboot via systemd"
