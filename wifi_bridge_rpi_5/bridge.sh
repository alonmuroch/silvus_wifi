#!/usr/bin/env bash

set -e

[ $EUID -ne 0 ] && echo "Run as root" >&2 && exit 1

echo "🔧 Setting Wi-Fi country code and basic parameters..."
country=US

echo "🚫 Stopping services to reconfigure networking..."
systemctl stop dhcpcd dhcp-helper systemd-resolved

echo "✅ Enabling necessary services to start on boot..."
systemctl enable dhcpcd dhcp-helper systemd-resolved

echo "🔗 Enabling wpa_supplicant hook for dhcpcd..."
ln -sf /usr/share/dhcpcd/hooks/10-wpa_supplicant /usr/lib/dhcpcd/dhcpcd-hooks/

echo "📡 Enabling IPv4 forwarding in sysctl..."
sed -i'' s/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/ /etc/sysctl.conf

echo "🚫 Telling dhcpcd to ignore eth0 (it will be manually configured)..."
grep '^denyinterfaces eth0$' /etc/dhcpcd.conf || printf "denyinterfaces eth0\n" >> /etc/dhcpcd.conf

echo "💾 Setting static IP addresses for eth0 in dhcpcd.conf..."
grep -q "interface eth0" /etc/dhcpcd.conf || cat <<EOF >> /etc/dhcpcd.conf

interface eth0
static ip_address=192.168.68.50/16
static routers=192.168.68.1
static domain_name_servers=192.168.68.1
EOF

echo "📨 Configuring dhcp-helper to relay from wlan0..."
cat > /etc/default/dhcp-helper <<EOF
DHCPHELPER_OPTS="-b wlan0"
EOF


echo "📡 Enabling Avahi mDNS reflector..."
sed -i'' 's/#enable-reflector=no/enable-reflector=yes/' /etc/avahi/avahi-daemon.conf
grep '^enable-reflector=yes$' /etc/avahi/avahi-daemon.conf || {
  echo "⚠️  Something went wrong setting Avahi reflector."
  echo "👉  Manually set 'enable-reflector=yes' in /etc/avahi/avahi-daemon.conf"
}

echo "🔁 Creating parprouted systemd service to enable bridging..."
cat <<'EOF' >/usr/lib/systemd/system/parprouted.service
[Unit]
Description=proxy arp routing service
Documentation=https://raspberrypi.stackexchange.com/q/88954/79866
Requires=sys-subsystem-net-devices-wlan0.device dhcpcd.service
After=sys-subsystem-net-devices-wlan0.device dhcpcd.service

[Service]
Type=forking
Restart=on-failure
RestartSec=5
TimeoutStartSec=30
ExecStartPre=/bin/bash -c '/sbin/ip addr add $(/sbin/ip -4 -br addr show wlan0 | /bin/grep -Po "\\d+\\.\\d+\\.\\d+\\.\\d+")/32 dev eth0'
ExecStartPre=/sbin/ip link set dev eth0 up
ExecStartPre=/sbin/ip link set wlan0 promisc on
ExecStart=-/usr/sbin/parprouted eth0 wlan0
ExecStopPost=/sbin/ip link set wlan0 promisc off
ExecStopPost=/sbin/ip link set dev eth0 down
ExecStopPost=/bin/bash -c '/sbin/ip addr del $(/sbin/ip -4 -br addr show wlan0 | /bin/grep -Po "\\d+\\.\\d+\\.\\d+\\.\\d+")/32 dev eth0'

[Install]
WantedBy=wpa_supplicant.service
EOF

echo "🧹 Disabling NetworkManager for eth0 to prevent interference..."
# systemctl disable NetworkManager
nmcli device set eth0 managed no

echo "🔃 Reloading systemd daemon and enabling parprouted..."
systemctl daemon-reload
systemctl enable parprouted

echo "✅ Setup complete! Reboot or start services manually to bring everything up."
