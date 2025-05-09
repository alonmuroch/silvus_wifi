# Network Setup

## Wifi Mesh
Deco M9

- Set in router mode
- DHCP from 192.168.68.2-49
- Fast roaming on 
- SSID: BBB:12345678

$# IP table
| Device            | IP                 | Detail                               |
|-------------------|--------------------|--------------------------------------|
| RPI LAN interface | 172.20.0.1      | Internal, not exposed to the network |
| RPI N2N Master Node | 192.168.50.201      | Exposed to the entire network |
| CAM               | 172.20.10.x | Exposed to the entire network, needs to be reserved in the Deco DHCP server        |
| Silvus            | 172.20.x.x | Exposed to the entire network        |