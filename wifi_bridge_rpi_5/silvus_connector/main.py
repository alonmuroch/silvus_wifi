#!/usr/bin/env python3

from scapy.all import sniff, IP, UDP
import threading
import time
import signal
import socket
import fcntl
import struct
from silvus_api import configure_virtual_ip_sequence

INTERFACE = "eth0"
TARGET_IP = "192.168.68.201"
SNIFF_TIMEOUT = 5  # seconds

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


SELF_IP = get_self_ip(INTERFACE)
log(f"[INFO] Detected local IP: {SELF_IP} (will be excluded)\n")


def is_172_20(ip):
    return ip.startswith("172.20.")


def post_reconfig_check(ip):
    log(f"[🔍] Waiting 30s to see if {ip} sends to {TARGET_IP} after reconfiguration...")
    start_time = time.time()
    while time.time() - start_time < 30:
        with lock:
            info = tracking_devices.get(ip, {})
            if info.get("saw_target_after_reconfig") and not info.get("completed"):
                log(f"[✔] {ip} sent to {TARGET_IP} after reconfiguration.")
                info["completed"] = True
                return
        time.sleep(1)

    log(f"[✘] {ip} did not send to {TARGET_IP} after reconfiguration.")
    with lock:
        tracking_devices.pop(ip, None)


def timer_check(ip):
    time.sleep(30)
    with lock:
        info = tracking_devices.get(ip)
        if not info or info.get("completed"):
            return

        if not info.get("saw_target") and not info.get("reconfig_sent"):
            log(f"[✘] {ip} failed to send to {TARGET_IP} within 30 seconds.")
            info["reconfig_sent"] = True

    log(f"[⚙] Sending API reconfiguration for {ip}...")
    configure_virtual_ip_sequence(ip, "0")
    configure_virtual_ip_sequence(ip, "1")

    time.sleep(1)
    with lock:
        tracking_devices[ip]["saw_target_after_reconfig"] = False
    threading.Thread(target=post_reconfig_check, args=(ip,), daemon=True).start()


def process_packet(pkt):
    if IP in pkt and UDP in pkt:
        src_ip = pkt[IP].src
        dst_ip = pkt[IP].dst
        sport = pkt[UDP].sport
        dport = pkt[UDP].dport

        log(f"{src_ip} → {dst_ip} | UDP sport={sport} dport={dport}")

        if src_ip == SELF_IP or not is_172_20(src_ip):
            return

        with lock:
            entry = tracking_devices.get(src_ip)

            if entry is None:
                tracking_devices[src_ip] = {
                    "saw_target": False,
                    "saw_target_after_reconfig": False,
                    "reconfig_sent": False,
                    "completed": False
                }
                log(f"[⏱] Tracking {src_ip} for 30s to see if it sends to {TARGET_IP}")
                threading.Thread(target=timer_check, args=(src_ip,), daemon=True).start()
                entry = tracking_devices[src_ip]

            if dst_ip == TARGET_IP:
                if entry.get("completed"):
                    return

                if "saw_target_after_reconfig" in entry and not entry["saw_target_after_reconfig"]:
                    entry["saw_target_after_reconfig"] = True
                    log(f"[↩] {src_ip} sent to {TARGET_IP} after reconfiguration!")
                elif not entry.get("saw_target"):
                    entry["saw_target"] = True
                    log(f"[✔] {src_ip} sent to {TARGET_IP} within 30 seconds!")


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
