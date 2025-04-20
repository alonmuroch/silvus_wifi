# Burn RPI Image
1) Use PI IMager
2) Select RPI 5, 64bit Pi OS
3) Set host name to rpi<pi number>.local
4) set username & password
```
username: admin
password: 12345678
```
5) set wireless LAN to an internet enabled WiFi
6) Burn

# RPI 5 WIFI Bridge
1) 
```
	scp -r wifi_bridge_rpi_5 admin@rpi.local:/home/admin/Desktop/wifi_bridge_rpi_5
```

2) 
```
	cd Desktop/wifi_bridge_rpi_5 && sudo sh run.sh
```

# IP table
| Device            | IP                 | Detail                               |
|-------------------|--------------------|--------------------------------------|
| RPI LAN interface | 192.168.68.50      | Internal, not exposed to the network |
| CAM               | 192.168.68.125-150 | Exposed to the entire network        |
| Silvus            | 192.168.68.150-200 | Exposed to the entire network        |