#!/usr/bin/env python3

from scapy.all import sniff, IP, UDP, get_if_addr
import threading
import time
import signal

INTERFACE = "eth0"
TARGET_IP = "192.168.50.201"
SNIFF_TIMEOUT = 5  # seconds

# Tracks each device and its timer state
tracking_devices = {}
failed_ips = set()
stop_sniffing = False
lock = threading.Lock()

SELF_IP = get_if_addr(INTERFACE)
print(f"[INFO] Detected local IP: {SELF_IP} (will be excluded)\n")

def is_172_20(ip):
    return ip.startswith("172.20.")

def timer_check(ip):
    time.sleep(30)
    with lock:
        if tracking_devices.get(ip, {}).get("saw_target") is False:
            print(f"[✘] {ip} failed to send to {TARGET_IP} within 30 seconds.")
            failed_ips.add(ip)
        tracking_devices.pop(ip, None)

def process_packet(pkt):
    global tracking_devices
    if IP in pkt and UDP in pkt:
        src_ip = pkt[IP].src
        dst_ip = pkt[IP].dst
        sport = pkt[UDP].sport
        dport = pkt[UDP].dport

        print(f"{src_ip} → {dst_ip} | UDP sport={sport} dport={dport}", flush=True)

        if src_ip == SELF_IP:
            return

        if is_172_20(src_ip):
            with lock:
                if src_ip in failed_ips:
                    return  # Already failed, skip

                if src_ip not in tracking_devices:
                    print(f"[⏱] Tracking {src_ip} for 30s to see if it sends to {TARGET_IP}")
                    tracking_devices[src_ip] = {"saw_target": False}
                    threading.Thread(target=timer_check, args=(src_ip,), daemon=True).start()

                if dst_ip == TARGET_IP and not tracking_devices[src_ip]["saw_target"]:
                    tracking_devices[src_ip]["saw_target"] = True
                    print(f"[✔] {src_ip} sent to {TARGET_IP} within 30 seconds!")

def signal_handler(sig, frame):
    global stop_sniffing
    print("\n[✓] Ctrl+C received — stopping...")
    stop_sniffing = True

def main():
    global stop_sniffing
    print(f"[+] Sniffing all UDP traffic on {INTERFACE}...\n")
    signal.signal(signal.SIGINT, signal_handler)

    while not stop_sniffing:
        sniff(
            iface=INTERFACE,
            filter="udp",
            timeout=SNIFF_TIMEOUT,
            prn=process_packet,
            store=False
        )

    print("\n[✓] Sniffer exited cleanly.")

if __name__ == "__main__":
    main()
