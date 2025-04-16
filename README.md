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
scp bssid_watch_rpi.py admin@rpi<pi number>.local:/home/admin/Desktop
scp bridgeV1.2.sh admin@rpi<pi number>.local:/home/admin/Desktop
```
2) ```
	sudo apt update && sudo apt install -y parprouted dhcp-helper dhcpcd systemd-resolved python3-gpiozero
```

3) change wifi to 'BBB' and reboot
```
	sudo nmtui
```

4)```

	sudo sh bridge.sh && sudo reboot
```