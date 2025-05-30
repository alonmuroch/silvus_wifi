# Silvus WiFi

Silvus WiFi is a project aimed at enabling Silvus radios to operate over WiFi in addition to their native RF links. This is accomplished using a combination of Layer 2 networking and VPN tunneling via N2N.

## 🛠️ Overview
Silvus radios primarily operate on Layer 2 frames, which makes bridging them over standard WiFi networks a complex task. Fortunately, Silvus devices support N2N VPN, which we leverage to tunnel traffic over WiFi networks while maintaining seamless communication.

## 📶 Network Topology
```arduino
Silvus Radio ⇄ Raspberry Pi ⇄ WiFi ⇄ N2N VPN Server
```
Each Raspberry Pi (RPI) acts as a lightweight router that:

* Forwards and masquerades Layer 2+ traffic from the Silvus radio
* Establishes a secure N2N VPN tunnel
* Provides basic IP routing over WiFi networks

## 📺 IP Camera Streaming
In addition to handling Silvus traffic, each RPI instance also:

Forwards port 8554 to 172.20.10.1:554, enabling RTSP streams from IP cameras over the VPN.

## 🌐 Network Configuration
* The Raspberry Pi obtains its IP address via DHCP
* mDNS is used for local hostname resolution using the format:

```bash
rpi<number>.local
```

For example, an RPI with index 3 can be accessed as rpi3.local on the local network.

## Install
### Client

```
scp -r wifi_bridge_rpi_5 admin@rpi0.local:/home/admin/Desktop
sudo sh run.sh
```

## Wifi Mesh
Deco M9

- Set in router mode
- DHCP from 192.168.68.2-49
- Fast roaming on 
- SSID: BBB:12345678

## IP table
| Device            | IP                 | Detail                               |
|-------------------|--------------------|--------------------------------------|
| RPI LAN interface | 172.20.0.1      | Internal, not exposed to the network |
| RPI WAN interface | 192.168.68.x/16      | Internal, not exposed to the network |
| RPI N2N Master Node | same as RPI0 (see below)      | Exposed to the entire network |
| CAM               | 172.20.10.x | Exposed to the entire network, needs to be reserved in the Deco DHCP server        |
| Silvus            | 172.20.x.x | Exposed to the entire network        |


## Operational WiFi RPI static IPs
| RPI            | IP                 | 
|-------------------|--------------------|
| 0 | 192.168.68.5/16       | 
| 1 | 192.168.68.6/16       | 
| 2 | 192.168.68.7/16       | 
| 3 | 192.168.68.8/16       | 
| 4 | 192.168.68.9/16       | 
| 5 | 192.168.68.10/16       | 
| 6 | 192.168.68.11/16       | 
| 7 | 192.168.68.12/16       | 
| 8 | 192.168.68.13/16       | 
| 9 | 192.168.68.14/16       | 


## Commom commands
Systemd service status
``` 
sudo systemctl status <supernode, watch_bssid>
```

TCP dump for N2N messages
``` 
sudo tcpdump -i wlan0 udp port 9000
```

Systemd processes 
``` 
sudo systemctl status watch_bssid.service
sudo systemctl restart watch_bssid.service
sudo journalctl -u watch_bssid.service -f

sudo systemctl status silvus_connector.service
sudo systemctl restart silvus_connector.service
sudo journalctl -u silvus_connector.service -f
```

iptabels
``` 
sudo iptables -t nat -L -n -v
```

RPI config
``` 
sudo raspi-config
sudo sudo nmtui
```





## Expected iptables
Chain PREROUTING (policy ACCEPT 23901 packets, 2772K bytes)
 pkts bytes target     prot opt in     out     source               destination         
    0     0 DNAT       6    --  wlan0  *       0.0.0.0/0            0.0.0.0/0            tcp dpt:8554 to:172.20.10.1:554

Chain INPUT (policy ACCEPT 7079 packets, 1674K bytes)
 pkts bytes target     prot opt in     out     source               destination         

Chain OUTPUT (policy ACCEPT 25614 packets, 1822K bytes)
 pkts bytes target     prot opt in     out     source               destination         

Chain POSTROUTING (policy ACCEPT 24576 packets, 1476K bytes)
 pkts bytes target     prot opt in     out     source               destination         
 1074  351K MASQUERADE  0    --  *      wlan0   0.0.0.0/0            0.0.0.0/0