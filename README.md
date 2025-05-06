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
| RPI LAN interface | 192.168.68.50      | Internal, not exposed to the network |
| RPI N2N Master Node | 192.168.68.25      | Exposed to the entire network |
| CAM               | 192.168.68.125-149 | Exposed to the entire network, needs to be reserved in the Deco DHCP server        |
| Silvus            | 192.168.68.150-200 | Exposed to the entire network        |