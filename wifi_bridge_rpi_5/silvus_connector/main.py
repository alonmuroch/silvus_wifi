#!/usr/bin/env python3

from scapy.all import sniff, IP, UDP, Ether
import threading
import time
import signal
import socket
import fcntl
import struct
import subprocess
from silvus_api import configure_virtual_ip_sequence, refresh_ptt_settings

INTERFACE = "eth0"
TARGET_IP = "192.168.68.201"
SNIFF_TIMEOUT = 5  # seconds
TIMEOUT_SECONDS = 15  # seconds for cleanup

tracking_devices = {}
stop_sniffing = False
lock = threading.Lock()


def log(msg):
    print(msg, flush=True)


def get_self_ip(interface):
    """Return the IP address for the given network interface (e.g., eth0)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        return socket.inet_ntoa(
            fcntl.ioctl(
                s.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack('256s', interface.encode('utf-8')[:15])
            )[20:24]
        )
    except Exception:
        return "127.0.0.1"


def get_self_mac(interface):
    """Return the MAC address for the given interface."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        info = fcntl.ioctl(
            s.fileno(),
            0x8927,  # SIOCGIFHWADDR
            struct.pack('256s', interface.encode('utf-8')[:15])
        )
        return ':'.join('%02x' % b for b in info[18:24])
    except Exception:
        return "00:00:00:00:00:00"


def mac_on_eth0_neigh(mac):
    """Return True if MAC is associated with eth0 in neighbor table and is in a valid state."""
    try:
        output = subprocess.check_output(["ip", "neigh", "show", "dev", INTERFACE], text=True)
        for line in output.splitlines():
            if (
                mac.lower() in line.lower()
                and any(state in line for state in ("REACHABLE", "STALE", "DELAY", "PROBE"))
            ):
                return True
    except Exception as e:
        log(f"[WARN] Could not query neighbor table: {e}")
    return False


SELF_IP = get_self_ip(INTERFACE)
SELF_MAC = get_self_mac(INTERFACE)

log(f"[INFO] Detected local IP: {SELF_IP} (will be excluded)")
log(f"[INFO] Detected {INTERFACE} MAC address: {SELF_MAC}\n")


def is_172_20(ip):
    return ip.startswith("172.20.")


def schedule_cleanup(ip, delay=TIMEOUT_SECONDS):
    def cleanup():
        time.sleep(delay)
        with lock:
            if ip in tracking_devices:
                log(f"[🧹] Cleaning up tracking state for {ip}")
                del tracking_devices[ip]
    threading.Thread(target=cleanup, daemon=True).start()


def timer_check(ip):
    time.sleep(TIMEOUT_SECONDS)

    schedule_cleanup(ip)
    with lock:
        info = tracking_devices.get(ip)
        if not info or info.get("saw_target"):
            return

        if not info.get("reconfig_sent"):
            log(f"[✘] {ip} failed to send to {TARGET_IP} within {TIMEOUT_SECONDS}s.")
            info["reconfig_sent"] = True

    log(f"[⚙] Sending API reconfiguration for {ip}...")
    configure_virtual_ip_sequence(ip, "0")
    configure_virtual_ip_sequence(ip, "1")
    refresh_ptt_settings(ip)


def process_packet(pkt):
    if Ether in pkt and IP in pkt and UDP in pkt:
        src_mac = pkt[Ether].src
        dst_mac = pkt[Ether].dst
        src_ip = pkt[IP].src
        dst_ip = pkt[IP].dst
        sport = pkt[UDP].sport
        dport = pkt[UDP].dport

        log(f"{src_ip} ({src_mac}) → {dst_ip} ({dst_mac}) | UDP sport={sport} dport={dport}")

        # Exclude self-originated, non-172.20, or MACs not valid on eth0
        if (
            src_ip == SELF_IP
            or not is_172_20(src_ip)
            or not mac_on_eth0_neigh(src_mac)
        ):
            return

        with lock:
            entry = tracking_devices.get(src_ip)

            if entry is None:
                tracking_devices[src_ip] = {
                    "saw_target": False,
                    "reconfig_sent": False
                }
                log(f"[⏱] Tracking {src_ip} for {TIMEOUT_SECONDS}s to see if it sends to {TARGET_IP}")
                threading.Thread(target=timer_check, args=(src_ip,), daemon=True).start()
                entry = tracking_devices[src_ip]

            if dst_ip == TARGET_IP and not entry.get("saw_target"):
                entry["saw_target"] = True
                log(f"[✔] {src_ip} sent to {TARGET_IP} within {TIMEOUT_SECONDS}s!")


def signal_handler(sig, frame):
    global stop_sniffing
    log("\n[✓] Ctrl+C received — stopping...")
    stop_sniffing = True


def main():
    global stop_sniffing
    log(f"[+] Sniffing all UDP traffic on {INTERFACE}...\n")
    signal.signal(signal.SIGINT, signal_handler)

    while not stop_sniffing:
        sniff(
            iface=INTERFACE,
            filter="udp",
            timeout=SNIFF_TIMEOUT,
            prn=process_packet,
            store=False
        )

    log("\n[✓] Sniffer exited cleanly.")


if __name__ == "__main__":
    main()
