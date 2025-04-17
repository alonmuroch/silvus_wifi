import subprocess
import time

SSID = "BBB"
INTERFACE = "wlan0"
SIGNAL_THRESHOLD = -55
SCAN_INTERVAL = 2  # seconds

def get_current_connection():
    result = subprocess.run(
        ["nmcli", "-f", "IN-USE,BSSID,SIGNAL", "dev", "wifi"],
        capture_output=True, text=True
    )
    for line in result.stdout.splitlines():
        if line.startswith("*"):
            try:
                parts = line.strip().split()
                bssid = parts[1]
                signal = int(parts[2])
                return bssid, signal*-1
            except Exception:
                continue
    return None, None

import re

def get_best_ap():
    subprocess.run(
        ["sudo", "nmcli", "dev", "wifi", "rescan"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(1)

    result = subprocess.run(
        ["nmcli", "-f", "SSID,BSSID,SIGNAL", "dev", "wifi", "list"],
        capture_output=True, text=True
    )

    best_bssid = None
    best_signal = -100
    lines = result.stdout.strip().splitlines()

    for line in lines[1:]:  # Skip header
        try:
            # Split by 2+ spaces, which handles variable SSID width
            parts = re.split(r'\s{2,}', line.strip())
            if len(parts) != 3:
                raise ValueError(f"Unexpected number of columns: {parts}")

            ssid, bssid, signal = parts[0].strip(), parts[1].strip(), int(parts[2].strip())
            signal *=-1


            if ssid == SSID and signal > best_signal:
                best_signal = signal
                best_bssid = bssid

        except Exception as e:
            print(f"[WARN] Failed to parse line: {line} ({e})")
            continue

    return best_bssid, best_signal




def connect_to_bssid(bssid):
    print(f"[INFO] Attempting to connect to BSSID {bssid} on SSID {SSID}")
    subprocess.run([
        "nmcli", "con", "up", SSID,
        "ifname", INTERFACE,
        "ap", bssid  # lock to this BSSID
    ])


while True:
    current_bssid, current_signal = get_current_connection()
    print(f"[INFO] Connected BSSID: {current_bssid} with signal {current_signal} dBm")

    best_bssid, best_signal = get_best_ap()
    print(f"[INFO] Best AP for SSID '{SSID}': {best_bssid} with signal {best_signal} dBm")

    if current_signal is not None and best_signal is not None:
        if current_signal < SIGNAL_THRESHOLD and best_signal > current_signal:
            print(f"[ACTION] Signal below {SIGNAL_THRESHOLD} dBm. Switching to better AP...")
            connect_to_bssid(best_bssid)
        else:
            print(f"[INFO] Staying on current AP.")
    else:
        print("[WARN] Could not determine current or best AP.")

    print("-----")
    time.sleep(SCAN_INTERVAL)
